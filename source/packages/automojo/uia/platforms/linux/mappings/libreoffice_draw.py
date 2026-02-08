
from automojo.uia.model.declarative import (
    DeclarativeApplication, 
    ElementHint, 
    WindowHint, 
    MenuBarHint, 
    MenuHint, 
    MenuItemHint, 
    DialogHint,
    ButtonHint
)

class AreaDialog(DialogHint):
    """
    Mapping for Area Format Dialog.
    """
    ColorButton = ButtonHint(name="Color")
    # Fallback for ColorButton is handled in test logic or we adding another hint
    
    BlackItem = ElementHint(name="Black") # Item in a list/table, generic element
    OKButton = ButtonHint(name="OK")

class LibreOfficeDraw(DeclarativeApplication):
    """
    Declarative mapping for LibreOffice Draw.
    """
    APPLICATION_NAME = "soffice"
    
    MainWindow = WindowHint(role="frame", name="LibreOffice Draw")
    """The main application window."""
    
    # Tools
    # Note: Name matches "Ellipse" or "Circle" depending on version/icon theme
    EllipseTool = ButtonHint(name="Ellipse") 
    """Ellipse drawing tool."""
    
    CircleTool = ButtonHint(name="Circle")
    """Circle drawing tool (alternative name)."""
    
    # Canvas
    DrawingArea = ElementHint(role="document frame")
    """The main drawing canvas area."""
    
    PageShape = ElementHint(name="PageShape") 
    """The page shape within the drawing area."""
    
    class MenuBar(MenuBarHint):
        """Application Menu Bar."""
        Format = MenuHint(name="Format")
        """Format menu."""
        
    FormatAreaItem = MenuItemHint(name="Area...")
    """'Area...' menu item."""

    # Attached Dialogs
    AreaDialog = AreaDialog(name="Area")
    """Attached Area Format dialog."""
