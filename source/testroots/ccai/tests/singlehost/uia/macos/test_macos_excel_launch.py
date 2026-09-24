import platform
import time

from ccai import testbase
from ccai.errors.exceptions import SkipError
from ccai.tests.singlehost.uia.macos._session import require_accessibility, require_application_installed


def test_macos_excel_launch_creates_workbook(uia_controller=None):
    """
        Launches Microsoft Excel, creates a workbook if needed, and then closes.
    """
    if platform.system() != "Darwin":
        raise SkipError("the MacOS tests need a Darwin host")

    if uia_controller is None:
        raise SkipError("no UI automation controller is available on this host")

    from ccai.uia.platforms.macos.mappings.excel import MicrosoftExcel

    require_application_installed(uia_controller, MicrosoftExcel.APPLICATION_NAME)
    require_accessibility()

    app = MicrosoftExcel.launch_or_attach(uia_controller)
    testbase.assert_equal(app is not None, True)

    try:
        app.activate()

        # Wait loop for a window to appear
        window = None
        hint = None
        
        for _ in range(20):
            window = app.get_focus_window()
            if window:
                hint = app.resolve_to_hint(window)
                if hint:
                    break
            time.sleep(1)

        if hint == MicrosoftExcel.StartDialog:
            start_dialog = window
            
            blank = MicrosoftExcel.StartBlankWorkbook.resolve(start_dialog)
            if blank:
                blank.click()
            else:
                create = MicrosoftExcel.StartCreate.resolve(start_dialog)
                if create:
                    create.click()
            
            # Wait for workbook
            for _ in range(10):
                window = app.get_focus_window()
                if window:
                    hint = app.resolve_to_hint(window)
                    if hint == MicrosoftExcel.MainWindow:
                        break
                time.sleep(1)

        testbase.assert_equal(hint == MicrosoftExcel.MainWindow, True)

        # Final check: the workbook window still has the focus.
        window = app.get_focus_window()
        testbase.assert_equal(window is not None, True)

    finally:
        if app is not None:
            app.terminate()

    return
