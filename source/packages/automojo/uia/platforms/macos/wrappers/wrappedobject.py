
from typing import Any, TYPE_CHECKING

import weakref

if TYPE_CHECKING:
    from automojo.uia.platforms.macos.automation import MacOSAutomation

class WrappedObject:

    def __init__(self, controller: "MacOSAutomation", native_obj: Any):
        self._controller_ref = weakref.ref(controller)
        self._native_obj = native_obj
        return
    
    @property
    def controller(self) -> "MacOSAutomation":
        return self._controller_ref()

    @property
    def native_obj(self) -> Any:
        return self._native_obj
