from typing import List, Optional, Any
from automojo.uia.platforms.base import UIMenuBar, UIMenu, UIMenuItem, UISubMenu, UIElement, UIDropDownMenu
from automojo.uia.platforms.linux.wrappers.uiaelement import LinuxElement
from automojo.uia.platforms.linux.agents.linuxbaseagents import AccessibilityAgent, WindowManagerAgent

class LinuxMenuItem(LinuxElement, UIMenuItem):
    """
    Wrapper for Linux menu items.
    """
    def __init__(self, native_obj: Any, access_agent: AccessibilityAgent, wm_agent: WindowManagerAgent, parent: Optional[UIElement] = None):
        super().__init__(native_obj, access_agent, wm_agent, parent=parent)

    @property
    def is_checked(self) -> bool:
        # Check for 'checked' state
        states = self.access_agent.get_states(self._native_obj)
        for state in states:
            if str(state) == "checked" or str(state).endswith("CHECKED"):
                return True
        return False

    @property
    def is_separator(self) -> bool:
        return self.role_name == "separator"

    def click(self) -> None:
        """
        Overrides click to prefer Window Manager (physical) click over Accessibility Action.
        This is crucial for Wayland/GTK environments where accessibility actions 
        are often ignored by menus.
        """
        # Try WM click first if coordinates available
        try:
            coords = self.bounds
            if coords and coords[2] > 0 and coords[3] > 0:
                x, y, w, h = coords
                center_x = x + (w // 2)
                center_y = y + (h // 2)
                
                if self.wm_agent:
                    self.wm_agent.click(center_x, center_y)
                    return
        except Exception:
            pass
            
        # Fallback to standard accessibility action
        super().click()

    def invoke(self) -> None:
        """Invokes the menu item (click)."""
        self.click()


class LinuxMenu(LinuxElement, UIMenu):
    """
    Wrapper for Linux menus (e.g. File, Edit).
    """
    def __init__(self, native_obj: Any, access_agent: AccessibilityAgent, wm_agent: WindowManagerAgent, parent: Optional[UIElement] = None):
        super().__init__(native_obj, access_agent, wm_agent, parent=parent)

    @property
    def is_open(self) -> bool:
        # Check 'showing' or 'visible' state generally, but menus might be transient.
        # Often purely logical in UIA, but visual in Linux.
        # Let's check if children are visible? Or state 'selected'?
        # For now, simplistic check.
        return self.is_visible

    def open(self) -> None:
        self.click()

    def click(self) -> None:
        """
        Overrides click to prefer Window Manager (physical) click over Accessibility Action.
        """
        # Try WM click first if coordinates available
        try:
            coords = self.bounds
            if coords and coords[2] > 0 and coords[3] > 0:
                x, y, w, h = coords
                center_x = x + (w // 2)
                center_y = y + (h // 2)
                
                if self.wm_agent:
                    self.wm_agent.click(center_x, center_y)
                    return
        except Exception:
            pass
            
        # Fallback to standard accessibility action
        super().click()

    def close(self) -> None:
        # Click again to close? Or Escape?
        # TODO: Implement robust close (maybe press Escape via WM agent)
        self.type_keys("<Esc>")

    def get_item(self, name: str) -> Optional[UIMenuItem]:
        children = self.access_agent.get_children(self._native_obj)
        for child in children:
            # Check role first?
            # role = self.access_agent.get_role(child)
            # We can check names
            child_name = self.access_agent.get_name(child)
            if child_name == name:
                return LinuxMenuItem(child, self.access_agent, self.wm_agent, parent=self)
        return None

    def get_items(self) -> List[UIMenuItem]:
        items = []
        children = self.access_agent.get_children(self._native_obj)
        for child in children:
            items.append(LinuxMenuItem(child, self.access_agent, self.wm_agent, parent=self))
        return items


class LinuxMenuBar(LinuxElement, UIMenuBar):
    """ 
    Wrapper for Linux Menu Bar.
    Wait, base class is UIMenuBar.
    """
    # Note: I need to check valid inheritance order if mixins used.
    # LinuxElement first for implementation, UIMenuBar for interface.
    
    def __init__(self, native_obj: Any, access_agent: AccessibilityAgent, wm_agent: WindowManagerAgent, parent: Optional[UIElement] = None):
        super().__init__(native_obj, access_agent, wm_agent, parent=parent)

    def get_menu(self, name: str) -> Optional[UIMenu]:
        children = self.access_agent.get_children(self._native_obj)
        for child in children:
            if self.access_agent.get_name(child) == name:
                return LinuxMenu(child, self.access_agent, self.wm_agent, parent=self)
        return None

    def get_menus(self) -> List[UIMenu]:
        menus = []
        children = self.access_agent.get_children(self._native_obj)
        for child in children:
             menus.append(LinuxMenu(child, self.access_agent, self.wm_agent, parent=self))
        return menus


class LinuxDropDownMenu(LinuxMenu, UIDropDownMenu):
    """
    Wrapper for drop-down menus. Currently behaves identically to LinuxMenu
    but provides a specific type for mapping.
    """
    def __init__(self, native_obj: Any, access_agent: AccessibilityAgent, wm_agent: WindowManagerAgent, parent: Optional[UIElement] = None):
        super().__init__(native_obj, access_agent, wm_agent, parent=parent)
