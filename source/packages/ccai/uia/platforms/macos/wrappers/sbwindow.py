from typing import Any, List, TYPE_CHECKING

import AppleScriptKit

from ccai.uia.platforms.macos.wrappers.wrappedobject import WrappedObject

if TYPE_CHECKING:
    from ccai.uia.platforms.macos.automation import MacOSAutomation

class SbWindow(WrappedObject):

    def __init__(self, controller: "MacOSAutomation", native_obj: Any):
        super().__init__(controller, native_obj)
        return
    
    def groups(self) -> list:
        objlist = [obj for obj in self.native_obj.groups()]

        return objlist