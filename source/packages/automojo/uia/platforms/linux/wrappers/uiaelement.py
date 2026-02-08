
import weakref
from typing import Any, Tuple, Optional
from automojo.uia.platforms.base import UIElement
from automojo.uia.platforms.linux.agents.linuxbaseagents import AccessibilityAgent, WindowManagerAgent

class LinuxElement(UIElement):
    """
    Base wrapper for Linux UI elements using Agent Architecture.
    """
    def __init__(self, native_obj: Any, access_agent: AccessibilityAgent, wm_agent: WindowManagerAgent, parent: Optional[UIElement] = None):
        super().__init__(parent)
        self._native_obj = native_obj
        self._access_agent = weakref.ref(access_agent)
        self._wm_agent = weakref.ref(wm_agent) if wm_agent else None

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
        coords = self.access_agent.get_coordinates(self._native_obj)
        if coords:
            return coords
        return (0, 0, 0, 0)

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
        # We need to check if 'visible' state is present. 
        # The agent returns list of states, we check string representation or object
        # PyAtspi states are objects, let's assume agent handles conversion or we check name
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
        # Try accessibility layer focus first (often works for widgets)
        try:
             component = self._native_obj.queryComponent()
             return component.grabFocus()
        except:
             pass
             
        # Use WM agent if it's a window or we can find the window
        # This is a bit tricky for individual elements.
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
            print(f"Fallback click failed: {e}")
            pass

        raise NotImplementedError("Click action failed or not supported by this element.")

    def type_keys(self, keys: str) -> None:
        """
            Types keys using the Window Manager Agent.
            Note: Requires X11. On Wayland systems, this will fail gracefully.
        """
        if not self.wm_agent:
             raise NotImplementedError(
                 "Keyboard input requires X11 WM Agent. "
                 "On Wayland systems, X11 is not available. "
                 "Consider using set_text() fallback or AT-SPI EditableText if supported."
             )
        
        # We need to ensure focus first.
        self.grab_focus()
        
        # Delegate to WM agent. 
        # Note: WM Agent usually takes a window handle or name, but our X11 agent implementation
        # currently behaves globally or takes a window object.
        # For X11Agent, we pass the element's window if possible, or just let it type globally
        # assuming focus is set.
        self.wm_agent.send_keys(None, keys)

    def set_text(self, text: str) -> None:
        # Try EditableText interface via Accessibility Agent?
        # For now, simplistic fallback
        self.type_keys(text)

    def find_descendant(self, name: str = None, role:str = None, max_depth: int = 10) -> 'LinuxElement':
        if max_depth < 0:
            return None
        
        children = self.access_agent.get_children(self._native_obj)
        for child in children:
            child_wrapper = LinuxElement(child, self.access_agent, self.wm_agent, parent=self)
            
            match = True
            if name and child_wrapper.name != name:
                match = False
            
            if role and child_wrapper.role_name != role:
                match = False
            
            if match:
                return child_wrapper
            
            found = child_wrapper.find_descendant(name, role, max_depth - 1)
            if found:
                return found
                 
        return None

    def set_value(self, value: float) -> None:
        """Sets a numeric value on an element using the Value interface."""
        try:
            value_iface = self._native_obj.queryValue()
            if value_iface:
                value_iface.currentValue = value
        except Exception as e:
            print(f"Error setting value: {e}")
    
    def __repr__(self) -> str:
        return f"LinuxElement<{self.name}>"
