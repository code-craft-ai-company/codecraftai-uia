
from automojo.uia.model.declarative import (
    DeclarativeApplication, 
    ElementHint, 
    WindowHint, 
    MenuBarHint, 
    MenuHint, 
    MenuItemHint, 
    DialogHint,
    ButtonHint,
    TextHint
)

class SaveAsDialog(DialogHint):
    """
    Mapping for Save As Dialog.
    """
    FileNameInput = TextHint(role="text") # Primary text input
    FileNameEntry = TextHint(role="entry") # Fallback
    SaveButton = ButtonHint(name="Save")

class ConfirmDialog(DialogHint):
    """
    Mapping for Confirmation Dialog.
    """
    YesButton = ButtonHint(name="Yes")
    ReplaceButton = ButtonHint(name="Replace")

class LibreOfficeCalc(DeclarativeApplication):
    """
    Declarative mapping for LibreOffice Calc.
    """
    APPLICATION_NAME = "soffice" 
    # Fallback name "Calc" is handled in logic, declarative App name is primary key
    
    # Hints
    # Note: Name might be variable (e.g. "Untitled 1 - LibreOffice Calc")
    # We rely on the test logic to filter windows using this hint as a reference
    MainWindow = WindowHint(role="frame", name="LibreOffice Calc")
    """The main application window."""
    
    class MenuBar(MenuBarHint):
        """Application Menu Bar."""
        File = MenuHint(name="File")
        """File menu."""

    SaveAsMenuItem = MenuItemHint(name="Save As...")
    """'Save As...' menu item."""

    # Attached Dialogs
    SaveAs = SaveAsDialog(name="Save As")
    """Attached Save As dialog."""
    
    ConfirmOverwrite = ConfirmDialog(name="Confirm")
    """Attached File Exists Confirmation dialog."""
