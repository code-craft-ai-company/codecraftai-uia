
import platform
import subprocess
import time

from automojo import testbase
from automojo.uia.factory import AutomationFactory
from automojo.uia.platforms.linux.wrappers.uiaelement import LinuxElement


def _try_import_pyatspi() -> bool:
    try:
        import pyatspi  # noqa: F401
        return True
    except Exception:
        return False


def _find_result_deep(element: LinuxElement, target: str, depth: int = 0) -> bool:
    if depth > 30:
        return False

    try:
        native = getattr(element, '_native_obj', element)

        # Check text interface
        if hasattr(native, 'queryText'):
            try:
                text_iface = native.queryText()
                content = text_iface.getText(0, -1)
                if target in content:
                    return True
            except Exception:
                pass

        # Check name
        if native.name == target:
            return True
            
        # Recursive check
        if hasattr(native, 'childCount'):
            count = native.childCount
            for i in range(min(count, 50)):
                child = native.getChildAtIndex(i)
                if _find_result_deep(LinuxElement(child, element._access_agent, element._wm_agent), target, depth + 1):
                    return True
    except Exception:
        pass

    return False


def test_linux_calc_send_keys():
    """
        Verifies keyboard input by typing "12*3=" into gnome-calculator and checking for "36".
    """
    if platform.system() != "Linux":
        return

    testbase.assert_equal(_try_import_pyatspi(), True)

    try:
        import os
        env = os.environ.copy()
        env['GDK_BACKEND'] = 'x11'
        proc = subprocess.Popen(["gnome-calculator"], env=env)
    except FileNotFoundError:
        testbase.assert_equal(True, False)

    try:
        time.sleep(2.0)
        testbase.assert_equal(proc.poll() is None, True)

        automation = AutomationFactory.get_automation_engine()
        time.sleep(2.0)

        app = automation.get_application_by_name("gnome-calculator")
        if not app:
            app = automation.get_application_by_name("Calculator")

        testbase.assert_equal(app is not None, True)

        windows = app.get_windows()
        testbase.assert_equal(len(windows) > 0, True)

        main_window = windows[0]
        
        # Ensure focus
        try:
            main_window.activate()
        except Exception:
            pass
        
        # Additional wait for focus settling
        time.sleep(1.0)
        
        # Attempt to grab focus explicitly on the window wrapper
        try:
            main_window.grab_focus()
        except: 
            pass
        time.sleep(0.5)

        # Helper to find the display element (role: text, parent role: scroll pane usually)
        display_element = None
        def find_display(element, depth=0):
            if depth > 30: return None
            
            # The debug output showed a 'text' role with some content
            if element.role_name == "text" or element.role_name == "entry":
                return element
                
            try:
                native = getattr(element, '_native_obj', element)
                if hasattr(native, 'childCount'):
                    for i in range(native.childCount):
                        found = find_display(LinuxElement(native.getChildAtIndex(i), element._access_agent, element._wm_agent), depth + 1)
                        if found: return found
            except:
                pass
            return None

        # High-level API usage
        # High-level API usage
        print("Activating main window...")
        main_window.activate()
        time.sleep(1.0)
        
        print("Finding display element to ensure focus...")
        # Note: 'text' role is generic, but usually works for calculator display
        display = main_window.find_descendant(role="text")
        
        if display:
             print(f"Found display: {display}")
             print("Clicking display to ensure widget focus...")
             try:
                 display.click()
                 time.sleep(0.5)
             except Exception as e:
                 print(f"Click failed: {e}")
                 
             print("Typing '12*3=' into display...")
             display.type_keys("12*3=")
        else:
             print("Display not found via find_descendant! Falling back to window typing...")
             main_window.type_keys("12*3=")

        time.sleep(1.0)

        found_result = False
        # Increased check time slightly as typing takes time
        for _ in range(10):
            # Check for "36"
            if _find_result_deep(main_window, "36", depth=0):
                found_result = True
                break
            time.sleep(1.0)
            
        if not found_result:
             # Debugging: check if we see "12" or "3" or anything
             print("Did not find 36. Checking what IS there...")
             _find_result_deep(main_window, "NON_EXISTENT_JUST_TO_RECURSE", depth=0) # Logic doesn't print, but we rely on failure dump below

        testbase.assert_equal(found_result, True)
    except Exception as e:
        with open("/tmp/calc_debug.log", "w") as f:
            f.write(f"Test failed with exception: {e}\n")
            f.write("Dumping UI tree after failure:\n")
            
            def dump(el, indent=""):
                try:
                    line = f"{indent}{el.role_name}: '{el.name}'"
                    native = getattr(el, '_native_obj', el)
                    if hasattr(native, 'text') and native.text:
                         line += f" Text: '{native.text}'"
                    if hasattr(native, 'queryText'):
                        try:
                            line += f" queryText: '{native.queryText().getText(0, -1)}'"
                        except: pass
                    f.write(line + "\n")
                    
                    if hasattr(native, 'childCount'):
                        for i in range(native.childCount):
                            dump(LinuxElement(native.getChildAtIndex(i), el._access_agent, el._wm_agent), indent + "  ")
                except: pass
            
            if 'main_window' in locals():
                dump(main_window)
        raise
    finally:
        proc.terminate()

    return
