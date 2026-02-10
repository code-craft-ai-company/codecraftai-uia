from automojo.uia.model.declarative import DeclarativeApplication, WindowHint, TextHint, ButtonHint

AX_WINDOW_ROLE = "AXWindow"
AX_BUTTON_ROLE = "AXButton"
AX_TEXT_ROLE = "AXTextField"
AX_STATIC_TEXT_ROLE = "AXStaticText"


class Calculator(DeclarativeApplication):
    """
        Declarative mapping for the MacOS Calculator application.
    """

    APPLICATION_NAME = "Calculator"
    APPLICATION_COMMAND = "open -a Calculator"

    MainWindow = WindowHint(role=AX_WINDOW_ROLE, name="Calculator")
    """The main Calculator window."""

    DisplayTextField = TextHint(role=AX_TEXT_ROLE)
    DisplayStaticText = TextHint(role=AX_STATIC_TEXT_ROLE)
    """Display control(s) showing the current input or result."""

    # Digits
    Button0 = ButtonHint(name="0", role=AX_BUTTON_ROLE)
    Button1 = ButtonHint(name="1", role=AX_BUTTON_ROLE)
    Button2 = ButtonHint(name="2", role=AX_BUTTON_ROLE)
    Button3 = ButtonHint(name="3", role=AX_BUTTON_ROLE)
    Button4 = ButtonHint(name="4", role=AX_BUTTON_ROLE)
    Button5 = ButtonHint(name="5", role=AX_BUTTON_ROLE)
    Button6 = ButtonHint(name="6", role=AX_BUTTON_ROLE)
    Button7 = ButtonHint(name="7", role=AX_BUTTON_ROLE)
    Button8 = ButtonHint(name="8", role=AX_BUTTON_ROLE)
    Button9 = ButtonHint(name="9", role=AX_BUTTON_ROLE)

    # Operators (symbol variants)
    ButtonAdd = ButtonHint(name="+", role=AX_BUTTON_ROLE)
    ButtonSubtract = ButtonHint(name="-", role=AX_BUTTON_ROLE)
    ButtonMultiply = ButtonHint(name="*", role=AX_BUTTON_ROLE)
    ButtonDivide = ButtonHint(name="/", role=AX_BUTTON_ROLE)
    ButtonEquals = ButtonHint(name="=", role=AX_BUTTON_ROLE)

    # Operators (word variants - accessibility labels may vary by OS version)
    ButtonAddWord = ButtonHint(name="add", role=AX_BUTTON_ROLE)
    ButtonSubtractWord = ButtonHint(name="subtract", role=AX_BUTTON_ROLE)
    ButtonMultiplyWord = ButtonHint(name="multiply", role=AX_BUTTON_ROLE)
    ButtonDivideWord = ButtonHint(name="divide", role=AX_BUTTON_ROLE)
    ButtonEqualsWord = ButtonHint(name="equals", role=AX_BUTTON_ROLE)

    ButtonClear = ButtonHint(name="C", role=AX_BUTTON_ROLE)
    ButtonClearWord = ButtonHint(name="clear", role=AX_BUTTON_ROLE)
