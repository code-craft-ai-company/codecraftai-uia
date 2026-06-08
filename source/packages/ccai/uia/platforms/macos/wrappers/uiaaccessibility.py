from typing import Any, List, Optional, Tuple, TYPE_CHECKING

import time

import weakref

import re

from ccai.uia.platforms.base import UIElement
from ccai.uia.exceptions import (
    ConfigurationError,
    UIAException,
    ElementNotFoundError,
    InteractionError,
    PlatformNotSupportedError
)
try:
    from ApplicationServices import (
        AXIsProcessTrusted,
        AXIsProcessTrustedWithOptions,
        AXUIElementCreateApplication,
        AXUIElementCopyAttributeValue,
        AXUIElementSetAttributeValue,
        AXUIElementPerformAction,
        AXValueGetValue,
        kAXChildrenAttribute,
        kAXEnabledAttribute,
        kAXErrorSuccess,
        kAXFocusedAttribute,
        kAXTrustedCheckOptionPrompt,
        kAXPositionAttribute,
        kAXPressAction,
        kAXRaiseAction,
        kAXRoleAttribute,
        kAXSizeAttribute,
        kAXTitleAttribute,
        kAXIdentifierAttribute,
        kAXHelpAttribute,
        kAXValueAttribute,
    )
    try:
        from HIServices import (
            kAXVisibleAttribute,
            kAXWindowsAttribute,
            kAXValueCGPointType,
            kAXValueCGSizeType
        )
    except ImportError:
        # Accessibility Attribute Strings
        kAXVisibleAttribute = "AXVisible"
        kAXWindowsAttribute = "AXWindows"

        # Accessibility Value Type Enums
        kAXValueCGPointType = 1
        kAXValueCGSizeType = 2
except ImportError:
    AXIsProcessTrusted = None
    AXIsProcessTrustedWithOptions = None
    AXUIElementCreateApplication = None
    AXUIElementCopyAttributeValue = None
    AXUIElementSetAttributeValue = None
    AXUIElementPerformAction = None
    AXValueGetValue = None
    kAXChildrenAttribute = None
    kAXEnabledAttribute = None
    kAXErrorSuccess = 0
    kAXFocusedAttribute = None
    kAXTrustedCheckOptionPrompt = None
    kAXPositionAttribute = None
    kAXPressAction = None
    kAXRaiseAction = None
    kAXRoleAttribute = None
    kAXSizeAttribute = None
    kAXTitleAttribute = None
    kAXIdentifierAttribute = None
    kAXHelpAttribute = None
    kAXValueAttribute = None
    kAXVisibleAttribute = None
    kAXWindowsAttribute = None
    kAXValueCGPointType = None
    kAXValueCGSizeType = None

try:
    from Quartz import (
        CGEventCreateKeyboardEvent,
        CGEventKeyboardSetUnicodeString,
        CGEventCreateMouseEvent,
        CGEventPost,
        CGPointMake,
        CGSizeMake,
        kCGEventKeyDown,
        kCGEventKeyUp,
        kCGEventLeftMouseDown,
        kCGEventLeftMouseUp,
        kCGHIDEventTap,
        kCGMouseButtonLeft
    )
except Exception:
    CGEventCreateKeyboardEvent = None
    CGEventKeyboardSetUnicodeString = None
    CGEventCreateMouseEvent = None
    CGEventPost = None
    CGPointMake = None
    CGSizeMake = None
    kCGEventKeyDown = None
    kCGEventKeyUp = None
    kCGEventLeftMouseDown = None
    kCGEventLeftMouseUp = None
    kCGHIDEventTap = None
    kCGMouseButtonLeft = None

if TYPE_CHECKING:
    from ccai.uia.platforms.macos.automation import MacOSAutomation

AX_SUCCESS = kAXErrorSuccess if kAXErrorSuccess is not None else 0


def is_accessibility_trusted(prompt: bool = False) -> bool:
    """
        Checks whether the process is trusted for Accessibility access.

        :param prompt: True to request the system to show the Accessibility prompt.

        :returns: True if the process is trusted, False otherwise.
    """
    if AXIsProcessTrustedWithOptions is not None:
        if prompt:
            if kAXTrustedCheckOptionPrompt is None:
                options = {}
            else:
                options = {kAXTrustedCheckOptionPrompt: True}
        else:
            options = {}

        trusted = AXIsProcessTrustedWithOptions(options)
        return bool(trusted)

    if AXIsProcessTrusted is not None:
        trusted = AXIsProcessTrusted()
        return bool(trusted)

    return False


