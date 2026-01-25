
from typing import Any, List, TYPE_CHECKING

from automojo.uia.platforms.macos.wrappers.wrappedobject import WrappedObject

from automojo.uia.platforms.macos.wrappers.sbwindow import SbWindow

if TYPE_CHECKING:
    from automojo.uia.platforms.macos.automation import MacOSAutomation

class SbProcess(WrappedObject):

    def __init__(self, controller: "MacOSAutomation", native_obj: Any):
        super().__init__(controller, native_obj)
        return

    def displayedName(self) -> str:
        rtnval = self._native_obj.displayedName()
        return rtnval
    
    def windows(self) -> List[SbWindow]:
        controller = self.controller
        wlist = [SbWindow(controller, w) for w in self.native_obj.windows()]
        return wlist