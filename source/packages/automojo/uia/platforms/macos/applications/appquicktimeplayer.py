
from automojo.uia.platforms.macos.wrappers.uiaapplication import MacApplication

class AppQuickTimePlayer(MacApplication):
    """
        Represents and instance of the 'Quick Time Player' application.
    """

    APPLICATION_NAME = "QuickTime Player"
    BUNDLE_IDENTIFIER = "com.apple.QuickTimePlayerX"
