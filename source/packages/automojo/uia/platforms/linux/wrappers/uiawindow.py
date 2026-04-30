from typing import Any, Optional, Tuple

from automojo.uia.platforms.base import UIWindow
from automojo.uia.platforms.linux.wrappers.uiaelement import LinuxElement
from automojo.uia.platforms.linux.agents.linuxbaseagents import AccessibilityAgent, WindowManagerAgent
from automojo.uia.platforms.base import UIWindow, UIElement

class LinuxWindow(LinuxElement, UIWindow):
    """
        Wrapper for Linux windows using Agent Architecture.
    """
    def __init__(self, native_obj: Any, access_agent: AccessibilityAgent, wm_agent: WindowManagerAgent, parent: Optional[UIElement] = None, native_window: Any = None):
        super().__init__(native_obj, access_agent, wm_agent, parent=parent)
        self.native_window = native_window
    
    @property
    def title(self) -> str:
        return self.name

    @property
    def main_menu(self) -> Optional['LinuxMenuBar']:
        """Returns the main menu bar of the window."""
        return self.get_main_menu()

    def get_main_menu(self) -> Optional['LinuxMenuBar']:
        from automojo.uia.platforms.linux.wrappers.menuelement import LinuxMenuBar
        
        # Menu bar might be nested (e.g. in a root pane), so search for it
        menu_bar = self.find_descendant(role="menu bar", max_depth=5)
        
        if menu_bar:
             # Repackage as LinuxMenuBar (reusing native obj and agents)
             return LinuxMenuBar(menu_bar.native_obj, self.access_agent, self.wm_agent, parent=self)
            
        return None

    def get_position(self) -> Tuple[int, int]:
        if self.native_window is not None:
            # Check if it's a Broker dict (Wayland Gnome)
            if isinstance(self.native_window, dict):
                 rect = self.native_window.get('rect_logical')
                 if rect is not None:
                     return (rect['x'], rect['y'])
            # Check if it's an X11 window object (has get_geometry)
            elif hasattr(self.native_window, 'get_geometry'):
                 try:
                     geo = self.native_window.get_geometry()
                     return (geo.x, geo.y)
                 except Exception:
                     pass

        # Fall back to the AT-SPI element's coordinates via the access agent.
        # native_obj is an AT-SPI element which has no get_coordinates method
        # of its own; that lives on the AccessibilityAgent.
        coords = self.access_agent.get_coordinates(self.native_obj)
        if coords is not None:
            x, y, _w, _h = coords
            return (x, y)
        return (0, 0)

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
            
            Uses AT-SPI grabFocus as primary method for compatibility with both
            X11 and Wayland applications. X11 focus is attempted as a fallback.
        """
        # Primary method: Use AT-SPI to grab focus
        # This works for both X11 and Wayland applications
        try:
            self.grab_focus()
            # Give the window manager time to process the focus request
            import time
            time.sleep(0.2)
        except Exception as e:
            print(f"AT-SPI grab_focus failed: {e}")
        
        # Secondary method: Try X11/Wayland window manager focus
        # This only works for X11 applications, but we attempt it anyway
        if self.wm_agent:
             # First try using the window name from accessibility tree
             name = self.name
             if name:
                 success = self.wm_agent.focus_window(name)
                 if success:
                     return
             
             # Try a simpler search - just look for 'Calc' for LibreOffice
             if name and 'Calc' in name:
                 success = self.wm_agent.focus_window('Calc')
                 if success:
                     return
             
             # Fallback: Try using the application name from the accessibility tree
             # For gnome-calculator, the app name is "gnome-calculator" while window
             # titles vary (Basic, Advanced, etc.)
             try:
                 app_name = self._native_obj.get_application().name
                 if app_name and app_name != name:
                     self.wm_agent.focus_window(app_name)
             except:
                 pass
    
    def bring_to_front(self) -> None:
        """Brings window to front by activating it."""
        self.activate()
    
    def send_to_back(self) -> None:
        """Sends window to back - not directly supported on Linux."""
        raise NotImplementedError("send_to_back is not supported for Linux windows.")

    def __repr__(self) -> str:
        return f"LinuxWindow<{self.title}>"
