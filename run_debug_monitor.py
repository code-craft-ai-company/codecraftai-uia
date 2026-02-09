import sys
import os
import time
import json

# Ensure source is in path
sys.path.append(os.path.abspath("source/packages"))

from automojo.uia.factory import AutomationFactory
from automojo.uia.platforms.linux.wrappers.uiaelement import LinuxElement

def walk_element(element, depth=0, max_depth=10):
    if depth > max_depth:
        return "<max_depth_reached>"
        
    data = {
        "name": getattr(element, 'name', ''),
        "role": getattr(element, 'role_name', ''),
        "states": [],
        "children": []
    }
    
    try:
        # Get states
        if hasattr(element, 'access_agent'):
             states_enum = element.access_agent.get_states(element.native_obj)
             data["states"] = [str(s).split('.')[-1] for s in states_enum]
    except: pass
    
    try:
        # Get children
        if hasattr(element, 'access_agent'):
            native = getattr(element, '_native_obj', element.native_obj)
            children = element.access_agent.get_children(native)
            for child in children:
                child_el = LinuxElement(child, element.access_agent, element.wm_agent)
                data["children"].append(walk_element(child_el, depth + 1, max_depth))
    except: pass
    
    return data

def main():
    print("Running Optimized Monitor...")
    automation = AutomationFactory.get_automation_engine()
    
    # Attach
    app = automation.get_application_by_name("soffice")
    if not app:
        app = automation.get_application_by_name("LibreOffice")
    
    if not app:
        print("Could not find running LibreOffice.")
        return

    print(f"Attached to: {app.name}")
    
    # Get Windows
    windows = app.get_windows()
    print(f"Found {len(windows)} top-level windows.")
    
    target_windows = []
    for w in windows:
        title = w.name
        print(f"Window: {title}")
        # Filter for Save As or Confirm
        if "Save" in title or "Confirm" in title or "Question" in title or "Exist" in title or "Error" in title:
             target_windows.append(w)
        # Also check main window just in case
        if "Calc" in title:
             # Maybe the dialog is a child of main window?
             # Let's check children of main window that are dialogs
             pass

    # Also check children of app that are not in get_windows() (e.g. alerts)
    try:
        children = app.access_agent.get_children(app.native_obj)
        for child in children:
             role = app.access_agent.get_role_name(child)
             name = app.access_agent.get_name(child)
             if role == "dialog" or role == "alert":
                 if "Save" in name or "Confirm" in name or "Question" in name or "Exist" in name:
                      w = LinuxElement(child, app.access_agent, app.wm_agent)
                      target_windows.append(w)
    except: pass

    if not target_windows:
        print("No target dialogs found! Dumping all windows shallowly...")
        target_windows = windows

    dump_data = []
    for w in target_windows:
        print(f"Dumping window: {w.name}")
        dump_data.append(walk_element(w, max_depth=6))
        
    print(json.dumps(dump_data, indent=2))

if __name__ == "__main__":
    main()
