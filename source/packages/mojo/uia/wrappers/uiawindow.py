
from typing import Any, TYPE_CHECKING

from mojo.uia.wrappers.wrappedobject import WrappedObject

if TYPE_CHECKING:
    from mojo.uia.uiacontroller import UiaController

class UiaApplication(WrappedObject):

    def __init__(self, controller: "UiaController", native_obj: Any):
        super().__init__(controller, native_obj)
        return