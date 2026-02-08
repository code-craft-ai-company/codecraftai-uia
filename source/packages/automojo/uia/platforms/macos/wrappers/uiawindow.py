from typing import Any, List, Tuple, TYPE_CHECKING

from automojo.uia.platforms.base import UIWindow
from automojo.uia.platforms.macos.wrappers.wrappedobject import WrappedObject
from automojo.uia.exceptions import (
    UIAException,
    ElementNotFoundError,
    InteractionError,
    PlatformNotSupportedError
)

if TYPE_CHECKING:
    from automojo.uia.platforms.macos.automation import MacOSAutomation


class UiaWindow(WrappedObject, UIWindow):
    """
        Wrapper for a window object. This represents a window as a UI element,
        distinct from the application process that owns it.
    """

    def __init__(self, controller: "MacOSAutomation", native_obj: Any):
        super().__init__(controller, native_obj)
        return

    def __repr__(self) -> str:
        title = None

        try:
            title = self.title
        except NotImplementedError:
            title = "Unknown"

        sval = f"UiaWindow< {title} >"
        return sval

    def _resolve_target(self) -> Any:
        target = self._native_obj

        if hasattr(target, "native_obj"):
            target = target.native_obj

        return target

    def _try_get_native_value(self, attr_name: str) -> Tuple[bool, Any]:
        if hasattr(self._native_obj, attr_name):
            attr = getattr(self._native_obj, attr_name)
            if callable(attr):
                value = attr()
            else:
                value = attr

            return True, value

        target = self._resolve_target()

        if hasattr(target, attr_name) is False:
            return False, None

        attr = getattr(target, attr_name)
        if callable(attr):
            value = attr()
        else:
            value = attr

        return True, value

    def _call_native_method(self, method_names: List[str]) -> bool:
        target = self._resolve_target()

        for method_name in method_names:
            if hasattr(target, method_name) is False:
                continue

            method = getattr(target, method_name)
            if callable(method) is False:
                continue

            method()
            return True

        return False

    @property
    def name(self) -> str:
        rtnval = self.title
        return rtnval

    @property
    def title(self) -> str:
        found, value = self._try_get_native_value("name")
        if found is False:
            found, value = self._try_get_native_value("title")

        if found is False:
            errmsg = "The native window does not expose a title or name."
            raise PlatformNotSupportedError(errmsg)

        return value

    @property
    def is_visible(self) -> bool:
        found, value = self._try_get_native_value("visible")
        if found is False:
            found, value = self._try_get_native_value("isVisible")

        if found is False:
            errmsg = "The native window does not expose visibility."
            raise PlatformNotSupportedError(errmsg)

        rtnval = bool(value)
        return rtnval

    @property
    def is_enabled(self) -> bool:
        found, value = self._try_get_native_value("enabled")
        if found is False:
            found, value = self._try_get_native_value("isEnabled")

        if found is False:
            errmsg = "The native window does not expose enabled state."
            raise PlatformNotSupportedError(errmsg)

        rtnval = bool(value)
        return rtnval

    def click(self) -> None:
        if hasattr(self._native_obj, "click"):
            self._native_obj.click()
            return

        errmsg = "Click is not supported for window objects."
        raise NotImplementedError(errmsg)

    def type_keys(self, keys: str) -> None:
        if hasattr(self._native_obj, "type_keys"):
            self._native_obj.type_keys(keys)
            return

        errmsg = "Type keys is not supported for window objects."
        raise NotImplementedError(errmsg)

    def focus(self) -> None:
        """
            Sets focus on the window when supported.
        """
        if hasattr(self._native_obj, "focus"):
            self._native_obj.focus()
            return

        if hasattr(self._native_obj, "click"):
            self._native_obj.click()
            return

        errmsg = "Focus is not supported for this window object."
        raise NotImplementedError(errmsg)

    def close(self) -> None:
        method_names = ["close", "performClose", "performClose_"]
        if self._call_native_method(method_names) is False:
            errmsg = "Close is not supported for this window object."
            raise PlatformNotSupportedError(errmsg)

        return

    def maximize(self) -> None:
        method_names = ["zoom", "performZoom", "performZoom_"]
        if self._call_native_method(method_names) is False:
            errmsg = "Maximize is not supported for this window object."
            raise PlatformNotSupportedError(errmsg)

        return

    def minimize(self) -> None:
        method_names = ["minimize", "miniaturize", "performMiniaturize", "performMiniaturize_"]
        if self._call_native_method(method_names) is False:
            errmsg = "Minimize is not supported for this window object."
            raise PlatformNotSupportedError(errmsg)

        return

    def restore(self) -> None:
        method_names = ["deminiaturize", "performDeminiaturize", "performDeminiaturize_"]
        if self._call_native_method(method_names) is False:
            errmsg = "Restore is not supported for this window object."
            raise PlatformNotSupportedError(errmsg)

        return

    def is_minimized(self) -> bool:
        """
            Indicates if the window is minimized when supported.
        """
        found, value = self._try_get_native_value("minimized")
        if found is False:
            found, value = self._try_get_native_value("isMinimized")

        if found is False:
            errmsg = "The native window does not expose minimized state."
            raise PlatformNotSupportedError(errmsg)

        rtnval = bool(value)
        return rtnval

    def is_focused(self) -> bool:
        """
            Indicates if the window is focused when supported.
        """
        found, value = self._try_get_native_value("focused")
        if found is False:
            found, value = self._try_get_native_value("isFocused")

        if found is False:
            found, value = self._try_get_native_value("isMain")

        if found is False:
            errmsg = "The native window does not expose focused state."
            raise PlatformNotSupportedError(errmsg)

        rtnval = bool(value)
        return rtnval

    def find_first_by_role(self, role: str, include_self: bool = False):
        """
            Finds the first element matching a role when Accessibility is available.
        """
        if hasattr(self._native_obj, "find_first_by_role"):
            return self._native_obj.find_first_by_role(role=role, include_self=include_self)

        return None

    def find_by_title(self, title: str, include_self: bool = False, expression: bool = False):
        """
            Finds elements by title when Accessibility is available.
        """
        if hasattr(self._native_obj, "find_by_title"):
            return self._native_obj.find_by_title(title=title, include_self=include_self, expression=expression)

        return []

    def find_by_tytle(self, title: str, include_self: bool = False, expression: bool = False):
        """
            Alias for find_by_title (spelling preserved for compatibility).
        """
        if hasattr(self._native_obj, "find_by_tytle"):
            return self._native_obj.find_by_tytle(title=title, include_self=include_self, expression=expression)

        return []

    def find_by_contents(self, contents: str, include_self: bool = False, expression: bool = False):
        """
            Finds elements by contents when Accessibility is available.
        """
        if hasattr(self._native_obj, "find_by_contents"):
            return self._native_obj.find_by_contents(contents=contents, include_self=include_self, expression=expression)

        return []

    def send_keys(self, keys: str) -> None:
        """
            Focuses the window and sends keys to the focused control.
        """
        self.focus()
        self.type_keys(keys)
        return
