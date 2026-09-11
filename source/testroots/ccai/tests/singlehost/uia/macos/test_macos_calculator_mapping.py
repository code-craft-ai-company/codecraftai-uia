import platform
import time

from ccai import testbase
from ccai.errors.exceptions import SkipError


def test_macos_calculator_mapping(uia_controller=None):
    """
        Validates the MacOS Calculator declarative mapping resolves key elements.
    """
    if platform.system() != "Darwin":
        raise SkipError("the MacOS tests need a Darwin host")

    if uia_controller is None:
        raise SkipError("no UI automation controller is available on this host")

    from ccai.uia.platforms.macos.mappings.calculator import Calculator

    app = Calculator.launch_or_attach(uia_controller)
    testbase.assert_equal(app is not None, True)

    try:
        app.activate()

        window = None
        for _ in range(10):
            window = Calculator.MainWindow.resolve(app)
            if window is not None:
                break
            time.sleep(0.5)
        testbase.assert_equal(window is not None, True)

        display = Calculator.DisplayTextField.resolve(window)
        if display is None:
            display = Calculator.DisplayStaticText.resolve(window)

        testbase.assert_equal(display is not None, True)

        button_one = Calculator.Button1.resolve(window)
        testbase.assert_equal(button_one is not None, True)

        button_plus = Calculator.ButtonAdd.resolve(window)
        testbase.assert_equal(button_plus is not None, True)

        button_equals = Calculator.ButtonEquals.resolve(window)
        testbase.assert_equal(button_equals is not None, True)
    finally:
        if app is not None and hasattr(app, "terminate"):
            app.terminate()

    return
