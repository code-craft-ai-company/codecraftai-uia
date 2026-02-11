
from abc import ABC, abstractmethod
from typing import List, Any, Tuple, Optional
import weakref
from automojo.uia.exceptions import (
    UIAException,
    ElementNotFoundError,
    InteractionError,
    PlatformNotSupportedError
)


class UIObject(ABC):
    """
        Base class for all UI objects.
    """

    @abstractmethod
    def __repr__(self) -> str:
        """
            Returns a string representation of the object.
        """
        pass

    @property
    def exists(self) -> bool:
        """
        Checks if the object currently exists/is valid.
        Default implementation assumes object exists if python object exists.
        Subclasses should override if they wrap a transient native object.
        """
        return True


class DisplayElement(UIObject):
    """
        Foundation class for any displayed UI object.
        Provides common properties for position, size, and visibility.
    """

    @property
    @abstractmethod
    def bounds(self) -> Tuple[int, int, int, int]:
        """
            The bounding rectangle (x, y, width, height) of the element.
        """
        pass

    @property
    @abstractmethod
    def position(self) -> Tuple[int, int]:
        """
            The position (x, y) of the element on screen.
        """
        pass

    @property
    @abstractmethod
    def size(self) -> Tuple[int, int]:
        """
            The size (width, height) of the element.
        """
        pass

    @property
    @abstractmethod
    def is_visible(self) -> bool:
        """
            True if the element is visible, False otherwise.
        """
        pass


class ScreenElement(DisplayElement):
    """
        Foundation class for screen-level objects like windows and applications.
        Provides properties and methods for managing screen positioning and layering.
    """

    @abstractmethod
    def bring_to_front(self) -> None:
        """
            Brings the element to the front (highest z-order).
        """
        pass

    @abstractmethod
    def send_to_back(self) -> None:
        """
            Sends the element to the back (lowest z-order).
        """
        pass


class UIElement(DisplayElement):
    """
        Abstract base class for UI elements (controls/widgets).
    """
    
    def __init__(self, parent: Optional['UIElement'] = None):
        self._parent = weakref.ref(parent) if parent else None

    @property
    def parent(self) -> Optional['UIElement']:
        """
            Returns the parent UI element.
        """
        if self._parent:
             return self._parent()
        return None

    @property
    @abstractmethod
    def name(self) -> str:
        """
            The name of the element.
        """
        pass

    @property
    @abstractmethod
    def is_enabled(self) -> bool:
        """
            True if the element is enabled, False otherwise.
        """
        pass

    @abstractmethod
    def click(self) -> None:
        """
            Performs a click action on the element.
        """
        pass

    @abstractmethod
    def type_keys(self, keys: str) -> None:
        """
            Types keys into the element.

            :param keys: The keys to type.
        """
        pass

    @abstractmethod
    def find_element(self, **kwargs) -> Optional['UIElement']:
        """
            Finds the first child element matching criteria.
            :param kwargs: Search criteria (name, role, etc.)
            :returns: Matching UIElement or None
        """
        pass

    @abstractmethod
    def find_elements(self, **kwargs) -> List['UIElement']:
        """
            Finds all child elements matching criteria.
            :param kwargs: Search criteria (name, role, etc.)
            :returns: List of matching UIElements
        """
        pass

    def wait_for_element(self, timeout: float = 10.0, interval: float = 0.5, **kwargs) -> 'UIElement':
        """
        Waits for a child element matching criteria to appear.
        
        :param timeout: Maximum time to wait in seconds.
        :param interval: Time to wait between checks.
        :param kwargs: Search criteria (name, role, etc.)
        :returns: The found UIElement.
        :raises: ElementNotFoundError if not found within timeout.
        """
        import time
        end_time = time.time() + timeout
        
        while time.time() < end_time:
            element = self.find_element(**kwargs)
            if element and element.exists:
                return element
            time.sleep(interval)
            
        raise ElementNotFoundError(f"Element matching {kwargs} not found within {timeout}s")

    def wait_until_gone(self, timeout: float = 10.0, interval: float = 0.5) -> bool:
        """
        Waits until this element no longer exists/is visible.
        
        :param timeout: Maximum time to wait in seconds.
        :param interval: Time to wait between checks.
        :returns: True if gone, False if timeout reached.
        """
        import time
        end_time = time.time() + timeout
        
        while time.time() < end_time:
            if not self.exists or not self.is_visible:
                return True
            time.sleep(interval)
            
        return False


