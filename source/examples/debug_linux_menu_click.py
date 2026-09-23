
import time
import sys
import os

# Add source to path for direct execution if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from ccai.uia.factory import AutomationFactory
from ccai.uia.platforms.linux.mappings.libreoffice_calc import LibreOfficeCalc

def debug_menu_click():
    print("Initializing Automation Engine...")
    automation = AutomationFactory.get_automation_engine()
    
    print("Attaching to LibreOffice Calc (assuming it is running)...")
    # We use launch_or_attach but since it's running it should just attach/find
    app = LibreOfficeCalc.launch_or_attach(automation)
    
    print("Resolving Main Window...")
    main_window = LibreOfficeCalc.MainWindow.resolve(app)
    
    if not main_window:
        print("Main window not found! Is LibreOffice Calc running?")
        return

    print(f"Found Main Window: '{main_window.name}'")
    main_window.activate()
    time.sleep(1)

    print("Resolving File Menu...")
    # Using the standardized mapping which usually maps to a Menu role
    file_menu_element = LibreOfficeCalc.MenuBar.File.resolve(main_window)
    
    if not file_menu_element:
        print("File menu element not found via hint. Trying direct search...")
        # Fallback search if hint fails
        file_menu_element = main_window.find_element(name="File", role="menu")

    if file_menu_element:
        print(f"Found File Menu Element: {file_menu_element}")
        print(f"  Role: {file_menu_element.role_name}")
        
        # Check bounds
        bounds = file_menu_element.bounds
        print(f"  Bounds: {bounds}")
        x, y, w, h = bounds
        
        if x < 0 or y < 0:
             print("  WARNING: Bounds seem invalid (negative). Element might be off-screen or virtual.")
        
        # Cast/Wrap as LinuxDropDownMenu for debugging purposes if not already
        # (Though mapped element is likely LinuxElement or LinuxMenu)
        
        print("Attempting Mouse Move + Access Click on File Menu...")
        try:
            # Calculate center
            x, y, w, h = bounds
            cx = x + w // 2
            cy = y + h // 2
            
            # Move mouse
            if file_menu_element.wm_agent:
                print(f"  Moving mouse to {cx}, {cy}...")
                # We need to cast / access the specific agent method if generic interface doesn't have it
                # But python is dynamic, so if it exists it works.
                # The wrapper exposes .wm_agent which is the X11WindowManagerAgent instance.
                file_menu_element.wm_agent.move_mouse(cx, cy)
                time.sleep(0.5) # Wait for hover
            else:
                print("  WARNING: No WM Agent available for mouse move!")

            # Introspect actions
            access = file_menu_element.access_agent
            native = file_menu_element.native_obj
            
            try:
                action_iface = native.queryAction()
                n = action_iface.nActions
                print(f"  Available Actions: {n}")
                for i in range(n):
                    print(f"    Action {i}: {action_iface.getName(i)} - {action_iface.getDescription(i)}")
            except Exception as e:
                print(f"  Could not querying actions: {e}")

            # Try direct action invocation via agent
            print("  Invoking 'do_action(0)' via agent...")
            result = access.do_action(native, 0)
            print(f"  do_action returned: {result}")
            
        except Exception as e:
            print(f"Click failed with exception: {e}")

        print("Waiting 2 seconds to observe result...")
        time.sleep(2)
        
        # Optional: Check if a child "Save As..." is now visible/bound
        print("Checking if 'Save As...' is visible...")
        save_as = file_menu_element.find_element(name="Save As...", role="menu item")
        if not save_as:
             save_as = file_menu_element.find_element(name="Save As", role="menu item")
             
        if save_as:
            sb = save_as.bounds
            print(f"  'Save As' found. Bounds: {sb}")
            if sb[0] > 0:
                print("  SUCCESS: 'Save As' has valid bounds. Menu is likely OPEN.")
            else:
                print("  FAILURE: 'Save As' has invalid bounds. Menu is likely CLOSED/INVISIBLE.")
        else:
            print("  FAILURE: 'Save As' element not found in accessibility tree.")

    else:
        print("File Menu object could not be found.")

if __name__ == "__main__":
    debug_menu_click()
