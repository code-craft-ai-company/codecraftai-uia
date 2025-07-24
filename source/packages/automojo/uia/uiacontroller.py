
import AppKit

from mojo.uia.uiacatalog import UiaCatalog

from mojo.uia.wrappers.uiaworkspace import UiaWorkspace
from mojo.uia.wrappers.uiaapplication import UiaApplication

from mojo.uia.appscript.asdatabaseevents import AsDatabaseEvents
from mojo.uia.appscript.asimageevents import AsImageEvents
from mojo.uia.appscript.assystemevents import AsSystemEvents


class UiaController:
    """
        The :class:`UiaController` provides a central point of access in order to
        connect with the user interface 
    """

    def __init__(self):
        self._workspace = UiaWorkspace(self)
        self._catalog = UiaCatalog()

        self._database_events = self.get_application_by_name(AsDatabaseEvents.APPLICATION_NAME)
        self._image_events = self.get_application_by_name(AsImageEvents.APPLICATION_NAME)
        self._system_events = self.get_application_by_name(AsSystemEvents.APPLICATION_NAME)
        return

    @property
    def catalog(self) -> UiaCatalog:
        return self._catalog

    @property
    def database_events(self) -> AsDatabaseEvents:
        return self._database_events
    
    @property
    def image_events(self) -> AsImageEvents:
        return self._image_events

    @property
    def system_events(self) -> AsSystemEvents:
        return self._system_events

    @property
    def workspace(self):
        return self._workspace

    def get_application_by_name(self, application_name: str, auto_launch: bool = True, metadata_refresh: bool = False) -> UiaApplication:

        rtn_app = None

        application_list = self._workspace.runningApplications()
        for nxt_app in application_list:
            if nxt_app.localized_name == application_name:
                rtn_app = nxt_app
                break

        # If the specified application is not already running, then we 
        if rtn_app is None:
            if auto_launch:
                rtn_app = self._workspace.launch_application_by_name(application_name, metadata_refresh=metadata_refresh)
        else:
            app_metadata = self._workspace.lookup_application_metadata_by_name(application_name, metadata_refresh=metadata_refresh)
            bundle_id = app_metadata.CFBundleIdentifier

            app_type = self._catalog.lookup_application_type_by_bundle_id(bundle_id)

            # Re-Wrap the application with a customize type if we have one
            rtn_app = app_type(self, rtn_app.native_obj)

            if rtn_app.APPLICATION_NAME == "NotSet":
                rtn_app.APPLICATION_NAME = application_name
            if rtn_app.BUNDLE_IDENTIFIER == "NotSet":
                rtn_app.BUNDLE_IDENTIFIER = bundle_id

        return rtn_app
    
    def lookup_scripting_process_by_name(self, application_name: str):

        scr_process = None

        scr_process_list = self.system_events.processes()

        for nxtproc in scr_process_list:
            nxtproc_name = nxtproc.displayedName()
            if nxtproc_name == application_name:
                scr_process = nxtproc
                break

        return scr_process
