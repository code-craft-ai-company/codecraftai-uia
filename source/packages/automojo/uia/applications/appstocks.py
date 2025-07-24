
from mojo.uia.wrappers.uiaapplication import UiaApplication

class AppStocks(UiaApplication):
    """
        Represents and instance of the 'Stocks' application.
    """

    APPLICATION_NAME = "Stocks"
    BUNDLE_IDENTIFIER = "com.apple.stocks"