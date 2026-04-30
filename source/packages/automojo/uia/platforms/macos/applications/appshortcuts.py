
from automojo.uia.platforms.macos.wrappers.uiaapplication import MacApplication

class AppShortcuts(MacApplication):
    """
        Represents an instance of the 'Shortcuts' application.
    """

    APPLICATION_NAME = "Shortcuts"
    BUNDLE_IDENTIFIER = "com.apple.shortcuts"