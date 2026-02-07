
import time
import subprocess
import sys
import os

# Add source/packages to path to find automojo
sys.path.append(os.path.abspath("source/packages"))

from automojo.uia.factory import AutomationFactory

def recursive_print(element, depth=0, max_depth=20):
    if depth > max_depth:
        return
    
    indent = "  " * depth
    try:
        import pyatspi
        # Access native object
        native = getattr(element, '_native_obj', element)
        
        name = native.name
        try:
            role = native.getRoleName()
        except:
            role = str(native.getRole())
            
        # Try to get text if possible
        text = ""
        try:
             # Check for text interface or value interface
             if hasattr(native, 'queryText'):
                 t = native.queryText()
                 content = t.getText(0, -1)
                 if content.strip():
                    text = f" Text='{content}'"
        except:
            pass

        print(f"{indent}- {name} (Role: {role}){text}")
        
        if hasattr(native, 'childCount'):
            count = native.childCount
            for i in range(min(count, 50)): # Limit 
                child = native.getChildAtIndex(i)
                recursive_print(child, depth + 1, max_depth)
    except Exception as e:
        print(f"{indent}Error accessing element: {e}")

def verify_calculator():
    print("Launching gnome-calculator...")
    # Launch calculator in background
    proc = subprocess.Popen(["gnome-calculator"])
    time.sleep(2) # Wait for it to show up

    try:
        print("Initializing Automation Engine...")
        automation = AutomationFactory.get_automation_engine()
        
        # Give it a moment to appear
        time.sleep(2.0)

        print("Searching for Calculator application...")
        # Try both 'gnome-calculator' and 'Calculator'
        app = automation.get_application_by_name("gnome-calculator")
        if not app:
             app = automation.get_application_by_name("Calculator")

        if app:
            print(f"Found App: {app}")
            
            # Get main window
            windows = app.get_windows()
            if windows:
                main_window = windows[0]
                print(f"  Main Window: {main_window.title}")
                
                # Activate window
                try:
                    main_window.activate()
                except:
                    pass
                time.sleep(1.0)
                
                # Type keys: 12+34=
                # This tests:
                # 1. digits (1, 2, 3, 4)
                # 2. shift/special chars (+)
                # 3. action keys (=)
                print("  Typing '12+34='...")
                main_window.type_keys("12+34=")
                time.sleep(0.5)
                # Send Return just in case = didn't trigger
                # main_window.type_keys("\n") 
                
                # Wait for calculation
                time.sleep(1.0)
                
                # Verify result "46"
                print("  Verifying result '46'...")
                
                found_result = False
                
                # Deep search helper
                def find_result_deep(element, target="46", depth=0):
                    if depth > 10: return False
                    
                    try:
                        native = getattr(element, '_native_obj', element)
                        
                        # Check Name
                        if native.name == target:
                            print(f"    Found in Name: {native.name} ({native.getRoleName()})")
                            return True
                            
                        # Check Text
                        if hasattr(native, 'queryText'):
                             try:
                                 t = native.queryText()
                                 content = t.getText(0, -1)
                                 # print(f"    Checking Text: '{content}'")
                                 if target in content:
                                     print(f"    Found in Text: '{content}' ({native.getRoleName()})")
                                     return True
                             except:
                                 pass
                        
                        # Recurse
                        if hasattr(native, 'childCount'):
                            count = native.childCount
                            for i in range(min(count, 50)):
                                child = native.getChildAtIndex(i)
                                from automojo.uia.platforms.linux.wrappers.uiaelement import LinuxElement
                                if find_result_deep(LinuxElement(child), target, depth + 1):
                                    return True
                    except:
                        pass
                    return False

                # Retry loop
                for i in range(3):
                    if find_result_deep(main_window, "46"):
                        print("  SUCCESS: Found result '46' in UI.")
                        found_result = True
                        break
                    print(f"  Retry {i+1}...")
                    time.sleep(1.0)

                if not found_result:
                    print("  WARNING: Could not find '46' in UI. Dumping UI tree with text:")
                    recursive_print(main_window)

            else:
                print("  No windows found.")
        else:
            print("Calculator application not found via automation.")
            
    except Exception as e:
        print(f"Verification Failed: {e}")
    finally:
        print("Terminating gnome-calculator...")
        proc.terminate()

if __name__ == "__main__":
    verify_calculator()
