
from automojo.uia.model.declarative import DeclarativeApplication, WindowHint, TextHint, ButtonHint

class Calculator(DeclarativeApplication):
    """
    Declarative mapping for the GNOME Calculator application.
    """
    APPLICATION_NAME = "gnome-calculator"
    
    # Hints
    MainWindow = WindowHint(role="frame", name="Calculator")
    """The main calculator window."""
    
    # Display typically has role 'text' or 'entry' somewhat deep in the hierarchy
    # We can use a more specific hint if we know the exact path or unique properties
    # For now, relying on 'text' role which worked in the original test
    Display = TextHint(role="text")
    DisplayEntry = TextHint(role="entry") # Fallback for some versions
    DisplayEdit = TextHint(role="edit")   # Another fallback
    """The calculator display area showing current input/result."""
    
    # Buttons
    # Buttons (Digits)
    Button0 = ButtonHint(name="0")
    Button1 = ButtonHint(name="1")
    Button2 = ButtonHint(name="2")
    Button3 = ButtonHint(name="3")
    Button4 = ButtonHint(name="4")
    Button5 = ButtonHint(name="5")
    Button6 = ButtonHint(name="6")
    Button7 = ButtonHint(name="7")
    Button8 = ButtonHint(name="8")
    Button9 = ButtonHint(name="9")

    # Operators
    ButtonAdd = ButtonHint(name="+")
    ButtonSubtract = ButtonHint(name="-") # or "−" depending on locale/app version
    ButtonMultiply = ButtonHint(name="*") # or "×"
    ButtonDivide = ButtonHint(name="/")   # or "÷"
    ButtonEquals = ButtonHint(name="=")
    
    ButtonResult = ButtonHint(name="Result")
    ButtonClear = ButtonHint(name="C")
