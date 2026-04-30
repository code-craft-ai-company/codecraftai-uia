
from automojo.uia.platforms.macos.wrappers.uiaapplication import MacApplication

class AppFinder(MacApplication):
    """
        Represents an instance of the 'Finder' application.
    """

    APPLICATION_NAME = "Finder"
    BUNDLE_IDENTIFIER = "com.apple.finder"
