
from typing import List, Any
try:
    import pyatspi
except ImportError:
    pyatspi = None

from automojo.uia.platforms.base import UIApplication, UIWindow
from automojo.uia.platforms.linux.wrappers.uiaelement import LinuxElement
from automojo.uia.platforms.linux.wrappers.uiawindow import LinuxWindow

class LinuxApplication(LinuxElement, UIApplication):
    """
        Wrapper for Linux applications using pyatspi.
    """
    
    def __init__(self, native_obj: Any):
        super().__init__(native_obj)

    @property
    def identifier(self) -> str:
        # Using ID if available, otherwise name as fallback
        return str(self._native_obj.id)

    def launch(self) -> None:
        pass # Assumes already running for now

    def terminate(self) -> None:
        raise NotImplementedError("Terminate is not yet implemented for Linux applications.")

    def activate(self) -> None:
        raise NotImplementedError("Activate is not yet implemented for Linux applications.")

    def get_windows(self) -> List[UIWindow]:
        windows = []
        if not pyatspi:
            return windows

        count = self._native_obj.childCount
        for i in range(count):
            try:
                child = self._native_obj.getChildAtIndex(i)
                # Check for ROLE_FRAME (standard window) or similar roles
                if child.getRole() == pyatspi.ROLE_FRAME:
                    windows.append(LinuxWindow(child))
            except Exception:
                continue
                
        return windows

    def __repr__(self) -> str:
        return f"LinuxApplication<{self.name}>"
