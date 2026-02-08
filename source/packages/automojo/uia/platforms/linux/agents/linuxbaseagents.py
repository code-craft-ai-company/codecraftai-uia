
from abc import ABC, abstractmethod
from typing import Any, List, Tuple

class AccessibilityAgent(ABC):
    """
    Abstract base class for interacting with the Accessibility layer (e.g., AT-SPI).
    """
    @abstractmethod
    def get_root(self) -> Any:
        pass

    @abstractmethod
    def get_application_by_name(self, name: str) -> Any:
        pass

    @abstractmethod
    def get_role(self, element: Any) -> Any:
        pass

    @abstractmethod
    def get_role_name(self, element: Any) -> str:
        pass

    @abstractmethod
    def get_name(self, element: Any) -> str:
        pass

    @abstractmethod
    def get_text(self, element: Any) -> str:
        pass
        
    @abstractmethod
    def get_children(self, element: Any) -> List[Any]:
        pass
        
    @abstractmethod
    def get_states(self, element: Any) -> List[Any]:
        pass

    @abstractmethod
    def do_action(self, element: Any, action_index: int) -> bool:
        pass

    # ... add other methods as needed (find descendant etc)

class WindowManagerAgent(ABC):
    """
    Abstract base class for interacting with the Window Manager (e.g., X11, Wayland).
    """

    

    @abstractmethod
    def get_active_window(self) -> Any:
        pass

    @abstractmethod
    def get_all_windows(self) -> List[Any]:
        pass

    @abstractmethod
    def get_default_display(self) -> Any:
        pass

    @abstractmethod
    def focus_window(self, window_name: str) -> bool:
        pass

    @abstractmethod
    def send_keys(self, window: Any, keys: str) -> None:
        pass
        
    @abstractmethod
    def click(self, x: int, y: int) -> None:
         pass

class DesktopAgent(ABC):
    """
    Abstract base class for interacting with the Desktop Environment (e.g., GNOME, KDE).
    """
    @abstractmethod
    def launch_app(self, command: str) -> Any:
        pass
