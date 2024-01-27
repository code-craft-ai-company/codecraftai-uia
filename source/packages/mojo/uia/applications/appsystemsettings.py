
from mojo.uia.wrappers.uiaapplication import UiaApplication

class AppSystemSettings(UiaApplication):
    """
        Represents and instance of the 'System Preferences' application.
    """

    APPLICATION_NAME = "System Settings"
    BUNDLE_IDENTIFIER = "com.apple.systempreferences"
