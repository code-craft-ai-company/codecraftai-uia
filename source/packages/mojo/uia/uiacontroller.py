
import AppKit

from mojo.uia.wrappers.uiaworkspace import UiaWorkspace

class UiaController:
    """
        The :class:`UiaController` provides a central point of access in order to
        connect with the user interface 
    """

    def __init__(self):
        self._workspace = UiaWorkspace()
        return

    def get_application(self, application_name: str):

        application_list = self._workspace.runningApplications()
        for app in application_list:
            print(app)

        return


