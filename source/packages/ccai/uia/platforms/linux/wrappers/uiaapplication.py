
from typing import List, Any
try:
    import pyatspi
except ImportError:
    pyatspi = None

from ccai.uia.platforms.base import UIApplication, UIWindow
from ccai.uia.platforms.linux.wrappers.uiaelement import LinuxElement
from ccai.uia.platforms.linux.wrappers.uiawindow import LinuxWindow


from ccai.uia.platforms.linux.agents.linuxbaseagents import AccessibilityAgent, WindowManagerAgent
from typing import Optional
from ccai.uia.platforms.base import UIElement

class LinuxApplication(LinuxElement, UIApplication):
    """
        Wrapper for Linux applications using Agent Architecture.
    """
    
    def __init__(self, native_obj: Any, access_agent: AccessibilityAgent, wm_agent: WindowManagerAgent, parent: Optional[UIElement] = None):
        super().__init__(native_obj, access_agent, wm_agent, parent=parent)

    @property
    def identifier(self) -> str:
        # Using ID if available, otherwise name as fallback
        try:
             return str(self._native_obj.id)
        except Exception:
             return self.name

    def launch(self) -> None:
        pass # Assumes already running for now

    def terminate(self) -> None:
        raise NotImplementedError("Terminate is not yet implemented for Linux applications.")

    def activate(self) -> None:
        """Activates the application by activating its first window."""
        windows = self.get_windows()
        if windows:
            windows[0].activate()
    
    def bring_to_front(self) -> None:
        """Brings application to front by activating its first window."""
        self.activate()
    
    def send_to_back(self) -> None:
        """Sends application to back - not directly supported on Linux."""
        raise NotImplementedError("send_to_back is not supported for Linux applications.")

    def get_windows(self) -> List[UIWindow]:
        windows = []
        children = self.access_agent.get_children(self._native_obj)
        
        for child in children:
            try:
                # Check role. PyAtspi constants might need to be abstracted or we check role name/id
                role = self.access_agent.get_role(child)
                # For now assuming pyatspi specific role check as we know the agent uses pyatspi underlying
                # But ideally we should ask agent "is_window(element)"
                if pyatspi and (role == pyatspi.ROLE_FRAME or role == pyatspi.ROLE_DIALOG or role == pyatspi.ROLE_FILE_CHOOSER):
                    windows.append(LinuxWindow(child, self.access_agent, self.wm_agent, parent=self))
            except Exception:
                continue
                
        return windows

    def __repr__(self) -> str:
        return f"LinuxApplication<{self.name}>"
