
class UiaWrappedObject:

    def __init__(self, native_obj):
        self._native_obj = native_obj
        return
    
    @property
    def native_obj(self):
        return self._native_obj
