from ccai.uia.model.declarative import DeclarativeApplication, WindowHint, TextHint, ButtonHint

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

    # Digits (AXIdentifier values)
    Button0 = ButtonHint(name="Zero", role=AX_BUTTON_ROLE)
    Button1 = ButtonHint(name="One", role=AX_BUTTON_ROLE)
    Button2 = ButtonHint(name="Two", role=AX_BUTTON_ROLE)
    Button3 = ButtonHint(name="Three", role=AX_BUTTON_ROLE)
    Button4 = ButtonHint(name="Four", role=AX_BUTTON_ROLE)
    Button5 = ButtonHint(name="Five", role=AX_BUTTON_ROLE)
    Button6 = ButtonHint(name="Six", role=AX_BUTTON_ROLE)
    Button7 = ButtonHint(name="Seven", role=AX_BUTTON_ROLE)
    Button8 = ButtonHint(name="Eight", role=AX_BUTTON_ROLE)
    Button9 = ButtonHint(name="Nine", role=AX_BUTTON_ROLE)

    # Operators (AXIdentifier values)
    ButtonAdd = ButtonHint(name="Add", role=AX_BUTTON_ROLE)
    ButtonSubtract = ButtonHint(name="Subtract", role=AX_BUTTON_ROLE)
    ButtonMultiply = ButtonHint(name="Multiply", role=AX_BUTTON_ROLE)
    ButtonDivide = ButtonHint(name="Divide", role=AX_BUTTON_ROLE)
    ButtonEquals = ButtonHint(name="Equals", role=AX_BUTTON_ROLE)
    ButtonDecimal = ButtonHint(name="Decimal", role=AX_BUTTON_ROLE)
    ButtonPercent = ButtonHint(name="Percent", role=AX_BUTTON_ROLE)
    ButtonNegate = ButtonHint(name="Negate", role=AX_BUTTON_ROLE)

    ButtonClear = ButtonHint(name="AllClear", role=AX_BUTTON_ROLE)
    ButtonDelete = ButtonHint(name="Delete", role=AX_BUTTON_ROLE)
