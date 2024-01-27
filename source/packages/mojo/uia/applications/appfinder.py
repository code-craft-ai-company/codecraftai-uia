
from mojo.uia.wrappers.uiaapplication import UiaApplication

class AppFinder(UiaApplication):
    """
        Represents and instance of the 'Finder' application.
    """

    APPLICATION_NAME = "Finder"
    BUNDLE_IDENTIFIER = "com.apple.finder"
