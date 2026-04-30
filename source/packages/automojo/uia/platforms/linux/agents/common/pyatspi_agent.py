
from typing import Any, List
try:
    import pyatspi
except ImportError:
    pyatspi = None

from automojo.uia.platforms.linux.agents.linuxbaseagents import AccessibilityAgent

class PyAtspiAccessibilityAgent(AccessibilityAgent):
    """
    Concrete implementation of AccessibilityAgent using PyAtspi.
    """
    def __init__(self):
        if not pyatspi:
             raise ImportError("PyAtspi is not installed.")
        self._registry = pyatspi.Registry

    def get_root(self) -> Any:
        return self._registry.getDesktop(0)

    def get_application_by_name(self, name: str) -> Any:
        desktop = self.get_root()
        for i in range(desktop.childCount):
            try:
                child = desktop.getChildAtIndex(i)
                if child.name == name:
                    return child
            except Exception:
                pass
        return None

    def get_role(self, element: Any) -> Any:
        try:
             return element.getRole()
        except Exception:
             return None

    def get_role_name(self, element: Any) -> str:
        try:
             return element.getRoleName()
        except Exception:
             return "Unknown"

    def get_name(self, element: Any) -> str:
        try:
            return element.name
        except Exception:
            return ""

    def get_text(self, element: Any) -> str:
        try:
            text_iface = element.queryText()
            return text_iface.getText(0, -1)
        except Exception:
            pass
            
        try:
            value_iface = element.queryValue()
            return str(value_iface.currentValue)
        except Exception:
            pass
            
        return ""


    def get_children(self, element: Any) -> List[Any]:
        children = []
        try:
             count = element.childCount
             # print(f"DEBUG: Getting children for {self.get_name(element)} (Role: {self.get_role_name(element)}), Count: {count}")
             for i in range(count):
                 try:
                     child = element.getChildAtIndex(i)
                     children.append(child)
                 except Exception as e:
                     print(f"Error getting child at index {i}: {e}")
        except Exception as e:
             print(f"Error getting child count: {e}")
        return children

    def get_states(self, element: Any) -> List[Any]:
        try:
             return element.getState().getStates()
        except Exception:
             return []

    def do_action(self, element: Any, action_index: int) -> bool:
        try:
            action = element.queryAction()
            if action.nActions > action_index:
                action.doAction(action_index)
                return True
        except Exception:
            pass
        return False
    
    def get_value(self, element: Any) -> float:
        try:
            value_iface = element.queryValue()
            return float(value_iface.currentValue)
        except Exception:
            return 0.0

    def set_value(self, element: Any, value: float) -> None:
        try:
            value_iface = element.queryValue()
            value_iface.currentValue = float(value)
        except Exception:
            pass
        return

    def get_coordinates(self, element: Any) -> tuple:
        try:
             component = element.queryComponent()
             # 0 is DESKTOP_COORDS
             extents = component.getExtents(0)
             return (extents.x, extents.y, extents.width, extents.height)
        except Exception:
             return None
