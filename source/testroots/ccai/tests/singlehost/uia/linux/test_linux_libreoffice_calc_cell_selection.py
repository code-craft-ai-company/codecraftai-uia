
import platform
import shutil
import time

from ccai import testbase
from ccai.tests.singlehost.uia.linux._desktop import launch_or_skip
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
    # Use Declarative Hint
    # Optimization: Check windows first
    tip_dialog = None
    if app:
        windows = app.get_windows()
        for w in windows:
             if "Tip" in w.title:
                 from ccai.uia.platforms.linux.wrappers.dialogelement import LinuxDialog
                 tip_dialog = LinuxDialog(w.native_obj, w.access_agent, w.wm_agent)
                 break

    if tip_dialog:
        print("Handling Tip of the Day dialog...")
        ok_btn = LibreOfficeCalc.TipOfTheDay.OKButton.resolve(tip_dialog)
        if not ok_btn:
             ok_btn = LibreOfficeCalc.TipOfTheDay.CloseButton.resolve(tip_dialog)
        
        if ok_btn:
            try:
                ok_btn.click()
                time.sleep(1.0)
            except Exception:
                # Dismissing the optional Tip of the Day dialog is best-effort; the test continues without it.
                pass


def test_libreoffice_selection():
    """
    Verifies cell selection in LibreOffice Calc: D1, D3, D5, B2, B4.
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
        # Give it time to appear
        time.sleep(10.0)
        testbase.assert_equal(proc.poll() is None, True)

        automation = AutomationFactory.get_automation_engine()
        
        # Declarative Attach
        app = LibreOfficeCalc.attach(automation)
        if not app:
             app = automation.get_application_by_name("LibreOffice")
        
        testbase.assert_equal(app is not None, True, "Correct application not found")

        _handle_tip_dialog(app)

        # MainWindow
        main_window = LibreOfficeCalc.MainWindow.resolve(app)
        if not main_window:
             windows = app.get_windows()
             if windows:
                 main_window = windows[0]
        
        testbase.assert_equal(main_window is not None, True, "Main window not found")

        try:
            main_window.activate()
        except Exception:
            # Activation is best-effort; the cell selection below goes through the AT-SPI table interface.
            pass
        time.sleep(1.0)

        # Spreadsheet
        spreadsheet = LibreOfficeCalc.Spreadsheet.resolve(main_window)
        
        # Validation of type and manual cast if needed
        if spreadsheet and not isinstance(spreadsheet, TableElement):
             spreadsheet = TableElement(spreadsheet.native_obj, spreadsheet.access_agent, spreadsheet.wm_agent, parent=main_window)
        
        testbase.assert_equal(spreadsheet is not None, True, "Spreadsheet table not found")

        # Cells to select: D1, D3, D5, B2, B4
        targets = [
            (0, 3, "D1"),
            (2, 3, "D3"),
            (4, 3, "D5"),
            (1, 1, "B2"),
            (3, 1, "B4")
        ]

        for row, col, label in targets:
            print(f"Selecting {label} (Row {row}, Col {col})...")
            
            # Use basic selection
            spreadsheet.select_cell(row, col)
            
            time.sleep(0.5)
            
            # Validation: Check if the specific cell has 'focused' or 'selected' state
            cell = spreadsheet.get_cell(row, col)
            testbase.assert_equal(cell is not None, True, f"Could not get cell object for {label}")
            testbase.assert_equal(cell.row, row, f"Cell row mismatch for {label}")
            testbase.assert_equal(cell.column, col, f"Cell column mismatch for {label}")
            
            # Using raw pyatspi check for robustness in validation
            states = cell._native_obj.getState()
            
            import pyatspi
            
            is_focused = states.contains(pyatspi.STATE_FOCUSED)
            is_selected = states.contains(pyatspi.STATE_SELECTED)
            
            print(f"  {label} -> Focused: {is_focused}, Selected: {is_selected}")
            
            testbase.assert_equal(is_focused or is_selected, True, f"Cell {label} was not selected/focused")
            
        # Verify get_range
        print("Verifying get_range(0, 0, 0, 2) [A1:C1]...")
        range_cells = spreadsheet.get_range(0, 0, 0, 2)
        testbase.assert_equal(len(range_cells), 3, "Range count mismatch")
        testbase.assert_equal(range_cells[0].row, 0, "Range cell 0 row mismatch")
        testbase.assert_equal(range_cells[0].column, 0, "Range cell 0 col mismatch")
        testbase.assert_equal(range_cells[2].column, 2, "Range cell 2 col mismatch")
        print("Range verification passed.")

    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    test_libreoffice_selection()