def require_accessibility_trusted(prompt: bool = False) -> None:
    """
        Ensures the process is trusted for Accessibility access.

        :param prompt: True to request the system to show the Accessibility prompt.

        :raises: PermissionError
    """
    if is_accessibility_trusted(prompt=prompt) is False:
        errmsg_lines = [
            "Accessibility permissions are not enabled for this process.",
            "Enable permissions in System Settings > Privacy & Security > Accessibility.",
            "Then restart the automation process."
        ]
        errmsg = " ".join(errmsg_lines)
        raise ConfigurationError(errmsg)

    return


def send_keys_to_focused(keys: str) -> None:
    """
        Sends a key stream through the system so input lands on the focused control.

        :param keys: The key stream to send.

        :raises: ValueError
        :raises: NotImplementedError
    """
    if keys is None:
        errmsg = "The keys parameter cannot be None."
        raise ValueError(errmsg)

    if CGEventCreateKeyboardEvent is None or CGEventPost is None:
        errmsg = "Quartz keyboard event APIs are not available."
        raise NotImplementedError(errmsg)

    for ch in keys:
        key_down = CGEventCreateKeyboardEvent(None, 0, True)
        CGEventKeyboardSetUnicodeString(key_down, 1, ch)
        CGEventPost(kCGHIDEventTap, key_down)

        key_up = CGEventCreateKeyboardEvent(None, 0, False)
        CGEventKeyboardSetUnicodeString(key_up, 1, ch)
        CGEventPost(kCGHIDEventTap, key_up)

    return


