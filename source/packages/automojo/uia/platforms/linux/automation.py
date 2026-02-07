
try:
    import pyatspi
except ImportError:
    pyatspi = None

from automojo.uia.platforms.base import AutomationEngine, UIApplication
from automojo.uia.platforms.linux.wrappers.uiaapplication import LinuxApplication

class LinuxAutomation(AutomationEngine):
    """
        Automation engine for Linux using pyatspi.
    """
    def __init__(self):
        if pyatspi is None:
            raise ImportError("pyatspi is required for Linux automation but is not installed.")
        
        # Ensure registry is loaded
        self._registry = pyatspi.Registry
        return

    def get_application_by_name(self, application_name: str) -> UIApplication:
        """
            Gets an application by its name from the AT-SPI registry.
        """
        desktop = self._registry.getDesktop(0)
        count = desktop.childCount
        for i in range(count):
            try:
                app = desktop.getChildAtIndex(i)
                if app.name == application_name:
                    return LinuxApplication(app)
            except Exception:
                continue
                
        return None
