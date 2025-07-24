from typing import Any, List, TYPE_CHECKING

import AppleScriptKit

from mojo.uia.wrappers.wrappedobject import WrappedObject

if TYPE_CHECKING:
    from mojo.uia.uiacontroller import UiaController

class SbWindow(WrappedObject):

    def __init__(self, controller: "UiaController", native_obj: Any):
        super().__init__(controller, native_obj)
        return
    
    def groups(self) -> list:
        objlist = [obj for obj in self.native_obj.groups()]

        for obj in objlist:
            name = obj.name
            print(name)

        return objlist