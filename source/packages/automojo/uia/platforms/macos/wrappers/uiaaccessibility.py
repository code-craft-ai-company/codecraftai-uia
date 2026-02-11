from typing import Any, List, Optional, Tuple, TYPE_CHECKING

import time

import weakref

import re

from automojo.errors.exceptions import ConfigurationError
from automojo.uia.platforms.base import UIElement
from automojo.uia.exceptions import (
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
    except:
        # Accessibility Attribute Strings
        kAXVisibleAttribute = "AXVisible"
        kAXWindowsAttribute = "AXWindows"

        # Accessibility Value Type Enums
        kAXValueCGPointType = 1
        kAXValueCGSizeType = 2
except Exception as err:
    import traceback
    print(traceback.format_exc())
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
    from automojo.uia.platforms.macos.automation import MacOSAutomation

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

        width = getattr(size, "width", None)
        height = getattr(size, "height", None)
        if width is None:
            width = getattr(size, "x", 0.0)
        if height is None:
            height = getattr(size, "y", 0.0)

        x = position.x + (width / 2.0)
        y = position.y + (height / 2.0)

        return x, y

    def _get_bounds(self) -> Optional[Tuple[float, float, float, float]]:
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

        width = getattr(size, "width", None)
        height = getattr(size, "height", None)
        if width is None:
            width = getattr(size, "x", 0.0)
        if height is None:
            height = getattr(size, "y", 0.0)

        return (position.x, position.y, width, height)

    @property
    def name(self) -> str:
        value = ""

        found, title_value = self._copy_attribute(kAXTitleAttribute)
        if found is True and isinstance(title_value, str):
            value = title_value

        if value:
            return value

        found, identifier_value = self._copy_attribute(kAXIdentifierAttribute)
        if found is True and isinstance(identifier_value, str):
            return identifier_value

        return ""

    @property
    def role(self) -> str:
        found, value = self._copy_attribute(kAXRoleAttribute)
        if found is False:
            rtnval = ""
            return rtnval

        return value

    @property
    def role_name(self) -> str:
        rtnval = self.role
        return rtnval

    @property
    def title(self) -> str:
        rtnval = self.name
        return rtnval

    @property
    def identifier(self) -> str:
        """
            Returns the AXIdentifier attribute when available.
        """
        found, value = self._copy_attribute(kAXIdentifierAttribute)
        if found is False or isinstance(value, str) is False:
            return ""

        return value

    @property
    def help(self) -> str:
        """
            Returns the AXHelp attribute when available.
        """
        found, value = self._copy_attribute(kAXHelpAttribute)
        if found is False or isinstance(value, str) is False:
            return ""

        return value

    @property
    def is_visible(self) -> bool:
        found, value = self._copy_attribute(kAXVisibleAttribute)
        if found is False:
            errmsg = "The accessibility element does not expose visibility."
            raise NotImplementedError(errmsg)

        rtnval = bool(value)
        return rtnval

    @property
    def is_focused(self) -> bool:
        found, value = self._copy_attribute(kAXFocusedAttribute)
        if found is False:
             return False

        rtnval = bool(value)
        return rtnval

    @property
    def is_enabled(self) -> bool:
        found, value = self._copy_attribute(kAXEnabledAttribute)
        if found is False:
            errmsg = "The accessibility element does not expose enabled state."
            raise NotImplementedError(errmsg)

        rtnval = bool(value)
        return rtnval

    @property
    def is_focused(self) -> bool:
        found, value = self._copy_attribute(kAXFocusedAttribute)
        if found is False:
             # Fallback? No, just return False if not found/supported
             return False

        rtnval = bool(value)
        return rtnval

    @property
    def bounds(self) -> Tuple[float, float, float, float]:
        """
            Returns (x, y, width, height) bounding rectangle when available.
        """
        bounds = self._get_bounds()
        if bounds is None:
            rtnval = (0.0, 0.0, 0.0, 0.0)
            return rtnval

        return bounds

    @property
    def position(self) -> Tuple[float, float]:
        """
            Returns (x, y) position from the bounds.
        """
        bounds = self.bounds
        rtnval = (bounds[0], bounds[1])
        return rtnval

    @property
    def size(self) -> Tuple[float, float]:
        """
            Returns (width, height) size from the bounds.
        """
        bounds = self.bounds
        rtnval = (bounds[2], bounds[3])
        return rtnval

    def children(self) -> List["UiaAccessibilityElement"]:
        """
            Returns child accessibility elements.
        """
        found, value = self._copy_attribute(kAXChildrenAttribute)
        if found is False:
            rtn_list = []
            return rtn_list

        child_list = []
        for child in value:
            child_list.append(UiaAccessibilityElement(self.controller, child))

        return child_list

    def find_first_by_role(self, role: str, include_self: bool = False) -> Optional["UiaAccessibilityElement"]:
        """
            Finds the first element that matches the given role.

            :param role: The role to match.
            :param include_self: True to include this element in the search.

            :returns: The first matching element or None.
            :raises: ValueError
        """
        if role is None:
            errmsg = "The role parameter cannot be None."
            raise ValueError(errmsg)

        for element in self._iter_descendants(include_self=include_self):
            if element.role == role:
                return element

        return None

    def find_by_title(self, title: str, include_self: bool = False, expression: bool = False) -> List["UiaAccessibilityElement"]:
        """
            Finds all elements with a title that matches the given string.

            :param title: The title to match.
            :param include_self: True to include this element in the search.
            :param expression: True to treat the title as a regular expression.

            :returns: A list of matching elements.
            :raises: ValueError
        """
        if title is None:
            errmsg = "The title parameter cannot be None."
            raise ValueError(errmsg)

        matches = []
        for element in self._iter_descendants(include_self=include_self):
            candidate = element.title
            if expression:
                if candidate is not None:
                    if re.search(title, candidate) is not None:
                        matches.append(element)
            else:
                if candidate == title:
                    matches.append(element)

        return matches

    def find_by_tytle(self, title: str, include_self: bool = False, expression: bool = False) -> List["UiaAccessibilityElement"]:
        """
            Alias for find_by_title (spelling preserved for compatibility).
        """
        return self.find_by_title(title=title, include_self=include_self, expression=expression)

    def find_by_contents(self, contents: str, include_self: bool = False, expression: bool = False) -> List["UiaAccessibilityElement"]:
        """
            Finds all elements whose title or value contains the given string.

            :param contents: The substring to search for.
            :param include_self: True to include this element in the search.
            :param expression: True to treat the contents as a regular expression.

            :returns: A list of matching elements.
            :raises: ValueError
        """
        if contents is None:
            errmsg = "The contents parameter cannot be None."
            raise ValueError(errmsg)

        matches = []
        for element in self._iter_descendants(include_self=include_self):
            title = element.title
            value = element._get_value_text()

            if expression:
                if title is not None:
                    if re.search(contents, title) is not None:
                        matches.append(element)
                        continue

                if value is not None:
                    if re.search(contents, value) is not None:
                        matches.append(element)
            else:
                if title is not None:
                    if contents in title:
                        matches.append(element)
                        continue

                if value is not None:
                    if contents in value:
                        matches.append(element)

        return matches

    def _get_value_text(self) -> Optional[str]:
        if kAXValueAttribute is None:
            return None

        found, value = self._copy_attribute(kAXValueAttribute)
        if found is False:
            return None

        if isinstance(value, str) is False:
            return None

        return value

    def click(self) -> None:
        if self._perform_action(kAXPressAction):
            return

        center = self._get_center_point()
        if center is None:
            errmsg = "Unable to click the element. No press action or position available."
            raise NotImplementedError(errmsg)

        if CGEventCreateMouseEvent is None or CGEventPost is None:
            errmsg = "Quartz mouse event APIs are not available."
            raise NotImplementedError(errmsg)

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

    def find_element(self, **kwargs) -> Optional['UIElement']:
        """
        Finds the first child element matching criteria.
        Args:
            name (str): The name/label of the element (exact match)
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
            match = True
            if name and element.name != name:
                match = False
            if role and element.role != role:
                match = False
            
            if match:
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
            match = True
            if name and element.name != name:
                match = False
            if role and element.role != role:
                match = False
            
            if match:
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

