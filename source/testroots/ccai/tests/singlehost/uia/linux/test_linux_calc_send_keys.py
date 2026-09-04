
import platform
import subprocess
import time

from ccai import testbase
from ccai.tests.singlehost.uia.linux._desktop import (
    launch_or_skip, require_automation_engine, require_display, require_pyatspi,
)
from ccai.uia.factory import AutomationFactory
from ccai.uia.platforms.linux.wrappers.uiaelement import LinuxElement


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

    require_pyatspi()
    require_display()

    import os
    env = os.environ.copy()
    env['GDK_BACKEND'] = 'x11'
    proc = launch_or_skip(["gnome-calculator"], env=env)

    try:
        time.sleep(2.0)
        testbase.assert_equal(proc.poll() is None, True)

        automation = require_automation_engine()
        time.sleep(2.0)

        # Declarative Usage
        from ccai.uia.platforms.linux.mappings.calculator import Calculator
        
        # 1. Attach/Launch
        # Note: launch_or_attach implementation in DeclarativeApplication might be stubbed, 
        # but we can implement/verify it or just use the hint manually if needed.
        # For now, let's try using the class method if available or simulate it.
        # Actually, let's use the standard factory but try to resolve the app via the class
        
        # automation is already gotten
        # app = Calculator.attach(automation) 
        # logic in DeclarativeApplication.attach is:
        # return automation_engine.get_application_by_name(cls.APPLICATION_NAME)
        
        # On a freshly started display the accessibility registry can take several
        # seconds to expose the application, so poll for it rather than looking once.
        app = None
        for _ in range(30):
            app = Calculator.attach(automation)
            if not app:
                # Fallback if name mismatch or timing
                app = automation.get_application_by_name("Calculator")
            if app:
                break
            time.sleep(1.0)

        testbase.assert_equal(app is not None, True, "Could not attach to the calculator application")

        # The window can lag the application registration by a few seconds on a
        # freshly started display, so poll for it before falling back to the mapping.
        main_window = None
        for _ in range(20):
            windows = app.get_windows()
            if windows:
                main_window = windows[0]
                break
            time.sleep(0.5)
        if main_window is None:
            main_window = Calculator.MainWindow.resolve(app)
        testbase.assert_equal(main_window is not None, True, "Could not find the calculator window")

        # On a cold desktop session the accessibility tree under a freshly launched
        # window can stay empty for a while, so wait for it to populate before typing.
        for _ in range(30):
            native = getattr(main_window, "_native_obj", None)
            if native is not None and getattr(native, "childCount", 0) > 0:
                break
            time.sleep(1.0)
        
        # Ensure focus
        try:
            main_window.activate()
        except Exception:
            pass
        time.sleep(1.0)
        
        # 3. Resolve Display Element
        # Using the hint from the mapping
        print("Resolving Display element using Declarative Mapping...")
        display = Calculator.Display.resolve(main_window)
        if not display:
            display = Calculator.DisplayEntry.resolve(main_window)
        if not display:
             display = Calculator.DisplayEdit.resolve(main_window)

        time.sleep(1.0)
        
        # Clear specific logic
        print("Clearing calculator...")
        clear_btn = Calculator.ButtonClear.resolve(main_window)
        if clear_btn:
            try:
                clear_btn.click()
                time.sleep(0.5)
            except Exception as e:
                print(f"Clear click failed: {e}")
        else:
             print("Warning: Clear button not found")

        if display:
             print(f"Found display: {display}")
             print("Clicking display to ensure widget focus...")
             try:
                 display.click()
                 time.sleep(0.5)
             except Exception as e:
                 # print(f"Click failed: {e}")
                 pass
                 
             print("Typing '12*3=' into display...")
             display.type_keys("12*3=")
        else:
             print("Display not found via mapping! Falling back to window typing...")
             main_window.type_keys("12*3=")

        time.sleep(1.0)

        found_result = False
        # Increased check time slightly as typing takes time
        for _ in range(10):
            # The display exposes its value through the element text property; the
            # deep search over names and text interfaces is kept as a fallback.
            if display:
                try:
                    if "36" in str(display.text):
                        found_result = True
                        break
                except Exception:
                    pass
            if _find_result_deep(main_window, "36", depth=0):
                found_result = True
                break
            time.sleep(1.0)
            
        if not found_result:
             # Debugging: check if we see "12" or "3" or anything
             print("Did not find 36. Checking what IS there...")
             if display:
                 try:
                     print(f"Display text after typing: {display.text!r}")
                 except Exception as e:
                     print(f"Display text unavailable: {e}")
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
                        except Exception: pass
                    f.write(line + "\n")
                    
                    if hasattr(native, 'childCount'):
                        for i in range(native.childCount):
                            dump(LinuxElement(native.getChildAtIndex(i), el.access_agent, el.wm_agent), indent + "  ")
                except Exception: pass
            
            if 'main_window' in locals():
                dump(main_window)
        raise
    finally:
        proc.terminate()

    return
