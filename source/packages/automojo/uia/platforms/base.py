
from abc import ABC, abstractmethod
from typing import List, Any


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


class UIElement(UIObject):
    """
        Abstract base class for UI elements (controls).
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
            The name of the element.
        """
        pass

    @property
    @abstractmethod
    def is_visible(self) -> bool:
        """
            True if the element is visible, False otherwise.
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


class UIWindow(UIElement):
    """
        Abstract base class for windows.
    """

    @property
    @abstractmethod
    def title(self) -> str:
        """
            The title of the window.
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


class UIApplication(UIObject):
    """
        Abstract base class for applications.
    """

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
