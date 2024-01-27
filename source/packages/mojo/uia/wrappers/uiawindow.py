
from typing import Any, TYPE_CHECKING

from mojo.uia.wrappers.uiawrappedobject import UiaWrappedObject

if TYPE_CHECKING:
    from mojo.uia.uiacontroller import UiaController

class UiaApplication(UiaWrappedObject):

    def __init__(self, controller: "UiaController", native_obj: Any):
        super().__init__(controller, native_obj)
        return