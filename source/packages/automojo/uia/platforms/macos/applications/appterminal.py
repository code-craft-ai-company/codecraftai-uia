
from automojo.uia.platforms.macos.wrappers.uiaapplication import MacApplication

class AppTerminal(MacApplication):
    """
        Represents and instance of the 'Terminal' application.
    """

    APPLICATION_NAME = "Terminal"
    BUNDLE_IDENTIFIER = "com.apple.Terminal"
    