class UIButton(UIElement):
    """
        Abstract base class for button controls.
    """

    @property
    @abstractmethod
    def label(self) -> str:
        """
            The label/text displayed on the button.
        """
        pass

    @abstractmethod
    def double_click(self) -> None:
        """
            Performs a double-click action on the button.
        """
        pass


class UIText(UIElement):
    """
        Abstract base class for text fields and labels.
    """

    @property
    @abstractmethod
    def text(self) -> str:
        """
            The text content of the element.
        """
        pass

    @property
    @abstractmethod
    def is_editable(self) -> bool:
        """
            True if the text can be edited, False otherwise.
        """
        pass

    @abstractmethod
    def get_text(self) -> str:
        """
            Gets the text content.
        """
        pass

    @abstractmethod
    def set_text(self, text: str) -> None:
        """
            Sets the text content.
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """
            Clears the text content.
        """
        pass


class UIList(UIElement):
    """
        Abstract base class for list controls.
    """

    @property
    @abstractmethod
    def item_count(self) -> int:
        """
            The number of items in the list.
        """
        pass

    @abstractmethod
    def get_item(self, index: int) -> Optional[UIElement]:
        """
            Gets the item at the specified index.
        """
        pass

    @abstractmethod
    def select_item(self, index: int) -> None:
        """
            Selects the item at the specified index.
        """
        pass

    @abstractmethod
    def scroll_to_item(self, index: int) -> None:
        """
            Scrolls to make the item at the specified index visible.
        """
        pass


class UICell(UIText):
    """
    Abstract base class for table cells.
    """

    @property
    @abstractmethod
    def row(self) -> int:
        """
        The row index of the cell.
        """
        pass

    @property
    @abstractmethod
    def column(self) -> int:
        """
        The column index of the cell.
        """
        pass


class UITable(UIElement):
    """
        Abstract base class for table/grid controls.
    """

    @property
    @abstractmethod
    def row_count(self) -> int:
        """
            The number of rows in the table.
        """
        pass

    @property
    @abstractmethod
    def column_count(self) -> int:
        """
            The number of columns in the table.
        """
        pass

    @abstractmethod
    def get_cell(self, row: int, column: int) -> Optional[UICell]:
        """
            Gets the cell at the specified row and column.
        """
        pass
    
    @abstractmethod
    def get_range(self, start_row: int, start_column: int, end_row: int, end_column: int) -> List[UICell]:
        """
            Gets a range of cells.
        """
        pass

    @abstractmethod
    def select_cell(self, row: int, column: int) -> None:
        """
            Selects the cell at the specified row and column.
        """
        pass

    @abstractmethod
    def get_cell_value(self, row: int, column: int) -> str:
        """
            Gets the value of the cell at the specified row and column.
            This is a convenience method for getting text without creating a cell object, 
            though implementations might just call get_cell(r,c).text
        """
        pass


class UIMenuBar(UIElement):
    """
        Abstract base class for menu bar controls.
    """

    @abstractmethod
    def get_menu(self, name: str) -> Optional['UIMenu']:
        """
            Gets a menu by name from the menu bar.
        """
        pass

    @abstractmethod
    def get_menus(self) -> List['UIMenu']:
        """
            Gets all menus in the menu bar.
        """
        pass


class UIMenu(UIElement):
    """
        Abstract base class for menu controls.
    """

    @property
    @abstractmethod
    def is_open(self) -> bool:
        """
            True if the menu is currently open, False otherwise.
        """
        pass

    @abstractmethod
    def open(self) -> None:
        """
            Opens the menu.
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """
            Closes the menu.
        """
        pass

    @abstractmethod
    def get_item(self, name: str) -> Optional['UIMenuItem']:
        """
            Gets a menu item by name.
        """
        pass

    @abstractmethod
    def get_items(self) -> List['UIMenuItem']:
        """
            Gets all items in the menu.
        """
        pass


class UISubMenu(UIMenu):
    """
        Abstract base class for submenu controls (menus within menus).
        Inherits all behavior from UIMenu.
    """
    
    @property
    @abstractmethod
    def parent_menu(self) -> Optional['UIMenu']:
        """
            Gets the parent menu that contains this submenu.
        """
        pass


class UIMenuItem(UIElement):
    """
        Abstract base class for menu item controls.
    """

    @property
    @abstractmethod
    def is_checked(self) -> bool:
        """
            True if the menu item is checked (for checkable items), False otherwise.
        """
        pass

    @property
    @abstractmethod
    def is_separator(self) -> bool:
        """
            True if this is a separator item, False otherwise.
        """
        pass

    @abstractmethod
    def invoke(self) -> None:
        """
            Invokes/activates the menu item (same as clicking it).
        """
        pass