class UiaAccessibilityElement(UIElement):
    """
        Wrapper for an Accessibility element. This provides low level interactions
        like click and type keys when the element supports accessibility actions.
    """

    def __init__(self, controller: "MacOSAutomation", native_obj: Any):
        self._controller_ref = weakref.ref(controller)
        self._native_obj = native_obj
        return

    @property
    def controller(self) -> "MacOSAutomation":
        return self._controller_ref()

    @property
    def native_obj(self) -> Any:
        return self._native_obj

    def __repr__(self) -> str:
        title = ""

        try:
            title = self.title
        except NotImplementedError:
            title = "Unknown"

        sval = f"UiaAccessibilityElement< {title} >"
        return sval

    def _copy_attribute(self, attribute_name: str) -> Tuple[bool, Any]:
        if AXUIElementCopyAttributeValue is None:
            return False, None

        result = AXUIElementCopyAttributeValue(self._native_obj, attribute_name, None)

        if isinstance(result, tuple) and len(result) == 2:
            err, value = result
        else:
            err = AX_SUCCESS
            value = result

        if err != AX_SUCCESS:
            return False, None

        return True, value

    def _set_attribute(self, attribute_name: str, value: Any) -> bool:
        if AXUIElementSetAttributeValue is None:
            return False

        err = AXUIElementSetAttributeValue(self._native_obj, attribute_name, value)
        if err != AX_SUCCESS:
            return False

        return True

    def _perform_action(self, action_name: str) -> bool:
        if AXUIElementPerformAction is None:
            return False

        err = AXUIElementPerformAction(self._native_obj, action_name)
        if err != AX_SUCCESS:
            return False

        return True

    def _iter_descendants(self, include_self: bool = False):
        if include_self:
            queue = [self]
        else:
            queue = self.children()

        idx = 0
        while idx < len(queue):
            current = queue[idx]
            idx += 1

            child_list = current.children()
            for child in child_list:
                queue.append(child)

            yield current

    def _get_center_point(self) -> Optional[Tuple[float, float]]:
        if AXValueGetValue is None:
            return None

        found, position_value = self._copy_attribute(kAXPositionAttribute)
        if found is False:
            return None

        found, size_value = self._copy_attribute(kAXSizeAttribute)
        if found is False:
            return None

        if CGPointMake is None or CGSizeMake is None:
            return None

        # valid output pointers found through inspection: None needed
        ok_pos, position = AXValueGetValue(position_value, kAXValueCGPointType, None)
        ok_size, size = AXValueGetValue(size_value, kAXValueCGSizeType, None)

        if ok_pos is False or ok_size is False:
            return None
        super().__init__(controller, native_obj)
        return

    @property
    def role(self) -> str:
        error, value = ApplicationServices.AXUIElementCopyAttributeValue(self._native_obj, "AXRole", None)
        if error == 0:
            return value
        return ""

    @property
    def subrole(self) -> str:
        error, value = ApplicationServices.AXUIElementCopyAttributeValue(self._native_obj, "AXSubrole", None)
        if error == 0:
            return value
        return ""

    @property
    def title(self) -> str:
        error, value = ApplicationServices.AXUIElementCopyAttributeValue(self._native_obj, "AXTitle", None)
        if error == 0:
            return value
        return ""

    @property
    def name(self) -> str:
        # AXTitle is usually the name
        return self.title

    @property
    def value(self) -> Any:
        error, value = ApplicationServices.AXUIElementCopyAttributeValue(self._native_obj, "AXValue", None)
        if error == 0:
            return value
        return None

    @property
    def help(self) -> str:
        error, value = ApplicationServices.AXUIElementCopyAttributeValue(self._native_obj, "AXHelp", None)
        if error == 0:
            return value
        return ""

    @property
    def is_enabled(self) -> bool:
        error, value = ApplicationServices.AXUIElementCopyAttributeValue(self._native_obj, "AXEnabled", None)
        if error == 0:
            return bool(value)
        return False

    @property
    def is_visible(self) -> bool:
        # AX API doesn't have a direct "IsVisible" property usually,
        # but we can check if it has a size/position or not hidden.
        # Often checks if it is in the view hierarchy or not.
        return True # Default to true for AX elements if we can reference them

    @property
    def is_focused(self) -> bool:
        error, value = ApplicationServices.AXUIElementCopyAttributeValue(self._native_obj, "AXFocused", None)
        if error == 0:
             return bool(value)
        return False

    @property
    def position(self) -> Tuple[int, int]:
        error, value = ApplicationServices.AXUIElementCopyAttributeValue(self._native_obj, "AXPosition", None)
        if error == 0:
            # value is a CGPoint structure wrapped
            # In PyObjC/Quartz it might come back as a point object or tuple
            # Assuming it handles the conversion to something usable
            return (int(value.x), int(value.y))
        return (0, 0)

    @property
    def size(self) -> Tuple[int, int]:
        error, value = ApplicationServices.AXUIElementCopyAttributeValue(self._native_obj, "AXSize", None)
        if error == 0:
            return (int(value.width), int(value.height))
        return (0, 0)

    @property
    def bounds(self) -> Tuple[int, int, int, int]:
        pos = self.position
        sz = self.size
        return (pos[0], pos[1], sz[0], sz[1])

    def click(self) -> None:

        x, y = center
        point = CGPointMake(x, y)

        down_event = CGEventCreateMouseEvent(None, kCGEventLeftMouseDown, point, kCGMouseButtonLeft)
        up_event = CGEventCreateMouseEvent(None, kCGEventLeftMouseUp, point, kCGMouseButtonLeft)

        CGEventPost(kCGHIDEventTap, down_event)
        CGEventPost(kCGHIDEventTap, up_event)

        return

    def focus(self) -> None:
        """
            Sets focus on this element without a click when possible.
        """
        if kAXFocusedAttribute is not None:
            if self._set_attribute(kAXFocusedAttribute, True):
                return

        if kAXRaiseAction is not None:
            if self._perform_action(kAXRaiseAction):
                return

        raise InteractionError("Unable to focus the element.")

    def type_keys(self, keys: str) -> None:
        try:
            send_keys_to_focused(keys)
        except Exception as e:
            raise InteractionError(f"Failed to type keys: {e}")

        return

    def _matches(self, element: 'UiaAccessibilityElement', name: str, role: str) -> bool:
        if role and element.role != role:
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

    def find_element(self, **kwargs) -> Optional['UIElement']:
        """
        Finds the first child element matching criteria.
        Args:
            name (str): The name/label of the element (supports wildcards *, ~)
            role (str): The role of the element
            recursive (bool): Whether to search recursively (default: True)
        """
        name = kwargs.get('name')
        role = kwargs.get('role')
        recursive = kwargs.get('recursive', True)
        
        # Reuse existing iterator
        # include_self=False by default for children search
        iterator = self._iter_descendants(include_self=False) if recursive else self.children()
        
        for element in iterator:
            if self._matches(element, name, role):
                return element
                
        return None

    def find_elements(self, **kwargs) -> List['UIElement']:
        """
        Finds all child elements matching criteria.
        """
        name = kwargs.get('name')
        role = kwargs.get('role')
        recursive = kwargs.get('recursive', True)
        
        iterator = self._iter_descendants(include_self=False) if recursive else self.children()
        
        matches = []
        for element in iterator:
            if self._matches(element, name, role):
                matches.append(element)
                
        return matches

