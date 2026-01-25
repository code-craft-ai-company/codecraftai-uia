
from typing import Any, TYPE_CHECKING

from automojo.uia.platforms.macos.wrappers.wrappedobject import WrappedObject

if TYPE_CHECKING:
    from automojo.uia.platforms.macos.automation import MacOSAutomation

class UiaIcon(WrappedObject):

    def __init__(self, controller: "MacOSAutomation", native_obj: Any):
        super().__init__(controller, native_obj)
        return
