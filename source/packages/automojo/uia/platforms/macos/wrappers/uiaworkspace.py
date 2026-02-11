
from typing import Dict, List, TYPE_CHECKING

import weakref
import subprocess
import time

import AppKit

from automojo.uia.platforms.macos.wrappers.uiaapplication import UiaApplication
from automojo.uia.platforms.macos.wrappers.uiametadataquery import UiaMetadataQuery, SearchPredicate
from automojo.uia.platforms.macos.wrappers.uiametadataitem import UiaMetadataItem
from automojo.uia.constraints import APP_LAUNCH_RETRY_COUNT, APP_LAUNCH_RETRY_INTERVAL

if TYPE_CHECKING:
    from automojo.uia.platforms.macos.automation import MacOSAutomation

class UiaWorkspace:
    """
    """

    def __init__(self, controller: "MacOSAutomation"):
        self._controller_ref = weakref.ref(controller)
        self._workspace = AppKit.NSWorkspace.sharedWorkspace()
        self._application_metadata = None
        return
    
    @property
    def controller(self) -> "MacOSAutomation":
        return self._controller_ref()

    def runningApplications(self) -> List[UiaApplication]:
        controller = self.controller
        catalog = controller.catalog

        app_list = []
        for obj in self._workspace.runningApplications():
            bundle_id = obj.bundleIdentifier()
            if bundle_id is None:
                app_type = UiaApplication
            else:
                app_type = catalog.lookup_application_type_by_bundle_id(bundle_id)

            app_list.append(app_type(controller, obj))

        return app_list
    
    def launch_application_by_name(self, application_name: str, metadata_refresh: bool=False) -> UiaApplication:

        rtn_app = None

        app_metadata = self.lookup_application_metadata_by_name(application_name, metadata_refresh=metadata_refresh)

        app_path = app_metadata.Path
        controller = self.controller
        catalog = controller.catalog

        bundle = AppKit.NSBundle.alloc().initWithPath_(app_path)
        bundle_id = bundle.bundleIdentifier()
        if bundle_id is None:
            errmsg = f"Unable to determine bundle identifier for '{application_name}'."
            raise ValueError(errmsg)

        url = self._workspace.URLForApplicationWithBundleIdentifier_(
            bundle_id
        )
        if url is None:
            errmsg = f"Unable to determine application URL for '{application_name}'."
            raise ValueError(errmsg)

        options = AppKit.NSWorkspaceLaunchDefault

        app, error = self._launch_with_retry(url, options, bundle_id, application_name)
        if app is None:
            last_error_message = str(error) if error is not None else "Unknown launch error."
            if error is not None:
                try:
                    domain = error.domain()
                except Exception:
                    domain = None
                try:
                    code = error.code()
                except Exception:
                    code = None
                try:
                    description = error.localizedDescription()
                except Exception:
                    description = None

                print(
                    (
                        "NSWorkspace launch error "
                        f"(domain={domain}, code={code}, description={description})"
                    )
                )

            errmsg = f"Failed to launch '{application_name}': {last_error_message}"
            raise RuntimeError(errmsg)

        app_type = catalog.lookup_application_type_by_bundle_id(bundle_id)
        rtn_app = app_type(controller, app)

        return rtn_app

    def _launch_with_retry(self, url: object, options: int, bundle_id: str, application_name: str):
        app = None
        error = None

        for attempt in range(APP_LAUNCH_RETRY_COUNT):
            app_result = self._workspace.launchApplicationAtURL_options_configuration_error_(
                url, options, {}, None
            )

            if isinstance(app_result, tuple) and len(app_result) == 2:
                app, error = app_result
            else:
                app = app_result
                error = None

            if app is not None:
                return app, error

            running_app = self._find_running_application(bundle_id, application_name)
            if running_app is not None:
                return running_app, None

            if attempt < APP_LAUNCH_RETRY_COUNT - 1:
                time.sleep(APP_LAUNCH_RETRY_INTERVAL)

        return app, error

    def _find_running_application(self, bundle_id: str, application_name: str):
        for obj in self._workspace.runningApplications():
            try:
                if bundle_id and obj.bundleIdentifier() == bundle_id:
                    return obj
            except Exception:
                pass

            try:
                if obj.localizedName() == application_name:
                    return obj
            except Exception:
                pass

        return None

    def _launch_via_open(self, application_name: str, timeout: float = 5.0):
        try:
            subprocess.Popen(["open", "-a", application_name])
        except Exception:
            return None

        end_time = time.time() + timeout
        while time.time() < end_time:
            for obj in self._workspace.runningApplications():
                if obj.localizedName() == application_name:
                    return obj
            time.sleep(0.25)

        return None

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
