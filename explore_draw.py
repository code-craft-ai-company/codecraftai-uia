
import time
import subprocess
import sys
import os

# Add source to path
sys.path.append(os.path.abspath("source"))

from ccai.uia.factory import AutomationFactory
from ccai.uia.platforms.linux.wrappers.uiaelement import LinuxElement

def dump_tree(element, depth=0, max_depth=5):
    if depth > max_depth:
        return
    
    indent = "  " * depth
    try:
        role = element.role_name
        name = element.name
        # Only print if relevant or if we are exploring top levels
        if depth < 3 or "Circle" in name or "Ellipse" in name or role in ["drawing area", "document frame", "scroll pane"]:
            print(f"{indent}{role}: {name}")
        
        # Check for children
        native = getattr(element, '_native_obj', element)
        if hasattr(native, 'childCount'):
            count = native.childCount
            for i in range(min(count, 50)): # Limit children to avoid huge output
                child = native.getChildAtIndex(i)
                # FIX: Use properties to get the actual objects, not the private weakrefs
                child_element = LinuxElement(child, element.access_agent, element.wm_agent)
                dump_tree(child_element, depth + 1, max_depth)
    except Exception as e:
        # print(f"{indent}Error accessing element: {e}")
        pass

def explore_draw():
    print("Launching LibreOffice Draw...")
    proc = subprocess.Popen(["libreoffice", "--draw", "--norestore"])
    
    try:
        automation = AutomationFactory.get_automation_engine()
        app = None
        
        for _ in range(10):
            time.sleep(2)
            app = automation.get_application_by_name("soffice")
            if not app:
                app = automation.get_application_by_name("Draw")
            if app:
                print(f"Found App: {app.name}")
                break
        
        if not app:
            print("Failed to find application")
            return

        time.sleep(5) # Wait for UI to fully load

        windows = app.get_windows()
        if not windows:
            print("No windows found")
            return
            
        main_window = windows[0]
        print(f"Main Window: {main_window.title}")
        
        print("\n--- Accessibility Tree Dump ---")
        dump_tree(main_window, max_depth=8)
        print("-------------------------------")

    finally:
        print("Closing application...")
        proc.terminate()

if __name__ == "__main__":
    explore_draw()
