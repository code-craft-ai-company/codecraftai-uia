
from typing import List

import AppKit

from mojo.uia.wrappers.uiaapplication import UiaApplication
from mojo.uia.wrappers.uiametadataquery import UiaMetadataQuery, SearchPredicate

class UiaWorkspace:
    """
    """

    def __init__(self):
        self._workspace = AppKit.NSWorkspace.sharedWorkspace()
        return
    
    def runningApplications(self) -> List[UiaApplication]:

        app_list = [UiaApplication(obj) for obj in self._workspace.runningApplications()]

        return app_list
    
    def applicationPaths(self) -> List[str]:

        predicate = SearchPredicate("kMDItemContentType == 'com.apple.application-bundle'")
        query = UiaMetadataQuery(predicate)
        results = query.run()

        app_path_list = [rv.Path for rv in results]

        return app_path_list