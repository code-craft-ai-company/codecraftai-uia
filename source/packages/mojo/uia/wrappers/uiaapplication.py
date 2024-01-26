
from mojo.uia.wrappers.uiawrappedobject import UiaWrappedObject

class UiaApplication(UiaWrappedObject):

    def __init__(self, native_obj):
        super().__init__(native_obj)
        return
    
    def localized_name(self) -> str:
        rtnval = self._native_obj.localizedName()
        return rtnval

    def localized_name_lower(self) -> str:
        rtnval = self._native_obj.localizedName().lower()
        return rtnval