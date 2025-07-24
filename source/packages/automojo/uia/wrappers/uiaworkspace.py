
from typing import Dict, List, TYPE_CHECKING

import weakref

import AppKit

from mojo.uia.wrappers.uiaapplication import UiaApplication
from mojo.uia.wrappers.uiametadataquery import UiaMetadataQuery, SearchPredicate
from mojo.uia.wrappers.uiametadataitem import UiaMetadataItem

if TYPE_CHECKING:
    from mojo.uia.uiacontroller import UiaController

class UiaWorkspace:
    """
    """

    def __init__(self, controller: "UiaController"):
        self._controller_ref = weakref.ref(controller)
        self._workspace = AppKit.NSWorkspace.sharedWorkspace()
        self._application_metadata = None
        return
    
    @property
    def controller(self) -> "UiaController":
        return self._controller_ref()

    def runningApplications(self) -> List[UiaApplication]:

        app_list = [UiaApplication(self, obj) for obj in self._workspace.runningApplications()]

        return app_list
    
    def launch_application_by_name(self, application_name: str, metadata_refresh: bool=False) -> UiaApplication:

        rtn_app = None

        app_metadata = self.lookup_application_metadata_by_name(application_name, metadata_refresh=metadata_refresh)

        app_path = app_metadata.Path
        controller = self.controller
        catalog = controller.catalog

        bundle = AppKit.NSBundle.alloc().initWithPath_(app_path)
        bundle_id = bundle.bundleIdentifier()
        url = self._workspace.URLForApplicationWithBundleIdentifier_(
            bundle_id
        )

        config = AppKit.NSWorkspaceOpenConfiguration.alloc().init()
        config.setActivates_(False)
        config.setHides_(True)

        def _launch_completion_handler(app, _error):
        
            nonlocal rtn_app

            nonlocal bundle_id
            nonlocal controller
            nonlocal catalog

            app_type = catalog.lookup_application_type_by_bundle_id(bundle_id)
            rtn_app =  app_type(controller, app)
            
            return
        
        self._workspace.openApplicationAtURL_configuration_completionHandler_(
            url, config, _launch_completion_handler     
        )

        return rtn_app

    def lookup_application_metadata_by_name(self, application_name: str, metadata_refresh: bool = False) -> UiaMetadataItem:

        if metadata_refresh or self._application_metadata is None:
            self._application_metadata = self.query_application_metadata()

        app_metadata = None
        if application_name in self._application_metadata:
            app_metadata = self._application_metadata[application_name]
        else:
            errmsg = f"No application metadata found for '{application_name}'"
            raise ValueError(errmsg)

        return app_metadata

    def query_application_metadata(self) -> Dict[str, UiaMetadataItem]:

        controller = self.controller

        predicate = SearchPredicate("kMDItemContentType == 'com.apple.application-bundle'")
        query = UiaMetadataQuery(controller, predicate)
        results = query.run()

        app_metadata_list = { rv.DisplayName: rv for rv in results }

        return app_metadata_list