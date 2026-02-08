
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
    """The calculator display area showing current input/result."""
    
    # Buttons
    Button1 = ButtonHint(name="1")
    """Number button 1."""
    
    Button2 = ButtonHint(name="2")
    """Number button 2."""
    
    Button3 = ButtonHint(name="3")
    """Number button 3."""
    
    ButtonAdd = ButtonHint(name="+")
    """Addition operator button."""
    
    ButtonMultiply = ButtonHint(name="*")
    """Multiplication operator button."""
    
    ButtonEquals = ButtonHint(name="=")
    """Equals/Calculate button."""
    
    ButtonResult = ButtonHint(name="Result")
    """Result button (if applicable)."""
