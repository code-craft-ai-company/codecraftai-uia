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
        self.add_option(OptionField("--output", alias="output", ptype=StringParameter, required=False, help="Optional file path to write results to"))

    def execute(self, context, app_command, hint, format, output):
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
                "windows": [],
                "menu_bar": None
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

            try:
                menu_bar = app.find_first_by_role("AXMenuBar")
            except Exception:
                menu_bar = None

            if menu_bar is not None:
                tree_data["menu_bar"] = self._walk_element(menu_bar)
            
            # 4. Dump Output
            if format.lower() == "yaml":
                output_text = yaml.dump(tree_data, sort_keys=False)
            else:
                output_text = json.dumps(tree_data, indent=2)

            if output:
                output_dir = os.path.dirname(output)
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                with open(output, "w", encoding="utf-8") as outfile:
                    outfile.write(output_text)
                print(f"Wrote mapping output to: {output}", file=sys.stderr)
            else:
                print(output_text)
                
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

        title = ""
        value = None
        role = ""
        description = ""
        bounds = (0, 0, 0, 0)

        try:
            title = getattr(element, "title", "") or ""
        except Exception:
            title = ""

        try:
            role = getattr(element, "role_name", getattr(element, "role", "")) or ""
        except Exception:
            role = ""

        try:
            description = getattr(element, "description", "") or ""
        except Exception:
            description = ""

        try:
            bounds = getattr(element, "bounds", (0, 0, 0, 0)) or (0, 0, 0, 0)
        except Exception:
            bounds = (0, 0, 0, 0)

        try:
            if isinstance(element, UiaAccessibilityElement):
                value = element._get_value_text()
        except Exception:
            value = None

        if value is None:
            try:
                value = getattr(element, "text", None)
            except Exception:
                value = None

        if value is None:
            try:
                value = getattr(element, "value", None)
            except Exception:
                value = None

        # Basic attributes
        identifier = ""
        help_text = ""
        try:
            identifier = getattr(element, "identifier", "") or ""
        except Exception:
            identifier = ""

        try:
            help_text = getattr(element, "help", "") or ""
        except Exception:
            help_text = ""

        data = {
            "name": getattr(element, "name", "") if hasattr(element, "name") else title,
            "title": title,
            "identifier": identifier,
            "help": help_text,
            "value": value,
            "role": role,
            "description": description,
            "states": [],
            "bounds": list(bounds) if isinstance(bounds, tuple) else bounds,
            "interfaces": [],
            "children": []
        }
        
        # Get states
        try:
            if isinstance(element, LinuxElement):
                 states_enum = element.access_agent.get_states(element.native_obj)
                 data["states"] = [str(s).split('.')[-1] for s in states_enum]
        except Exception:
            pass

        # Get interfaces/attributes
        try:
            if isinstance(element, LinuxElement):
                native = getattr(element, '_native_obj', element) if hasattr(element, '_native_obj') else element.native_obj
                # PyAtspi specific: list interfaces
                if 'pyatspi' in sys.modules:
                    pyatspi_module = sys.modules['pyatspi']
                    start_interfaces = pyatspi_module.listInterfaces(native)
                else:
                    start_interfaces = []
                # If we can't get them easily via wrapper, maybe just try to query common ones or skip
                # Actually, capturing interfaces is hard without direct pyatspi access in this context if not imported
                # Let's try to get description via access_agent if possible
                pass
        except Exception:
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
        except Exception:
            pass
             
        return data
