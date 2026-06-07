
from ccai.uia.platforms.macos.wrappers.uiaapplication import MacApplication

class AppCalculator(MacApplication):
    """
        Represents an instance of the 'Calculator' application.
    """

    APPLICATION_NAME = "Calculator"
    BUNDLE_IDENTIFIER = "com.apple.calculator"
    