import platform

from automojo import testbase


def test_accessibility_window_search(uia_controller=None):
    """
        Validates accessibility-based window discovery and search helpers.
    """
    system = platform.system()
    if system != "Darwin":
        return

    if uia_controller is None:
        return

    app = uia_controller.get_application_by_name("Calculator")
    testbase.assert_equal(app is not None, True)

    try:
        app.activate()

        windows = app.get_windows()
        testbase.assert_equal(isinstance(windows, list), True)
        testbase.assert_equal(len(windows) > 0, True)

        first_window = windows[0]
        role_match = first_window.find_first_by_role("AXWindow", include_self=True)
        testbase.assert_equal(role_match is not None, True)

        title_matches = first_window.find_by_title(".*", include_self=True, expression=True)
        testbase.assert_equal(isinstance(title_matches, list), True)

        contents_matches = first_window.find_by_contents(".*", include_self=True, expression=True)
        testbase.assert_equal(isinstance(contents_matches, list), True)
    finally:
        if app is not None:
            app.terminate()

    return
