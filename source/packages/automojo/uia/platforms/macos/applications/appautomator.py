
from automojo.uia.platforms.macos.wrappers.uiaapplication import MacApplication

class AppAutomator(MacApplication):
    """
        Represents and instance of the 'Automator' application.
    """

    APPLICATION_NAME = "Automator"
    BUNDLE_IDENTIFIER = "com.apple.Automator"
