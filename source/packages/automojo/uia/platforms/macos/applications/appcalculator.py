
from automojo.uia.platforms.macos.wrappers.uiaapplication import MacApplication

class AppCalculator(MacApplication):
    """
        Represents and instance of the 'Calculator' application.
    """

    APPLICATION_NAME = "Calculator"
    BUNDLE_IDENTIFIER = "com.apple.calculator"
    