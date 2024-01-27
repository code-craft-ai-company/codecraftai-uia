
from typing import Any, TYPE_CHECKING

import weakref

import AppKit

from mojo.uia.wrappers.uiawrappedobject import UiaWrappedObject

from mojo.uia.wrappers.uiaicon import UiaIcon


if TYPE_CHECKING:
    from mojo.uia.uiacontroller import UiaController

class UiaApplication(UiaWrappedObject):

    def __init__(self, controller: "UiaController", native_obj: Any):
        super().__init__(controller, native_obj)
        self._se_process = None
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
    def controller(self) -> "UiaController":
        return self._controller_ref()

    @property
    def executable_url(self) -> str:
        rtnval = self._native_obj.executableURL()
        return rtnval

    @property
    def icon(self) -> UiaIcon:
        rtnval = UiaIcon(self._native_obj.icon())
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

    def activate(self):

        if not self._native_obj.isFinishedLaunching():
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
    
    def focus(self):

        for app in self.controller.workspace.runningApplications():
            app.unhide()

        return

    def unhide(self):

        self._native_obj.unhide()

        return

    def __repr__(self):
        sval = f"UiaApplication< {self.localized_name}: {self.bundle_identifier} >"
        return sval

    def __str__(self):
        sval = f"UiaApplication< {self.localized_name}: {self.bundle_identifier} >"
        return sval