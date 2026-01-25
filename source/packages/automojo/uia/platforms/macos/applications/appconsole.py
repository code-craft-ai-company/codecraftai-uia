
from automojo.uia.platforms.macos.wrappers.uiaapplication import UiaApplication

class AppConsole(UiaApplication):
    """
        Represents and instance of the 'Console' application.
    """

    APPLICATION_NAME = "Console"
    BUNDLE_IDENTIFIER = "com.apple.Console"
