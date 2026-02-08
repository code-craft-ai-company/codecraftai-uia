
import platform
import subprocess
import time
import os

from automojo import testbase
from automojo.uia.factory import AutomationFactory
from automojo.uia.platforms.linux.wrappers.uiaelement import LinuxElement
from automojo.uia.platforms.linux.wrappers.tableelement import TableElement


def _try_import_pyatspi() -> bool:
    try:
        import pyatspi  # noqa: F401
        return True
    except Exception:
        return False


def _handle_tip_dialog(automation) -> None:
    tip_dialog = automation.get_application_by_name("Tip of the Day")
    if not tip_dialog:
        return

    ok_btn = tip_dialog.find_descendant(name="OK")
    if not ok_btn:
        ok_btn = tip_dialog.find_descendant(name="Close")

    if ok_btn:
        try:
            ok_btn.click()
            time.sleep(1.0)
        except Exception:
            pass


def _find_all_tables(element: LinuxElement, tables: list, depth: int = 0) -> None:
    if depth > 15:
        return

    try:
        if element.role_name == "table":
            tables.append(element)

        count = element._native_obj.childCount
        for i in range(min(count, 50)):
            child = element._native_obj.getChildAtIndex(i)
            child_element = LinuxElement(child, element.access_agent, element.wm_agent, parent=element)
            _find_all_tables(child_element, tables, depth + 1)
    except Exception:
        pass


def test_libreoffice_selection():
    """
    Verifies cell selection in LibreOffice Calc: D1, D3, D5, B2, B4.
    """
    if platform.system() != "Linux":
        return

    testbase.assert_equal(_try_import_pyatspi(), True)

    try:
        env = os.environ.copy()
        env['GDK_BACKEND'] = 'x11'
        proc = subprocess.Popen(["libreoffice", "--calc"], env=env)
    except FileNotFoundError:
        testbase.assert_equal(True, False, "libreoffice not found")

    try:
        # Give it time to appear
        time.sleep(10.0)
        testbase.assert_equal(proc.poll() is None, True)

        automation = AutomationFactory.get_automation_engine()
        _handle_tip_dialog(automation)

        app = None
        for name in ["soffice", "LibreOffice", "libreoffice", "calc"]:
            app = automation.get_application_by_name(name)
            if app:
                break
        
        testbase.assert_equal(app is not None, True, "Correct application not found")

        windows = app.get_windows()
        testbase.assert_equal(len(windows) > 0, True)

        main_window = None
        for window in windows:
            if "Calc" in window.title:
                main_window = window
                break
        if not main_window:
            main_window = windows[0]

        try:
            main_window.activate()
        except:
            pass
        time.sleep(1.0)

        tables_found = []
        _find_all_tables(main_window, tables_found)

        spreadsheet = None
        max_children = -1
        for table in tables_found:
             # Heuristic: main spreadsheet usually has many children (cells)
             count = table._native_obj.childCount
             if count > max_children:
                 max_children = count
                 spreadsheet = TableElement(table._native_obj, table.access_agent, table.wm_agent, parent=table.parent)
        
        testbase.assert_equal(spreadsheet is not None, True, "Spreadsheet table not found")

        # Cells to select: D1, D3, D5, B2, B4
        # Columns (0-indexed): A=0, B=1, C=2, D=3
        # Rows (0-indexed): 1=0, 2=1, ...
        
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
            # Note: select_cell is the new/preferred method on UITable
            spreadsheet.select_cell(row, col)
            
            time.sleep(0.5)
            
            # Validation: Check if the specific cell has 'focused' or 'selected' state
            cell = spreadsheet.get_cell(row, col)
            testbase.assert_equal(cell is not None, True, f"Could not get cell object for {label}")
            testbase.assert_equal(cell.row, row, f"Cell row mismatch for {label}")
            testbase.assert_equal(cell.column, col, f"Cell column mismatch for {label}")
            
            # Using raw pyatspi check for robustness in validation
            states = cell._native_obj.getState()
            
            # State set usually contains STATE_FOCUSED and/or STATE_SELECTED/STATE_ACTIVE
            import pyatspi
            
            is_focused = states.contains(pyatspi.STATE_FOCUSED)
            is_selected = states.contains(pyatspi.STATE_SELECTED)
            
            print(f"  {label} -> Focused: {is_focused}, Selected: {is_selected}")
            
            # Assert either focused or selected is true
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
