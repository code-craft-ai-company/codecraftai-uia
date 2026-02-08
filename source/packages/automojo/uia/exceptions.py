
class UIAException(Exception):
    """
    Base exception for all UI Automation errors.
    """
    pass

class ElementNotFoundError(UIAException):
    """
    Raised when a UI element cannot be found.
    """
    pass

class InteractionError(UIAException):
    """
    Raised when an interaction with a UI element fails (e.g., click, type).
    """
    pass

class PlatformNotSupportedError(UIAException):
    """
    Raised when a requested feature or action is not supported on the current platform.
    """
    pass
