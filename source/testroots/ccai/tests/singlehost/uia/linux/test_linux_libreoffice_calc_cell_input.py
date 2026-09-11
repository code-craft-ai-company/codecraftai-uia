import platform
import shutil
import subprocess
import time

from ccai import testbase
from ccai.tests.singlehost.uia.linux._desktop import (
    launch_or_skip, require_automation_engine, require_display, require_pyatspi,
)
from ccai.errors.exceptions import SkipError
from ccai.uia.factory import AutomationFactory
from ccai.uia.platforms.linux.mappings.libreoffice_calc import LibreOfficeCalc
from ccai.uia.platforms.linux.wrappers.tableelement import TableElement


def _try_import_pyatspi() -> bool:
    try:
        import pyatspi  # noqa: F401
        return True
    except Exception:
        return False


def _handle_tip_dialog(app) -> None:
    # Use Declarative Hint
    # Optimization: Check windows first
    tip_dialog = None
    if app:
        for w in app.get_windows():
            if "Tip" in w.title:
                 # Wrap it? resolve(app) does finding.
                 # Let's try resolve(app) but maybe it's slow if it scans invalid children.
                 pass
    
    # Just try resolve but assume it might be slow if not present.
    # Actually, if we don't see it in windows, maybe skip?
    # LibreOffice Tip is usually a top-level window or dialog.
    
    # Let's use a quick check:
    windows = app.get_windows()
    for w in windows:
         if "Tip" in w.title:
             from ccai.uia.platforms.linux.wrappers.dialogelement import LinuxDialog
             tip_dialog = LinuxDialog(w.native_obj, w.access_agent, w.wm_agent)
             break

    if not tip_dialog:
         # Fast fail if not in windows? Or deep scan?
         # Deep scan causes hangs if AtSpi is flaky.
         # Let's assume if it's not in get_windows, it's not there.
         pass

    if tip_dialog:
        print("Handling Tip of the Day dialog...")
        # Try OK or Close
        ok_btn = LibreOfficeCalc.TipOfTheDay.OKButton.resolve(tip_dialog)
        if not ok_btn:
             ok_btn = LibreOfficeCalc.TipOfTheDay.CloseButton.resolve(tip_dialog)
        
        if ok_btn:
            try:
                ok_btn.click()
                time.sleep(1.0)
            except Exception:
                pass


def _set_cell_value(spreadsheet: TableElement, row: int, col: int, value: str, expected: str) -> bool:
    print(f"Setting cell ({row}, {col}) to '{value}', expecting '{expected}'")
    
    cell = spreadsheet.get_cell(row, col)
    if not cell:
        print(f"  ERROR: Could not get cell ({row}, {col})")
        return False

    try:
        # Click to focus
        cell.click()
        time.sleep(0.5)
        
        # Type value
        if value.startswith("="):
             print(f"  Typing formula: {value}")
             cell.type_keys(value + "\n")
        else:
             print(f"  Typing value: {value}")
             cell.type_keys(value + "\n")
    except Exception as e:
        print(f"  Error setting text: {e}")
        return False
    
    # Give LibreOffice time to commit the value
    time.sleep(1.0)
    
    current_text = cell.text
    print(f"  Current cell text: '{current_text}'")
    
    if expected in current_text or current_text == expected:
        print(f"  SUCCESS: Cell value matches expected")
        return True

    print(f"  FAILED: Cell text '{current_text}' doesn't match expected '{expected}'")
    return False


def test_linux_libreoffice_calc_cell_input():
    """
        Verifies LibreOffice Calc table entry using Linux UI automation.
        Refactored to use Declarative Mapping.
    """
    if platform.system() != "Linux":
        raise SkipError("the Linux desktop tests need a Linux host")

    if shutil.which("libreoffice") is None:
        raise SkipError("libreoffice is not installed on this host")

    testbase.assert_equal(_try_import_pyatspi(), True)

    import os
    env = os.environ.copy()
    env['GDK_BACKEND'] = 'x11'
    proc = launch_or_skip(["libreoffice", "--calc", "--norestore"], env=env)

    try:
        # Startup time
        time.sleep(10.0)
        testbase.assert_equal(proc.poll() is None, True)
        
        automation = AutomationFactory.get_automation_engine()

        # Declarative Attach (App)
        # Note: LibreOffice title changes, but process name is soffice/libreoffice
        # DeclarativeApplication uses a hint or name.
        # LibreOfficeCalc.APPLICATION_NAME = "soffice"
        app = LibreOfficeCalc.attach(automation)
        
        # Fallback if attach by name failed (e.g. wrapper name mismatch vs registry)
        if not app:
             # Try other names via direct engine call if generic attach fails
             app = automation.get_application_by_name("LibreOffice")
             
        testbase.assert_equal(app is not None, True, "Could not attach to LibreOffice")

        # Handle Tip
        _handle_tip_dialog(app)

        # MainWindow
        main_window = LibreOfficeCalc.MainWindow.resolve(app)
        
        # If not compliant with hint (e.g. name variations), try fallback or assume first window
        if not main_window:
             windows = app.get_windows()
             if windows:
                 main_window = windows[0]
        
        testbase.assert_equal(main_window is not None, True, "Main window not found")

        try:
            main_window.activate()
        except Exception:
            pass
        time.sleep(1.0)

        # Spreadsheet
        # Requires TableHint resolution which should auto-wrap to TableElement
        spreadsheet = LibreOfficeCalc.Spreadsheet.resolve(main_window)
        
        # Validation of type
        if spreadsheet and not isinstance(spreadsheet, TableElement):
            print(f"Warning: Resolved spreadsheet is {type(spreadsheet)}, expected TableElement. Attempting cast.")
            # If auto-wrap failed (e.g. factory issue), manual cast
            spreadsheet = TableElement(spreadsheet.native_obj, spreadsheet.access_agent, spreadsheet.wm_agent, parent=main_window)

        if not spreadsheet:
             # Fallback manual search if hint fails (e.g. recursive depth issue)
             # But we should rely on hint.
             pass

        testbase.assert_equal(spreadsheet is not None, True, "Spreadsheet table not found via Declarative Hint")

        # Test Logic
        testbase.assert_equal(_set_cell_value(spreadsheet, 0, 3, "2", "2"), True)
        testbase.assert_equal(_set_cell_value(spreadsheet, 1, 3, "5", "5"), True)
        testbase.assert_equal(_set_cell_value(spreadsheet, 2, 3, "=D1{+}D2", "7"), True)
    finally:
        proc.terminate()

    return

if __name__ == "__main__":
    test_linux_libreoffice_calc_cell_input()
