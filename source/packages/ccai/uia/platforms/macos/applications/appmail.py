
from ccai.uia.platforms.macos.wrappers.uiaapplication import MacApplication

class AppMail(MacApplication):
    """
        Represents an instance of the 'Mail' application.
    """

    APPLICATION_NAME = "Mail"
    BUNDLE_IDENTIFIER = "com.apple.mail"
