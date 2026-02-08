import platform
import subprocess
import time

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


def _set_cell_value(spreadsheet: LinuxElement, row: int, col: int, value: str, expected: str) -> bool:
    print(f"Setting cell ({row}, {col}) to '{value}', expecting '{expected}'")
    
    cell = spreadsheet.get_cell(row, col)
    if not cell:
        print(f"  ERROR: Could not get cell ({row}, {col})")
        return False

    try:
        if value.startswith("="):
             print(f"  Typing formula: {value}")
             cell.set_text(value)
        else:
             print(f"  Typing value: {value}")
             cell.set_text(value)
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
    """
    if platform.system() != "Linux":
        return

    testbase.assert_equal(_try_import_pyatspi(), True)

    try:
        import os
        env = os.environ.copy()
        env['GDK_BACKEND'] = 'x11'
        proc = subprocess.Popen(["libreoffice", "--calc"], env=env)
    except FileNotFoundError:
        testbase.assert_equal(True, False)

    try:
        time.sleep(10.0)
        testbase.assert_equal(proc.poll() is None, True)
        automation = AutomationFactory.get_automation_engine()

        _handle_tip_dialog(automation)

        app = None
        for name in ["soffice", "LibreOffice", "libreoffice", "calc"]:
            app = automation.get_application_by_name(name)
            if app:
                break

        if not app:
            testbase.assert_equal(True, False)

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
        except Exception:
            pass
        time.sleep(1.0)

        tables_found = []
        _find_all_tables(main_window, tables_found)

        spreadsheet = None
        max_children = -1
        for table in tables_found:
            count = table._native_obj.childCount
            if count > max_children:
                max_children = count
                # Wrap the biggest table in TableElement
                spreadsheet = TableElement(table._native_obj, table.access_agent, table.wm_agent, parent=table.parent)

        if not spreadsheet:
            testbase.assert_equal(True, False)

        testbase.assert_equal(_set_cell_value(spreadsheet, 0, 3, "2", "2"), True)
        testbase.assert_equal(_set_cell_value(spreadsheet, 1, 3, "5", "5"), True)
        testbase.assert_equal(_set_cell_value(spreadsheet, 2, 3, "=D1+D2", "7"), True)
    finally:
        proc.terminate()

    return
