
from automojo.uia.platforms.base import UIWindow
from automojo.uia.platforms.linux.wrappers.uiaelement import LinuxElement

class LinuxWindow(LinuxElement, UIWindow):
    """
        Wrapper for Linux windows using pyatspi.
    """
    
    @property
    def title(self) -> str:
        return self.name

    def close(self) -> None:
        raise NotImplementedError("Close is not yet implemented for Linux windows.")

    def maximize(self) -> None:
        raise NotImplementedError("Maximize is not yet implemented for Linux windows.")

    def minimize(self) -> None:
        raise NotImplementedError("Minimize is not yet implemented for Linux windows.")

    def restore(self) -> None:
        raise NotImplementedError("Restore is not yet implemented for Linux windows.")

    def activate(self) -> None:
        """
            Activates the window (brings it to foreground).
        """
        # Try accessible action first
        self.grab_focus()
        
        # If possible, try to raise
        try:
            component = self._native_obj.queryComponent()
            # method grabFocus is already called by grab_focus
            # layer = component.getLayer()
            pass
        except:
            pass

    def __repr__(self) -> str:
        return f"LinuxWindow<{self.title}>"
