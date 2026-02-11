
from automojo.uia.platforms.macos.wrappers.uiaapplication import MacApplication

class AppStocks(MacApplication):
    """
        Represents and instance of the 'Stocks' application.
    """

    APPLICATION_NAME = "Stocks"
    BUNDLE_IDENTIFIER = "com.apple.stocks"