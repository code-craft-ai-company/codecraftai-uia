
from automojo.uia.platforms.macos.wrappers.uiaapplication import UiaApplication

class AppAutomator(UiaApplication):
    """
        Represents and instance of the 'Automator' application.
    """

    APPLICATION_NAME = "Automator"
    BUNDLE_IDENTIFIER = "com.apple.Automator"
