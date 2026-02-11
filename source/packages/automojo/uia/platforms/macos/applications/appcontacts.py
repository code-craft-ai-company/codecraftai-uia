
from automojo.uia.platforms.macos.wrappers.uiaapplication import MacApplication

class AppContacts(MacApplication):
    """
        Represents and instance of the 'Contacts' application.
    """

    APPLICATION_NAME = "Contacts"
    BUNDLE_IDENTIFIER = "com.apple.AddressBook"
