
from automojo.uia.platforms.macos.wrappers.uiaapplication import UiaApplication

class AppPreview(UiaApplication):
    """
        Represents and instance of the 'Preview' application.
    """

    APPLICATION_NAME = "Preview"
    BUNDLE_IDENTIFIER = "com.apple.Preview"
