
import os

from typing import Any, List
try:
    import pyatspi
except ImportError:
    pyatspi = None

from ccai.uia.exceptions import InteractionError
from ccai.uia.platforms.linux.agents.linuxbaseagents import AccessibilityAgent

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
                # Applications that exit while the desktop is enumerated leave defunct children; skip them.
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
            # Elements without a working Action interface report failure through the False return value,
            # which lets callers such as LinuxElement.click() fall back to a coordinate click.
            pass
        return False
    
    def get_value(self, element: Any) -> float:
        try:
            value_iface = element.queryValue()
            return float(value_iface.currentValue)
        except Exception:
            return 0.0

    def set_value(self, element: Any, value: float) -> None:
        """
            Sets the numeric value of a value-bearing element through the AT-SPI Value interface.

            :param element: The native accessible whose value is set.
            :param value: The value to set.

            :raises: InteractionError when the element does not provide the Value interface or the
                     value cannot be assigned.
        """
        float_value = float(value)
        try:
            value_iface = element.queryValue()
            value_iface.currentValue = float_value
        except Exception as xcpt:
            element_name = self.get_name(element)
            element_role = self.get_role_name(element)

            err_msg_lines = [
                "Failed to set the value of an accessible element through the AT-SPI Value interface."
            ]
            err_msg_lines.append("ELEMENT:")
            err_msg_lines.append("    name: {}".format(element_name))
            err_msg_lines.append("    role: {}".format(element_role))
            err_msg_lines.append("VALUE: {}".format(float_value))
            err_msg_lines.append("CAUSE: {}: {}".format(type(xcpt).__name__, xcpt))
            err_msg = os.linesep.join(err_msg_lines)
            raise InteractionError(err_msg) from xcpt
        return

    def get_coordinates(self, element: Any) -> tuple:
        try:
             component = element.queryComponent()
             # 0 is DESKTOP_COORDS
             extents = component.getExtents(0)
             return (extents.x, extents.y, extents.width, extents.height)
        except Exception:
             return None
