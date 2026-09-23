
from typing import Any, List, Optional, TYPE_CHECKING

import AppKit

from ccai.uia.platforms.base import UIApplication, UIWindow, UIElement
from ccai.uia.platforms.macos.wrappers.sbwindow import SbWindow
from ccai.uia.platforms.macos.wrappers.uiaaccessibility import (
    UiaAccessibilityApplication,
    is_accessibility_trusted,
    send_keys_to_focused
)
from ccai.uia.exceptions import (
    InteractionError,
    ConfigurationError,
)
from ccai.uia.platforms.macos.wrappers.uiawindow import MacWindow
from ccai.uia.platforms.macos.wrappers.wrappedobject import WrappedObject

from ccai.uia.platforms.macos.wrappers.uiaicon import MacIcon


if TYPE_CHECKING:
    from ccai.uia.platforms.macos.automation import MacOSAutomation

class MacApplication(WrappedObject, UIApplication):
    """
        Wrapper for an application process. Use this object to attach to and
        communicate with the application process; window objects are exposed
        separately via window wrappers.
    """

    APPLICATION_NAME = "NotSet"
    BUNDLE_IDENTIFIER = "NotSet"

    def __init__(self, controller: "MacOSAutomation", native_obj: Any):
        super().__init__(controller, native_obj)

        self._sb_process = None
        self._ax_app = None
        # declarative_model initialized in base class
        return

    def get_focus_window(self) -> 'MacWindow':
        """
        Returns the currently focused window of the application.
        """
        try:
            # Try to get the focused window via accessibility
            focused_window = self.accessibility.get_focus_window()
            if focused_window:
                win = MacWindow(self.controller, focused_window)
                return win
        except Exception:
            # The accessibility focus query is the fast path; any failure falls back to checking each window below.
            pass
            
        # Fallback: check all windows if focused (less reliable/performant)
        windows = self.get_windows()
        for window in windows:
            try:
                if window.is_focused():
                    return window
            except Exception:
                # If window doesn't support focus check or other error, skip it
                continue
        
        return None

    @property
    def name(self) -> str:
        rtnval = self.localized_name

        if rtnval is None:
            rtnval = self.APPLICATION_NAME

        return rtnval

    @property
    def identifier(self) -> str:
        rtnval = self.bundle_identifier
        return rtnval

    @property
    def bounds(self):
        """
            The bounding rectangle (x, y, width, height) for the application.
        """
        try:
            windows = self.get_windows()
        except Exception:
            windows = []

        if windows is not None:
            if len(windows) > 0:
                window = windows[0]
                return window.bounds

        rtnval = (0, 0, 0, 0)
        return rtnval

    @property
    def position(self):
        bounds = self.bounds
        rtnval = (bounds[0], bounds[1])
        return rtnval

    @property
    def size(self):
        bounds = self.bounds
        rtnval = (bounds[2], bounds[3])
        return rtnval

    @property
    def is_visible(self) -> bool:
        if self._native_obj.isHidden():
            return False

        return True

    def bring_to_front(self) -> None:
        self.activate()
        return

    def send_to_back(self) -> None:
        self.hide()
        return
    
    @property
    def bundle_identifier(self) -> str:
        rtnval = self._native_obj.bundleIdentifier()
        return rtnval

    @property
    def bundle_url(self) -> str:
        rtnval = self._native_obj.bundleURL()
        return rtnval
    
    @property
    def controller(self) -> "MacOSAutomation":
        return self._controller_ref()

    @property
    def executable_url(self) -> str:
        rtnval = self._native_obj.executableURL()
        return rtnval

    @property
    def icon(self) -> MacIcon:
        rtnval = MacIcon(self.controller, self._native_obj.icon())
        return rtnval

    @property
    def is_frontmost(self):
        rtnval = self._native_obj.isActive()
        return rtnval

    @property
    def launch_date(self):
        rtnval = self._native_obj.launchDate()
        return rtnval

    @property
    def localized_name(self) -> str:
        rtnval = self._native_obj.localizedName()
        return rtnval

    @property
    def localized_name_lower(self) -> str:
        rtnval = self._native_obj.localizedName().lower()
        return rtnval
    
    @property
    def owns_menu_bar(self) -> bool:
        rtnval = self._native_obj.ownsMenuBar()
        return rtnval
    
    @property
    def process_identifier(self) -> str:
        rtnval = self._native_obj.processIdentifier()
        return rtnval

    @property
    def sb_process(self):

        if self._sb_process is None:
            app_name = self.APPLICATION_NAME

            if app_name == "NotSet":
                app_name = self.localized_name

            if app_name is None:
                self._sb_process = None
            else:
                self._sb_process = self.controller.lookup_scripting_process_by_name(app_name)

        return self._sb_process

    @property
    def scripting_process(self):
        """
            Returns the scripting process that represents the application.
        """
        rtnval = self.sb_process
        return rtnval

    @property
    def accessibility(self) -> UiaAccessibilityApplication:
        """
            Returns the accessibility application wrapper.

            :returns: The accessibility application wrapper.
        """
        if self._ax_app is None:
            pid = self.process_identifier
            self._ax_app = UiaAccessibilityApplication(self.controller, pid)

        return self._ax_app

    def is_accessibility_available(self) -> bool:
        """
            Indicates whether Accessibility access is available.
        """
        rtnval = is_accessibility_trusted(prompt=False)
        return rtnval

    def launch(self) -> None:
        """
            Ensures the application is launched.
        """
        if self._native_obj is None:
            errmsg = "The application has no native instance to launch."
            raise ValueError(errmsg)

        if self._native_obj.isFinishedLaunching() is False:
            app_name = self.localized_name

            if app_name is None:
                app_name = self.APPLICATION_NAME

            if app_name is None:
                errmsg = "Unable to determine application name for launch."
                raise InteractionError(errmsg)

            self.controller.workspace.launch_application_by_name(app_name)

        return

    def activate(self):

        if self._native_obj.isFinishedLaunching() is False:
            self.launch()

        if self._native_obj.isHidden():
            self.unhide()

        self._native_obj.activateWithOptions_(
            AppKit.NSApplicationActivateAllWindows | AppKit.NSApplicationActivateIgnoringOtherApps
        )

        return
    
    def focus(self):

        this_app_name = self.localized_name

        for app in self.controller.workspace.runningApplications():
            if app.localized_name != this_app_name:
                app.hide()
            else:
                app.unhide()

        return
        

    def hide(self):

        self._native_obj.hide()

        return

    def quit(self):

        self._native_obj.terminate()

        return

    def terminate(self):

        self._native_obj.terminate()

        return

    def click(self) -> None:
        self.activate()
        return

    def type_keys(self, keys: str) -> None:
        self.send_keys(keys)
        return

    def get_windows(self) -> List[UIWindow]:
        """
            Returns window wrappers that represent the application's windows.
        """
        window_list = []

        try:
            ax_windows = self.accessibility.windows()
            for ax_window in ax_windows:
                window_list.append(MacWindow(self.controller, ax_window))
        except ConfigurationError:
            raise
        except Exception:
            # Accessibility may be unavailable or denied. Fall back to scripting windows.
            pass

        if len(window_list) > 0:
            return window_list

        process = self.scripting_process
        if process is None:
            rtn_list = []
            return rtn_list

        sb_windows = process.windows()
        window_list = []
        for sb_window in sb_windows:
            window_list.append(MacWindow(self.controller, sb_window))

        return window_list

    def find_first_by_role(self, role: str, include_self: bool = False) -> Any:
        """
            Finds the first element matching a role using Accessibility when available.
        """
        try:
            found = self.accessibility.find_first_by_role(role=role, include_self=include_self)
            if found is None and role == "AXWindow":
                windows = self.get_windows()
                if len(windows) > 0:
                    return windows[0]

            return found
        except ConfigurationError:
            raise
        except Exception:
            return None

    def find_by_title(self, title: str, include_self: bool = False, expression: bool = False) -> List[Any]:
        """
            Finds elements by title using Accessibility when available.
        """
        try:
            return self.accessibility.find_by_title(title=title, include_self=include_self, expression=expression)
        except ConfigurationError:
            raise
        except Exception:
            return []

    def find_by_contents(self, contents: str, include_self: bool = False, expression: bool = False) -> List[Any]:
        """
            Finds elements by contents using Accessibility when available.
        """
        try:
            return self.accessibility.find_by_contents(contents=contents, include_self=include_self, expression=expression)
        except ConfigurationError:
            raise
        except Exception:
            return []

    def find_element(self, **kwargs) -> Optional[UIElement]:
        """
        Finds the first child element matching criteria.
        Delegates to the accessibility root element.
        """
        try:
            return self.accessibility.root_element().find_element(**kwargs)
        except Exception:
            return None

    def find_elements(self, **kwargs) -> List[UIElement]:
        """
        Finds all child elements matching criteria.
        Delegates to the accessibility root element.
        """
        try:
            return self.accessibility.root_element().find_elements(**kwargs)
        except Exception:
            return []

    def send_keys(self, keys: str) -> None:
        """
            Sends a key stream to the focused control after activating the app.
        """
        self.activate()

        windows = self.get_windows()
        if windows is not None:
            if len(windows) > 0:
                window = windows[0]
                try:
                    window.focus()
                except NotImplementedError:
                    # Window objects that cannot be focused individually still receive the keys through the
                    # application activated above.
                    pass
            else:
                pass
        else:
            raise InteractionError("Expected a list of windows but received None.")

        send_keys_to_focused(keys)

        return
    
    def unfocus(self):

        for app in self.controller.workspace.runningApplications():
            app.unhide()

        return

    def unhide(self):

        self._native_obj.unhide()

        return
    
    def windows(self) -> List[SbWindow]:
        """
            Returns scripting windows from the application process. This is distinct
            from UIA window wrappers returned by :meth:`get_windows`.
        """
        process = self.scripting_process
        if process is None:
            rtn_list = []
            return rtn_list

        sb_wlist = process.windows()

        return sb_wlist

    def __repr__(self):
        sval = f"MacApplication< {self.localized_name}: {self.bundle_identifier} >"
        return sval

    def __str__(self):
        sval = f"MacApplication< {self.localized_name}: {self.bundle_identifier} >"
        return sval
