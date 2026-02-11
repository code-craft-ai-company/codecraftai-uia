
from automojo.uia.platforms.macos.wrappers.uiaapplication import MacApplication

class AppMail(MacApplication):
    """
        Represents and instance of the 'Mail' application.
    """

    APPLICATION_NAME = "Mail"
    BUNDLE_IDENTIFIER = "com.apple.mail"
