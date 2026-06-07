
from typing import Any, TYPE_CHECKING

from ccai.uia.platforms.macos.wrappers.wrappedobject import WrappedObject

if TYPE_CHECKING:
    from ccai.uia.platforms.macos.automation import MacOSAutomation

class MacIcon(WrappedObject):

    def __init__(self, controller: "MacOSAutomation", native_obj: Any):
        super().__init__(controller, native_obj)
        return
