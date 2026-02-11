
from automojo.uia.platforms.macos.wrappers.uiaapplication import MacApplication

class AppPhotos(MacApplication):
    """
        Represents and instance of the 'Photos' application.
    """

    APPLICATION_NAME = "Photos"
    BUNDLE_IDENTIFIER = "com.apple.Photos"
