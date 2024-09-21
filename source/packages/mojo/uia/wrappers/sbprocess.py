
from typing import Any, List, TYPE_CHECKING

from mojo.uia.wrappers.wrappedobject import WrappedObject

from mojo.uia.wrappers.sbwindow import SbWindow

if TYPE_CHECKING:
    from mojo.uia.uiacontroller import UiaController

class SbProcess(WrappedObject):

    def __init__(self, controller: "UiaController", native_obj: Any):
        super().__init__(controller, native_obj)
        return

    def displayedName(self) -> str:
        rtnval = self._native_obj.displayedName()
        return rtnval
    
    def windows(self) -> List[SbWindow]:
        controller = self.controller
        wlist = [SbWindow(controller, w) for w in self.native_obj.windows()]
        return wlist