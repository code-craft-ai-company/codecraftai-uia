from automojo.arcli.model.command import Command
from automojo.arcli.model.fields.argfield import ArgField
from automojo.arcli.model.fields.optionfield import OptionField
from automojo.arcli.model.parameters.stringparameter import StringParameter
from automojo.uia.factory import AutomationFactory
from automojo.uia.platforms.linux.wrappers.uiaelement import LinuxElement
from automojo.uia.platforms.macos.wrappers.uiaaccessibility import UiaAccessibilityElement
import subprocess
import time
import os
import json
import yaml
import sys

class MonitorCommand(Command):

    def __init__(self):
        super().__init__("monitor", self.execute)
        self.add_argument(ArgField("app_command", ptype=StringParameter, help="The application command to run and monitor"))
        self.add_option(OptionField("--hint", alias="hint", ptype=StringParameter, required=True, help="Processing hint to find the application (e.g. name)"))
        self.add_option(OptionField("--format", alias="format", ptype=StringParameter, default="json", help="Output format: json or yaml"))

    def execute(self, context, app_command, hint, format):
        automation = AutomationFactory.get_automation_engine()
        app = None
        we_launched_it = False
        
        # 1. Try to find existing application
        print(f"Searching for application with hint: '{hint}'...", file=sys.stderr)
        app = automation.get_application_by_name(hint)
        
        if not app:
            # 2. Launch if not found
            print(f"Application not found. Launching: {app_command}", file=sys.stderr)
            proc = subprocess.Popen(app_command, shell=True)
            we_launched_it = True
            
            # Wait for it to appear
            for i in range(20):
                time.sleep(1)
                app = automation.get_application_by_name(hint)
                if app:
                    break
        else:
             print("Found running application.", file=sys.stderr)

        if not app:
            print("Error: Could not find application even after launch.", file=sys.stderr)
            if we_launched_it:
                 proc.kill()
            return

        print(f"Attached to app: {app.name}", file=sys.stderr)
        
        try:
            # 3. Walk Tree
            # We need the main window usually
            # But let's dump from the App root if possible, or iterate windows
            print("Walking UI tree...", file=sys.stderr)
            
            tree_data = {
                "application": app.name,
                "windows": []
            }
            
            # Wait for windows
            windows = []
            for i in range(5):
                windows = app.get_windows()
                if windows: break
                time.sleep(1)

            for window in windows:
                win_data = self._walk_element(window)
                tree_data["windows"].append(win_data)
            
            # 4. Dump Output
            if format.lower() == "yaml":
                print(yaml.dump(tree_data, sort_keys=False))
            else:
                print(json.dumps(tree_data, indent=2))
                
        finally:
            # 5. Cleanup
            if we_launched_it:
                print("Closing application...", file=sys.stderr)
                # Try graceful close first? 
                # For now, just terminate the process we started if possible
                # Because we used shell=True, proc.terminate() kills the sh, not the app usually
                # But let's try.
                try:
                    proc.terminate()
                    # Also try to close the app via UI automation if possible
                    # app.close() # Not standard API yet?
                except:
                    pass
            else:
                print("Detaching from application (leaving it running).", file=sys.stderr)

    def _walk_element(self, element, depth=0):
        # Unwrap if we were handed a platform wrapper with a native object
        native_obj = getattr(element, "native_obj", None)
        if native_obj is not None:
            if isinstance(native_obj, UiaAccessibilityElement):
                element = native_obj

        # Basic attributes
        data = {
            "name": getattr(element, "name", ""),
            "role": getattr(element, "role_name", getattr(element, "role", "")),
            "description": getattr(element, 'description', ''),
            "states": [],
            "bounds": getattr(element, "bounds", (0, 0, 0, 0)),
            "interfaces": [],
            "children": []
        }
        
        # Get states
        try:
            if isinstance(element, LinuxElement):
                 states_enum = element.access_agent.get_states(element.native_obj)
                 data["states"] = [str(s).split('.')[-1] for s in states_enum]
        except:
            pass

        # Get interfaces/attributes
        try:
            if isinstance(element, LinuxElement):
                native = getattr(element, '_native_obj', element) if hasattr(element, '_native_obj') else element.native_obj
                # PyAtspi specific: list interfaces
                start_interfaces = pyatspi.listInterfaces(native) if 'pyatspi' in sys.modules else []
                # If we can't get them easily via wrapper, maybe just try to query common ones or skip
                # Actually, capturing interfaces is hard without direct pyatspi access in this context if not imported
                # Let's try to get description via access_agent if possible
                pass
        except:
            pass
            
        # Helper to recurse
        try:
            if isinstance(element, LinuxElement):
                native = getattr(element, '_native_obj', element) if hasattr(element, '_native_obj') else element.native_obj
                children = element.access_agent.get_children(native)
                for child in children:
                    child_el = LinuxElement(child, element.access_agent, element.wm_agent)
                    data["children"].append(self._walk_element(child_el, depth + 1))
            elif isinstance(element, UiaAccessibilityElement):
                children = element.children()
                for child in children:
                    data["children"].append(self._walk_element(child, depth + 1))
            else:
                if hasattr(element, "children"):
                    children = element.children()
                    for child in children:
                        data["children"].append(self._walk_element(child, depth + 1))
        except:
            pass
             
        return data
