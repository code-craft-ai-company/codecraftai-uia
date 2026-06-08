
from ccai.uia.platforms.macos.wrappers.uiaapplication import MacApplication

class AppTextEdit(MacApplication):
    """
        Represents an instance of the 'TextEdit' application.
    """

    APPLICATION_NAME = "TextEdit"
    BUNDLE_IDENTIFIER = "com.apple.TextEdit"