class UiaAccessibilityApplication:
    """
        Accessibility wrapper for an application process.
    """

    def __init__(self, controller: "MacOSAutomation", process_identifier: int):
        self._controller_ref = weakref.ref(controller)
        self._process_identifier = process_identifier
        self._ax_app = None
        return

    @property
    def controller(self) -> "MacOSAutomation":
        return self._controller_ref()

    @property
    def process_identifier(self) -> int:
        return self._process_identifier

    @property
    def ax_app(self) -> Any:
        if self._ax_app is None:
            require_accessibility_trusted(prompt=False)

            if AXUIElementCreateApplication is None:
                errmsg = "Accessibility APIs are not available."
                raise PlatformNotSupportedError(errmsg)

            self._ax_app = AXUIElementCreateApplication(self._process_identifier)

        return self._ax_app

    def root_element(self) -> UiaAccessibilityElement:
        """
            Returns the root accessibility element for the application.
        """
        element = UiaAccessibilityElement(self.controller, self.ax_app)
        return element

    def find_first_by_role(self, role: str, include_self: bool = False) -> Optional[UiaAccessibilityElement]:
        """
            Finds the first element that matches the given role.
        """
        root = self.root_element()
        found = root.find_first_by_role(role=role, include_self=include_self)
        if found is None and role == "AXWindow":
            windows = self.windows()
            if len(windows) > 0:
                return windows[0]

        return found

    def find_by_title(self, title: str, include_self: bool = False, expression: bool = False) -> List[UiaAccessibilityElement]:
        """
            Finds all elements whose title matches the given string.
        """
        root = self.root_element()
        return root.find_by_title(title=title, include_self=include_self, expression=expression)

    def find_by_tytle(self, title: str, include_self: bool = False, expression: bool = False) -> List[UiaAccessibilityElement]:
        """
            Alias for find_by_title (spelling preserved for compatibility).
        """
        root = self.root_element()
        return root.find_by_tytle(title=title, include_self=include_self, expression=expression)

    def find_by_contents(self, contents: str, include_self: bool = False, expression: bool = False) -> List[UiaAccessibilityElement]:
        """
            Finds all elements whose title or value contains the given string.
        """
        root = self.root_element()
        return root.find_by_contents(contents=contents, include_self=include_self, expression=expression)

    def get_focus_window(self) -> Optional[UiaAccessibilityElement]:
        """
            Returns the focused window of the application.
        """
        found, value = self._copy_attribute(self.ax_app, "AXFocusedWindow")
        if found is True and value is not None:
             return UiaAccessibilityElement(self.controller, value)
        
        return None

    def windows(self) -> List[UiaAccessibilityElement]:
        """
            Returns accessibility window elements for the application.

            :returns: A list of accessibility window elements.
        """
        window_list = []
        max_attempts = 6
        for attempt in range(max_attempts):
            window_list = []
            found, value = self._copy_attribute(self.ax_app, kAXWindowsAttribute)
            if found is True and value is not None:
                for wobj in value:
                    window_list.append(UiaAccessibilityElement(self.controller, wobj))

            focused_found, focused_value = self._copy_attribute(self.ax_app, "AXFocusedWindow")
            if focused_found is True and focused_value is not None:
                already_listed = False
                for window in window_list:
                    if window.native_obj is focused_value or window.native_obj == focused_value:
                        already_listed = True
                        break
                if already_listed is False:
                    window_list.append(UiaAccessibilityElement(self.controller, focused_value))

            if len(window_list) > 0:
                return window_list

            if attempt < max_attempts - 1:
                time.sleep(0.25)

        return window_list

    def _copy_attribute(self, obj: Any, attribute_name: str) -> Tuple[bool, Any]:
        if AXUIElementCopyAttributeValue is None:
            return False, None

        result = AXUIElementCopyAttributeValue(obj, attribute_name, None)

        if isinstance(result, tuple) and len(result) == 2:
            err, value = result
        else:
            err = AX_SUCCESS
            value = result

        if err != AX_SUCCESS:
            return False, None

        return True, value

