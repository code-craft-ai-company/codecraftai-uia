
from automojo.uia.platforms.macos.wrappers.uiaapplication import MacApplication

class AppSystemSettings(MacApplication):
    """
        Represents and instance of the 'System Preferences' application.
    """

    APPLICATION_NAME = "System Settings"
    BUNDLE_IDENTIFIER = "com.apple.systempreferences"
