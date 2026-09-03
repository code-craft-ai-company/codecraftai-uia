
import platform
import subprocess
import time
import sys
import os

# Add source to path so we can import ccai
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../source/packages')))

from ccai.uia.factory import AutomationFactory
from ccai.uia.platforms.linux.wrappers.uiaelement import LinuxElement

def dump_value(main_window):
    try:
        # Find the result display
        display = None
        
        # Helper to find display
        def find_display(element, depth=0):
            if depth > 30: return None
            if element.role_name == "text":
                return element
            
            native = getattr(element, '_native_obj', element)
            if hasattr(native, 'childCount'):
                for i in range(native.childCount):
                    child = native.getChildAtIndex(i)
                    found = find_display(LinuxElement(child, main_window._access_agent, main_window._wm_agent), depth + 1)
                    if found: return found
            return None

        display = find_display(main_window)
        if display:
            native = getattr(display, '_native_obj', display)
            try:
                text = native.queryText().getText(0, -1)
                print(f"Current Display Text: '{text}'")
            except Exception:
                print("Could not get text from display")
    except Exception as e:
        print(f"Error dumping value: {e}")


def debug_keys():
    if platform.system() != "Linux":
        print("Not Linux")
        return

    try:
        env = os.environ.copy()
        env['GDK_BACKEND'] = 'x11'
        proc = subprocess.Popen(["gnome-calculator"], env=env)
    except FileNotFoundError:
        print("gnome-calculator not found")
        return

    try:
        time.sleep(2.0)
        
        automation = AutomationFactory.get_automation_engine()
        app = automation.get_application_by_name("gnome-calculator") or automation.get_application_by_name("Calculator")
        
        if not app:
            print("App not found")
            return

        windows = app.get_windows()
        if not windows:
            print("No windows found")
            return

        main_window = windows[0]
        try:
            main_window.activate()
            print("Activated main window")
        except Exception as e:
            print(f"Failed to activate window: {e}")
            
        time.sleep(1.0)
        
        # Strategy: Find display text, CLICK IT to focus, then type
        display = None
        def find_display(element, depth=0):
            if depth > 30: return None
            if element.role_name == "text" or element.role_name == "entry":
                return element
            
            native = getattr(element, '_native_obj', element)
            if hasattr(native, 'childCount'):
                for i in range(native.childCount):
                    child = native.getChildAtIndex(i)
                    found = find_display(LinuxElement(child, element._access_agent, element._wm_agent), depth + 1)
                    if found: return found
            return None

        display = find_display(main_window)
        if display:
             print(f"Clicking display element (Assume it grabs focus)...")
             try:
                 display.click() # Using our wrapper click which tries Action interface
             except Exception:
                 # Try raw component click if wrapper fails
                 try:
                     native = getattr(display, '_native_obj', display)
                     comp = native.queryComponent()
                     # grab focus directly on component too
                     comp.grabFocus()
                     print("Grabbed focus on display component")
                 except Exception as e:
                     print(f"Failed to focus display: {e}")
        else:
             print("Display element not found to click")
        
        time.sleep(0.5)



        keys = "12*3="
        print(f"Attempting to type '{keys}' via python-xlib XTest (with X11 focus force)...")
        
        try:
            from Xlib import X, display, XK
            from Xlib.ext import xtest
            
            d = display.Display(os.environ.get('DISPLAY', ':0'))
            
            # Find the calculator window purely via X11 logic to be sure
            root = d.screen().root
            target_win = None
            
            def find_calc_window(win):
                try:
                    # Some windows might not have names or return bytes
                    name = win.get_wm_name()
                    if name:
                        if isinstance(name, bytes):
                             name = name.decode('utf-8', 'ignore')
                        print(f"Checking window: {hex(win.id)} - {name}")
                        if "Calculator" in name or "gnome-calculator" in name:
                            return win
                    
                    # Query tree can fail on some windows
                    try:
                        children = win.query_tree().children
                    except Exception:
                        return None
                        
                    for child in children:
                        res = find_calc_window(child)
                        if res: return res
                except Exception as e:
                    # print(f"Error checking window: {e}")
                    pass
                return None

            # Attempt to find it
            target_win = find_calc_window(root)
            if target_win:
                print(f"Found X11 window: {target_win.id} - {target_win.get_wm_name()}")
                target_win.set_input_focus(X.RevertToParent, X.CurrentTime)
                d.sync()
                print("Forced X11 input focus to calculator window")
                time.sleep(0.5)
                
                curr_focus = d.get_input_focus().focus
                print(f"Current X11 Focus: {curr_focus.id if hasattr(curr_focus, 'id') else curr_focus}")
            else:
                print("Could not find calculator window via X11 traversal")

            for char in keys:
                keysym = None
                if char == '*': keysym = XK.string_to_keysym("asterisk")
                elif char == '=': keysym = XK.string_to_keysym("equal")
                else: keysym = XK.string_to_keysym(char)

                keycode = d.keysym_to_keycode(keysym)
                
                xtest.fake_input(d, X.KeyPress, keycode)
                xtest.fake_input(d, X.KeyRelease, keycode)
                d.sync()
                
                print(f"Sent XTest event for '{char}'")
                time.sleep(0.2)
                
        except Exception as e:
            print(f"python-xlib XTest failed: {e}")

        time.sleep(1.0)
        dump_value(main_window)

    finally:
        proc.terminate()


if __name__ == "__main__":
    debug_keys()
