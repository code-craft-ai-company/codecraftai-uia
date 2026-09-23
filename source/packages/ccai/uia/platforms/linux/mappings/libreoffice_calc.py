
from ccai.uia.model.declarative import (
    DeclarativeApplication,
    WindowHint,
    MenuBarHint,
    MenuHint,
    MenuItemHint,
    DialogHint,
    ButtonHint,
    TextHint,
    TableHint,
)

class TipOfTheDayDialog(DialogHint):
    """
    Mapping for Tip of the Day Dialog.
    """
    OKButton = ButtonHint(name="OK")
    CloseButton = ButtonHint(name="Close")

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
    APPLICATION_COMMAND = "libreoffice --calc --norestore"
    # Fallback name "Calc" is handled in logic, declarative App name is primary key
    
    # Hints
    # Note: Name might be variable (e.g. "Untitled 1 - LibreOffice Calc")
    # We rely on the test logic to filter windows using this hint as a reference
    MainWindow = WindowHint(role="frame", name="~LibreOffice Calc")
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
    
    ConfirmOverwrite = ConfirmDialog(name="Question", role="alert")
    """Attached File Exists Confirmation dialog."""

    TipOfTheDay = TipOfTheDayDialog(name="Tip of the Day")
    """Tip of the Day dialog which appears on startup."""

    # Spreadsheet
    # We use a recursive search or path to ensure we find the main table
    # Heuristic from tests: "table" role with most children.
    # Declarative: we can try to be specific or just map "Table"
    Spreadsheet = TableHint(role="table")
    """The main spreadsheet table."""
