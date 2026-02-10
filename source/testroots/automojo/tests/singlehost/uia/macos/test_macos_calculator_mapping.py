import platform

from automojo import testbase


def test_macos_calculator_mapping(uia_controller):
    """
        Validates the MacOS Calculator declarative mapping resolves key elements.
    """
    if platform.system() != "Darwin":
        return

    if uia_controller is None:
        return

    from automojo.uia.platforms.macos.wrappers.uiaaccessibility import is_accessibility_trusted
    from automojo.uia.platforms.macos.mappings.calculator import Calculator

    if is_accessibility_trusted(prompt=False) is False:
        return

    app = Calculator.launch_or_attach(uia_controller)
    testbase.assert_equal(app is not None, True)

    window = Calculator.MainWindow.resolve(app)
    testbase.assert_equal(window is not None, True)

    display = Calculator.DisplayTextField.resolve(window)
    if display is None:
        display = Calculator.DisplayStaticText.resolve(window)

    testbase.assert_equal(display is not None, True)

    button_one = Calculator.Button1.resolve(window)
    testbase.assert_equal(button_one is not None, True)

    button_plus = Calculator.ButtonAdd.resolve(window)
    if button_plus is None:
        button_plus = Calculator.ButtonAddWord.resolve(window)

    testbase.assert_equal(button_plus is not None, True)

    button_equals = Calculator.ButtonEquals.resolve(window)
    if button_equals is None:
        button_equals = Calculator.ButtonEqualsWord.resolve(window)

    testbase.assert_equal(button_equals is not None, True)

    if hasattr(app, "terminate"):
        app.terminate()

    return
