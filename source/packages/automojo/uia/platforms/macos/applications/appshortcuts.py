
from automojo.uia.platforms.macos.wrappers.uiaapplication import UiaApplication

class AppShortcuts(UiaApplication):
    """
        Represents and instance of the 'Shortcuts' application.
    """

    APPLICATION_NAME = "Shortcuts"
    BUNDLE_IDENTIFIER = "com.apple.shortcuts"