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
    if depth > 10:
        return False

    try:
        native = getattr(element, '_native_obj', element)

        try:
            if target in element.text:
                return True
        except Exception:
            pass

        if native.name == target:
            return True

        if hasattr(native, 'queryText'):
            try:
                text_iface = native.queryText()
                content = text_iface.getText(0, -1)
                if target in content:
                    return True
            except Exception:
                pass

        if hasattr(native, 'childCount'):
            count = native.childCount
            for i in range(min(count, 50)):
                child = native.getChildAtIndex(i)
                if _find_result_deep(LinuxElement(child), target, depth + 1):
                    return True
    except Exception:
        pass

    return False


def _find_input_element(element: LinuxElement, depth: int = 0) -> LinuxElement | None:
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
                found = _find_input_element(LinuxElement(child), depth + 1)
                if found is not None:
                    return found
    except Exception:
        pass

    return None


def test_linux_calc_type_keys():
    """
        Verifies type_keys by typing into gnome-calculator and checking the result.
    """
    if platform.system() != "Linux":
        return

    testbase.assert_equal(_try_import_pyatspi(), True)

    try:
        proc = subprocess.Popen(["gnome-calculator"])
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
        try:
            main_window.activate()
        except Exception:
            pass
        time.sleep(1.0)

        input_element = _find_input_element(main_window)
        testbase.assert_equal(input_element is not None, True)

        try:
            input_element.click()
        except Exception:
            pass
        input_element.grab_focus()
        time.sleep(0.5)

        input_element.type_keys("12+34=")
        time.sleep(1.0)

        found_result = False
        for _ in range(3):
            if _find_result_deep(main_window, "46"):
                found_result = True
                break
            time.sleep(1.0)

        testbase.assert_equal(found_result, True)
    finally:
        proc.terminate()

    return
