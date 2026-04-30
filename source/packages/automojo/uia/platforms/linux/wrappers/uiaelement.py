
import weakref
from typing import Any, Tuple, Optional, List
from automojo.uia.platforms.base import UIElement
from automojo.uia.platforms.linux.agents.linuxbaseagents import AccessibilityAgent, WindowManagerAgent
from automojo.uia.exceptions import (
    UIAException,
    ElementNotFoundError,
    InteractionError,
    PlatformNotSupportedError
)

class LinuxElement(UIElement):
    """
        Base wrapper for Linux UI elements using Agent Architecture.
    """
    def __init__(self, native_obj: Any, access_agent: AccessibilityAgent, wm_agent: WindowManagerAgent, parent: Optional[UIElement] = None):
        super().__init__(parent)
        self._native_obj = native_obj
        self._access_agent = weakref.ref(access_agent)
        self._wm_agent = weakref.ref(wm_agent) if wm_agent else None

    # ... (properties unchanged) ...
    @property
    def access_agent(self) -> AccessibilityAgent:
        return self._access_agent()

    @property
    def wm_agent(self) -> Optional[WindowManagerAgent]:
        if self._wm_agent:
            return self._wm_agent()
        return None

    @property
    def native_obj(self) -> Any:
        return self._native_obj

    @property
    def name(self) -> str:
        return self.access_agent.get_name(self._native_obj)

    @property
    def text(self) -> str:
        return self.access_agent.get_text(self._native_obj)

    @property
    def bounds(self) -> tuple:
        """Returns (x, y, width, height) bounding rectangle."""
        # 1. Get raw AT-SPI coordinates
        coords = self.access_agent.get_coordinates(self._native_obj)
        if not coords:
            return (0, 0, 0, 0)
            
        # 2. Check if we need to apply Wayland/Broker offset
        # This is required if we are on Gnome Wayland where AT-SPI returns window-relative(0,0) coords
        try:
            # We check if we are inside a LinuxWindow that has a different position than AT-SPI reports
            from automojo.uia.platforms.linux.wrappers.uiawindow import LinuxWindow
            
            # Find parent window
            parent = self.parent
            root_window = None
            while parent:
                if isinstance(parent, LinuxWindow):
                    root_window = parent
                    break
                parent = getattr(parent, 'parent', None)
            
            if root_window:
                # Get Window's "True" Position (Broker-based if available)
                win_true_pos = root_window.get_position() # (x, y)
                
                # Get Window's "Raw" AT-SPI Position
                # We access the raw agent method directly to avoid recursion/overrides
                win_atspi_coords = self.access_agent.get_coordinates(root_window.native_obj)
                if win_atspi_coords:
                    win_atspi_x, win_atspi_y = win_atspi_coords[0], win_atspi_coords[1]
                    
                    # Calculate Offset
                    delta_x = win_true_pos[0] - win_atspi_x
                    delta_y = win_true_pos[1] - win_atspi_y
                    
                    # Apply offset if significant (avoid minor jitter)
                    if abs(delta_x) > 1 or abs(delta_y) > 1:
                        return (coords[0] + delta_x, coords[1] + delta_y, coords[2], coords[3])

        except Exception as e:
            # print(f"Warning: Coordinate offset calculation failed: {e}")
            pass

        return coords

    @property
    def position(self) -> tuple:
        """Returns (x, y) position."""
        bounds = self.bounds
        return (bounds[0], bounds[1])

    @property
    def size(self) -> tuple:
        """Returns (width, height) size."""
        bounds = self.bounds
        return (bounds[2], bounds[3])

    @property
    def is_visible(self) -> bool:
        states = self.access_agent.get_states(self._native_obj)
        for state in states:
             if str(state) == "visible" or str(state).endswith("VISIBLE"):
                 return True
        return False

    @property
    def role(self) -> Any:
        return self.access_agent.get_role(self._native_obj)

    @property
    def role_name(self) -> str:
        return self.access_agent.get_role_name(self._native_obj)

    @property
    def is_enabled(self) -> bool:
        states = self.access_agent.get_states(self._native_obj)
        for state in states:
             if str(state) == "enabled" or str(state).endswith("ENABLED"):
                 return True
        return False
    
    def grab_focus(self) -> bool:
        try:
             component = self._native_obj.queryComponent()
             return component.grabFocus()
        except:
             pass
        return False

    def click(self) -> None:
        """
            Attempts to perform a click action via the Accessibility Agent (Action interface).
        """
        if self.access_agent.do_action(self._native_obj, 0):
             return
        
        # Fallback to WM click if coordinates available
        try:
            coords = self.access_agent.get_coordinates(self._native_obj)
            if coords:
                x, y, w, h = coords
                # Click center
                center_x = x + (w // 2)
                center_y = y + (h // 2)
                
                if self.wm_agent:
                    self.wm_agent.click(center_x, center_y)
                    return
        except Exception as e:
            raise InteractionError(f"Fallback click failed: {e}")

        raise InteractionError("Click action failed or not supported by this element.")

    def type_keys(self, keys: str) -> None:
        """
            Types keys using the Window Manager Agent.
        """
        if not self.wm_agent:
             raise PlatformNotSupportedError(
                 "Keyboard input requires X11 WM Agent. "
                 "On Wayland systems, X11 is not available."
             )
        
        self.grab_focus()
        try:
            self.wm_agent.send_keys(None, keys)
        except Exception as e:
            raise InteractionError(f"Failed to type keys: {e}")
        return

    def set_text(self, text: str) -> None:
        self.type_keys(text)
        return

    def _create_child_wrapper(self, native_child: Any) -> 'LinuxElement':
        """
            Creates a wrapper for a native child element using the Factory.
        """
        # late import to avoid circular dependency if factory imports LinuxElement at top level
        from automojo.uia.platforms.linux.wrappers.factory import LinuxWrapperFactory
        
        return LinuxWrapperFactory.create_wrapper(
            native_child, 
            self.access_agent, 
            self.wm_agent, 
            parent=self
        )

    def find_descendant(self, name: str = None, role:str = None, max_depth: int = 10) -> 'LinuxElement':
        # Alias specifically for internal/legacy use, delegates to find_element logic but recursive
        # Re-implementing using find_element logic is cleaner
        return self.find_element(name=name, role=role, recursive=True, max_depth=max_depth)

    def find_element(self, **kwargs) -> Optional['UIElement']:
        """
            Finds the first child element matching criteria.

            :param name: The name/label of the element
            :param role: The role name of the element
            :param recursive: Whether to search recursively (default: True)
            :param max_depth: Maximum depth for recursive search (default: 10)
        """
        name = kwargs.get('name')
        role = kwargs.get('role')
        recursive = kwargs.get('recursive', True)
        max_depth = kwargs.get('max_depth', 10)
        
        if recursive:
             return self._find_recursive(name, role, max_depth)
        
        # Immediate children search
        children = self.access_agent.get_children(self._native_obj)
        for child in children:
            child_wrapper = self._create_child_wrapper(child)
            if self._matches(child_wrapper, name, role):
                return child_wrapper
        return None

    def find_elements(self, **kwargs) -> List['UIElement']:
        """
            Finds all child elements matching criteria.
        """
        name = kwargs.get('name')
        role = kwargs.get('role')
        recursive = kwargs.get('recursive', True)
        max_depth = kwargs.get('max_depth', 10)
        
        found_elements = []
        if recursive:
             self._find_recursive_all(name, role, max_depth, found_elements)
        else:
            children = self.access_agent.get_children(self._native_obj)
            for child in children:
                child_wrapper = self._create_child_wrapper(child)
                if self._matches(child_wrapper, name, role):
                    found_elements.append(child_wrapper)
        return found_elements

    def _matches(self, element: 'LinuxElement', name: str, role: str) -> bool:
        if role and element.role_name != role:
            return False
            
        if name:
            el_name = element.name or ""
            if name.startswith('~'):
                if name[1:] not in el_name:
                    return False
            elif name.endswith('*'):
                 if not el_name.startswith(name[:-1]):
                     return False
            elif name.startswith('*'):
                 if not el_name.endswith(name[1:]):
                     return False
            elif element.name != name:
                return False
                
        return True

    def _find_recursive(self, name: str, role: str, depth: int) -> Optional['LinuxElement']:
        if depth < 0:
            return None
        
        children = self.access_agent.get_children(self._native_obj)
        for child in children:
            child_wrapper = self._create_child_wrapper(child)
            
            if self._matches(child_wrapper, name, role):
                return child_wrapper
            
            # Recurse only if not found (DFS)
            # Optimization: If child is a table, should we search inside it via recursion?
            # Yes, standard behavior.
            
            # Note: We must call internal _find_recursive to avoid re-wrapping if possible?
            # But _find_recursive is on instance.
            
            found = child_wrapper._find_recursive(name, role, depth - 1)
            if found:
                return found
        return None

    def _find_recursive_all(self, name: str, role: str, depth: int, results: List['LinuxElement']):
        if depth < 0:
            return
            
        children = self.access_agent.get_children(self._native_obj)
        for child in children:
            child_wrapper = self._create_child_wrapper(child)
            
            if self._matches(child_wrapper, name, role):
                results.append(child_wrapper)
            
            child_wrapper._find_recursive_all(name, role, depth - 1, results)
        return

    def set_value(self, value: float) -> None:
        """
            Sets a numeric value on an element using the Value interface.
        """
        try:
            value_iface = self._native_obj.queryValue()
            if value_iface:
                value_iface.currentValue = value
        except Exception as e:
            print(f"Error setting value: {e}")
        return

    def drag_to(self, end_x: int, end_y: int, duration: float = 0.5) -> None:
        """
            Drags from the center of this element to the specified coordinates.
        """
        if not self.wm_agent:
            raise NotImplementedError("Drag/drop requires Window Manager Agent")
            
        # calculate center
        rect = self.bounds
        start_x = rect[0] + rect[2] // 2
        start_y = rect[1] + rect[3] // 2
        
        self.wm_agent.drag_and_drop(start_x, start_y, end_x, end_y, duration)
        return
    
    def __repr__(self) -> str:
        return f"LinuxElement<{self.name}>"
