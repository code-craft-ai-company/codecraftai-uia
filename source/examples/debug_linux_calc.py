
import platform
import subprocess
import time
import sys
import os

# Add source to path so we can import ccai
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'source/packages')))

from ccai.uia.factory import AutomationFactory
from ccai.uia.platforms.linux.wrappers.uiaelement import LinuxElement

def dump_tree(element, depth=0):
    if depth > 30:
        return
    
    indent = "  " * depth
    try:
        native = getattr(element, '_native_obj', element)
        role = element.role_name
        name = native.name
        description = native.description
        text = element.text
        
        # Enhanced text inspection
        extra_debug = []
        if role == "text" or True: # Check all for now
            try:
                text_iface = native.queryText()
                raw_text = text_iface.getText(0, -1)
                if raw_text:
                    extra_debug.append(f"TextIface: '{raw_text}'")
            except Exception:
                pass

            try:
                val_iface = native.queryValue()
                val = val_iface.currentValue
                extra_debug.append(f"ValueIface: {val}")
            except Exception:
                pass
        
        states = []
        try:
            s = native.getState()
            states = [str(st) for st in s.getStates()]
        except:
            pass

        extra_str = ", ".join(extra_debug)
        if extra_str:
            extra_str = f" [{extra_str}]"
            
        print(f"{indent}Role: {role}, Name: '{name}', Desc: '{description}', Text: '{text}' States: {len(states)}{extra_str}")
        
        if hasattr(native, 'childCount'):
            count = native.childCount
            for i in range(min(count, 50)):
                child = native.getChildAtIndex(i)
                dump_tree(LinuxElement(child, element._access_agent, element._wm_agent), depth + 1)
    except Exception as e:
        print(f"{indent}Error accessing element: {e}")

def _find_input_element(element, depth=0):
    if depth > 10:
        return None

    try:
        role_name = element.role_name.lower()
        if role_name in {"entry", "text", "text entry", "editable text"}:
            return element

        native = getattr(element, '_native_obj', element)
        if hasattr(native, 'childCount'):
            count = native.childCount
            for i in range(min(count, 50)):
                child = native.getChildAtIndex(i)
                found = _find_input_element(LinuxElement(child, element._access_agent, element._wm_agent), depth + 1)
                if found is not None:
                    return found
    except Exception:
        pass

    return None

def find_button(element, name):
    try:
        if element.role_name == "push button" and getattr(element, '_native_obj', element).name == name:
            return element
        
        native = getattr(element, '_native_obj', element)
        if hasattr(native, 'childCount'):
            count = native.childCount
            for i in range(min(count, 50)):
                child = native.getChildAtIndex(i)
                found = find_button(LinuxElement(child, element._access_agent, element._wm_agent), name)
                if found:
                    return found
    except:
        pass
    return None

def debug():
    if platform.system() != "Linux":
        print("Not Linux")
        return

    try:
        proc = subprocess.Popen(["gnome-calculator"])
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
        except Exception:
            pass
        time.sleep(1.0)

        # Full sequence: 12+34=
        sequence = "12+34="
        print(f"Clicking sequence: {sequence}")
        
        for char in sequence:
            btn = find_button(main_window, char)
            if btn:
                print(f"Clicking '{char}'")
                btn.click()
                time.sleep(0.5)
            else:
                print(f"Button '{char}' not found")

        print("--- Tree after full sequence ---")
        dump_tree(main_window)
        print("-------------------------------")

    finally:
        proc.terminate()

if __name__ == "__main__":
    debug()
