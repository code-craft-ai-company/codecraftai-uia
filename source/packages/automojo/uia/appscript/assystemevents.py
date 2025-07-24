
from typing import Any, TYPE_CHECKING

import ScriptingBridge

from mojo.uia.wrappers.sbprocess import SbProcess
from mojo.uia.wrappers.uiaapplication import UiaApplication

if TYPE_CHECKING:
    from mojo.uia.uiacontroller import UiaController

class AsSystemEvents(UiaApplication):
    """
        Represents and instance of the 'System Events' application.
    """

    APPLICATION_NAME = "System Events"
    BUNDLE_IDENTIFIER = "com.apple.systemevents"

    def __init__(self, controller: "UiaController", native_obj: Any):
        super().__init__(controller, native_obj)

        self._scripting_bridge = None
        return

    @property
    def scripting_bridge(self):

        if self._scripting_bridge is None:
            bundle_url = self.native_obj.bundleURL()
            self._scripting_bridge = ScriptingBridge.SBApplication.alloc().initWithURL_(
                bundle_url
            )

        return self._scripting_bridge

    def processes(self):

        controller = self.controller
        proc_list = [SbProcess(controller, p) for p in self.scripting_bridge.processes()]

        return proc_list