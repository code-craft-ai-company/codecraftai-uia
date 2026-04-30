
from automojo.uia.platforms.macos.wrappers.uiaapplication import MacApplication

class AppReminders(MacApplication):
    """
        Represents an instance of the 'Reminders' application.
    """

    APPLICATION_NAME = "Reminders"
    BUNDLE_IDENTIFIER = "com.apple.reminders"
