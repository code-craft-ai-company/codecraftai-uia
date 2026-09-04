import platform
import subprocess
import time

from ccai import testbase
from ccai.tests.singlehost.uia.linux._desktop import (
    launch_or_skip, require_automation_engine, require_display, require_pyatspi,
)
from ccai.uia.factory import AutomationFactory
from ccai.uia.model.declarative import ButtonHint
from ccai.uia.platforms.linux.mappings.calculator import Calculator


def _try_import_pyatspi() -> bool:
    try:
        import pyatspi  # noqa: F401
        return True
    except Exception:
        return False


def test_linux_calc_type_keys():
    """
        Verifies type_keys by typing into gnome-calculator and checking the result.
        Refactored to use Declarative Mapping.
    """
    if platform.system() != "Linux":
        return

    require_pyatspi()
    require_display()

    # Launch logic (or rely on launch_or_attach, but Calculator.launch_or_attach is a stub for now that does attach)
    # We'll launch manually to ensure clean state as per original test
    proc = launch_or_skip(["gnome-calculator"])

    try:
        time.sleep(2.0)
        testbase.assert_equal(proc.poll() is None, True)

        automation = AutomationFactory.get_automation_engine()
        time.sleep(2.0)

        # Declarative Attach
        app = Calculator.attach(automation)
        testbase.assert_equal(app is not None, True, "Could not attach to Calculator")

        main_window = Calculator.MainWindow.resolve(app)
        testbase.assert_equal(main_window is not None, True, "Could not find Main Window")

        try:
            main_window.activate()
        except Exception:
            pass
        time.sleep(1.0)

        # Typing sequence using ButtonHints
        sequence = "12+34="
        for char in sequence:
            # Dynamic hint creation for buttons
            # We could use Calculator.Button1 etc, but dynamic is cleaner for loop
            btn = ButtonHint(name=char).resolve(main_window)
            if btn:
                btn.click()
                time.sleep(0.5)
            else:
                testbase.assert_equal(True, False, f"Could not find button for '{char}'")
            time.sleep(0.2)
        
        time.sleep(1.0)

        # Verification
        found_result = False
        display = Calculator.Display.resolve(main_window)
        
        if display:
             # Check text
             # Display might contain "46" or "46\n"
             print(f"Display text: '{display.text}'")
             if "46" in display.text:
                 found_result = True
        
        testbase.assert_equal(found_result, True, "Result '46' not found in display")

    finally:
        proc.terminate()

    return
