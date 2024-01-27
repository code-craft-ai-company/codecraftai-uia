
from mojo.uia.wrappers.uiaapplication import UiaApplication

class AppContacts(UiaApplication):
    """
        Represents and instance of the 'Contacts' application.
    """

    APPLICATION_NAME = "Contacts"
    BUNDLE_IDENTIFIER = "com.apple.AddressBook"
