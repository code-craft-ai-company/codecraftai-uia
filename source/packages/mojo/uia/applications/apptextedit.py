
from mojo.uia.wrappers.uiaapplication import UiaApplication

class AppTextEdit(UiaApplication):
    """
        Represents and instance of the 'TextEdit' application.
    """

    APPLICATION_NAME = "TextEdit"
    BUNDLE_IDENTIFIER = "com.apple.TextEdit"