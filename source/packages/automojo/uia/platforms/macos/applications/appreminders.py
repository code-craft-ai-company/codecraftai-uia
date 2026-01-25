
from automojo.uia.platforms.macos.wrappers.uiaapplication import UiaApplication

class AppReminders(UiaApplication):
    """
        Represents and instance of the 'Reminders' application.
    """

    APPLICATION_NAME = "Reminders"
    BUNDLE_IDENTIFIER = "com.apple.reminders"
