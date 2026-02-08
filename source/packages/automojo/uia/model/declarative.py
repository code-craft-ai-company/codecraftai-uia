
from typing import Optional, Type, Any, List, TypeVar, Generic
from automojo.uia.platforms.base import (
    UIElement, UIApplication, UIWindow, AutomationEngine,
    UIButton, UIText, UIList, UIMenu, UIMenuItem, UIMenuBar, UITable,
    UIDialog, UIModalDialog, UISaveDialog, UIModalDialogFileAlreadyExists
)
from automojo.uia.factory import AutomationFactory

T = TypeVar('T', bound=UIElement)

class ElementHint(Generic[T]):
    """
    Declarative hint to locate a UI element of type T.
    
    :param type_class: The expected class of the element (e.g. UIButton). 
                       Used for return type inference and optional runtime validation.
    :param name: The name of the element to match.
    :param role: The role of the element to match.
    :param access_name: Alternate accessibility name.
    """
    def __init__(self, type_class: Type[T] = UIElement, name: str = None, role: str = None, access_name: str = None):
        self.type_class = type_class
        self.name = name
        self.role = role
        self.access_name = access_name

    def resolve(self, parent: UIElement) -> Optional[T]:
        """
        Resolves the hint to a concrete UI element within the parent context.
        
        :param parent: The parent UI element to search within.
        :return: The found element as type T, or None.
        """
        # Strategy: Use parent's find capability
        found = None
        
        # Check if parent supports find_descendant (Linux style)
        if hasattr(parent, 'find_descendant'):
            found = parent.find_descendant(name=self.name, role=self.role)
            
        # Check if parent supports find_first_by_role (MacOS style)
        elif hasattr(parent, 'find_first_by_role') and self.role:
            found = parent.find_first_by_role(role=self.role)
            
        elif hasattr(parent, 'find_by_title') and self.name:
            matches = parent.find_by_title(title=self.name)
            if matches:
                found = matches[0]
                
        if found:
            # Future: casting or wrapping if needed to ensure T
            # For now, we assume the underlying system returns a compatible object
            # or relies on duck typing. The hints primarily help static analysis.
            return found # type: ignore
            
        return None

# Specialized Hints for common controls
class WindowHint(ElementHint[UIWindow]):
    """Hint for locating a Window."""
    def __init__(self, name: str = None, role: str = "window", access_name: str = None):
        super().__init__(UIWindow, name, role, access_name)

class DialogHint(ElementHint[UIDialog]):
    """Hint for locating a Dialog."""
    def __init__(self, name: str = None, role: str = "dialog", access_name: str = None):
        super().__init__(UIDialog, name, role, access_name)

class ButtonHint(ElementHint[UIButton]):
    """Hint for locating a Button."""
    def __init__(self, name: str = None, role: str = "push button", access_name: str = None):
        super().__init__(UIButton, name, role, access_name)

class TextHint(ElementHint[UIText]):
    """Hint for locating a Text control."""
    def __init__(self, name: str = None, role: str = "text", access_name: str = None):
        super().__init__(UIText, name, role, access_name)

class MenuBarHint(ElementHint[UIMenuBar]):
    """Hint for locating a Menu Bar."""
    def __init__(self, name: str = None, role: str = "menu bar", access_name: str = None):
        super().__init__(UIMenuBar, name, role, access_name)

class MenuHint(ElementHint[UIMenu]):
    """Hint for locating a Menu."""
    def __init__(self, name: str = None, role: str = "menu", access_name: str = None):
        super().__init__(UIMenu, name, role, access_name)

class MenuItemHint(ElementHint[UIMenuItem]):
    """Hint for locating a Menu Item."""
    def __init__(self, name: str = None, role: str = "menu item", access_name: str = None):
        super().__init__(UIMenuItem, name, role, access_name)


class DeclarativeApplication:
    """
    Base class for declarative application models.
    Note: This is a factory/proxy, not the actual application instance.
    It returns a concrete UIApplication when valid.
    """
    
    APPLICATION_HINT: str = None
    APPLICATION_NAME: str = None
    
    @classmethod
    def attach(cls, automation_engine: Optional[AutomationEngine] = None) -> Optional[UIApplication]:
        """
        Attaches to the running application matching the hint.
        """
        if not automation_engine:
             automation_engine = AutomationFactory.get_automation_engine()
             
        if cls.APPLICATION_NAME:
            return automation_engine.get_application_by_name(cls.APPLICATION_NAME)
        
        # Future: Implement more complex matching logic using APPLICATION_HINT
        return None

    @classmethod
    def launch_or_attach(cls, automation_engine: Optional[AutomationEngine] = None) -> Optional[UIApplication]:
        """
        Launches the application if not running, or attaches to it.
        """
        app = cls.attach(automation_engine)
        if app:
            return app
            
        # Launch logic would go here, possibly using the hint
        # For now, we rely on attach logic which might auto-launch on some platforms (MacOS)
        return None