class UIWindow(ScreenElement):
    """
        Abstract base class for windows.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
            The name of the window.
        """
        pass

    @property
    @abstractmethod
    def title(self) -> str:
        """
            The title of the window.
        """
        pass

    @abstractmethod
    def click(self) -> None:
        """
            Clicks on the window.
        """
        pass

    @abstractmethod
    def type_keys(self, keys: str) -> None:
        """
            Types keys into the window.
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """
            Closes the window.
        """
        pass

    @abstractmethod
    def maximize(self) -> None:
        """
            Maximizes the window.
        """
        pass

    @abstractmethod
    def minimize(self) -> None:
        """
            Minimizes the window.
        """
        pass

    @abstractmethod
    def restore(self) -> None:
        """
            Restores the window to its normal state.
        """
        pass


class UIApplication(ScreenElement):
    """
        Abstract base class for applications.
    """

    def __init__(self, parent: Optional['UIElement'] = None):
        super().__init__(parent)
        self._declarative_model = None

    @property
    def declarative_model(self):
        """
        The declarative model class associated with this application instance.
        """
        return self._declarative_model

    @declarative_model.setter
    def declarative_model(self, value):
        self._declarative_model = value

    def resolve_to_hint(self, window: 'UIWindow'):
        """
        Resolves a window instance to its corresponding ElementHint in the declarative model.
        """
        if not self.declarative_model:
            return None
        
        if not window:
            return None

        # Iterate through the model's attributes to find matching hints
        # We look for WindowHint or DialogHint
        # Import here to avoid circular dependency
        from automojo.uia.model.declarative import WindowHint, DialogHint

        for name, value in vars(self.declarative_model).items():
            if isinstance(value, (WindowHint, DialogHint)):
                if value.matches(window):
                    return value
        
        return None

    @property
    @abstractmethod
    def name(self) -> str:
        """
            The name of the application.
        """
        pass

    @property
    @abstractmethod
    def identifier(self) -> str:
        """
            The unique identifier of the application (e.g., bundle ID).
        """
        pass

    @abstractmethod
    def click(self) -> None:
        """
            Clicks on the application.
        """
        pass

    @abstractmethod
    def type_keys(self, keys: str) -> None:
        """
            Types keys into the application.
        """
        pass

    @abstractmethod
    def launch(self) -> None:
        """
            Launches the application.
        """
        pass

    @abstractmethod
    def terminate(self) -> None:
        """
            Terminates the application.
        """
        pass

    @abstractmethod
    def activate(self) -> None:
        """
            Activates the application (brings it to front).
        """
        pass

    @abstractmethod
    def get_windows(self) -> List[UIWindow]:
        """
            Returns a list of windows belonging to the application.

            :returns: A list of UIWindow objects.
        """
        pass


class AutomationEngine(ABC):
    """
        Abstract base class for the automation engine.
    """

    @abstractmethod
    def get_application_by_name(self, application_name: str) -> UIApplication:
        """
            Gets an application by its name.

            :param application_name: The name of the application.
            :returns: A UIApplication object.
        """
        pass


class UIDialog(UIWindow):
    """
        Abstract base class for dialog windows.
    """
    pass


class UIModalDialog(UIDialog):
    """
        Abstract base class for modal dialogs.
    """
    pass


class UISaveDialog(UIModalDialog):
    """
        Abstract base class for Save dialogs.
    """

    @abstractmethod
    def set_filename(self, filename: str) -> None:
        """
            Sets the filename to save.
        """
        pass

    @abstractmethod
    def save(self) -> None:
        """
            Performs the save action (clicks Save button).
        """
        pass


class UISaveAsDialog(UISaveDialog):
    """
        Abstract base class for Save As dialogs.
    """
    pass


class UIOpenDialog(UIModalDialog):
    """
        Abstract base class for Open dialogs.
    """

    @abstractmethod
    def set_filename(self, filename: str) -> None:
        """
            Sets the filename to open.
        """
        pass

    @abstractmethod
    def open(self) -> None:
        """
            Performs the open action (clicks Open button).
        """
        pass



class UIModalDialogFileAlreadyExists(UIModalDialog):
    """
        Abstract base class for "File Already Exists" confirmation dialogs.
    """

    @abstractmethod
    def confirm_overwrite(self) -> None:
        """
            Confirms the overwrite action (clicks Yes/Replace).
        """
        pass


class UIDropDownMenu(UIMenu):
    """
    Abstract base class for drop-down menus (typically in a menu bar).
    """
    pass

