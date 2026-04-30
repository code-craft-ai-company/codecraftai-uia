
from automojo.uia.platforms.macos.wrappers.uiaapplication import MacApplication

class AppPreview(MacApplication):
    """
        Represents an instance of the 'Preview' application.
    """

    APPLICATION_NAME = "Preview"
    BUNDLE_IDENTIFIER = "com.apple.Preview"
