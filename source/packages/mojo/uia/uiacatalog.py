
from typing import Type

from mojo.uia.wrappers.uiaapplication import UiaApplication

from mojo.uia.applications.appautomator import AppAutomator
from mojo.uia.applications.appcalculator import AppCalculator
from mojo.uia.applications.appcalendar import AppCalendar
from mojo.uia.applications.appconsole import AppConsole
from mojo.uia.applications.appcontacts import AppContacts
from mojo.uia.applications.appdictionary import AppDictionary
from mojo.uia.applications.appfinder import AppFinder
from mojo.uia.applications.appfontbook import AppFontBook
from mojo.uia.applications.appkeynote import AppKeynote
from mojo.uia.applications.appmail import AppMail
from mojo.uia.applications.appmaps import AppMaps
from mojo.uia.applications.appmessages import AppMessages
from mojo.uia.applications.appmusic import AppMusic
from mojo.uia.applications.appnotes import AppNotes
from mojo.uia.applications.appnumbers import AppNumbers
from mojo.uia.applications.apppages import AppPages
from mojo.uia.applications.appphotos import AppPhotos
from mojo.uia.applications.apppreview import AppPreview
from mojo.uia.applications.appquicktimeplayer import AppQuickTimePlayer
from mojo.uia.applications.appreminders import AppReminders
from mojo.uia.applications.appsafari import AppSafari
from mojo.uia.applications.appscripteditor import AppScriptEditor
from mojo.uia.applications.appshortcuts import AppShortcuts
from mojo.uia.applications.appstocks import AppStocks
from mojo.uia.applications.appsystemsettings import AppSystemSettings
from mojo.uia.applications.appterminal import AppTerminal
from mojo.uia.applications.apptextedit import AppTextEdit
from mojo.uia.applications.apptv import AppTV

BUNDLE_TO_APPLICATION_TYPES = {
    AppAutomator.BUNDLE_IDENTIFIER: AppAutomator,
    AppCalculator.BUNDLE_IDENTIFIER: AppCalculator,
    AppCalendar.BUNDLE_IDENTIFIER: AppCalendar,
    AppConsole.BUNDLE_IDENTIFIER: AppConsole,
    AppContacts.BUNDLE_IDENTIFIER: AppContacts,
    AppDictionary.BUNDLE_IDENTIFIER: AppDictionary,
    AppFinder.BUNDLE_IDENTIFIER: AppFinder,
    AppFontBook.BUNDLE_IDENTIFIER: AppFontBook,
    AppKeynote.BUNDLE_IDENTIFIER: AppKeynote,
    AppMail.BUNDLE_IDENTIFIER: AppMail,
    AppMaps.BUNDLE_IDENTIFIER: AppMaps,
    AppMessages.BUNDLE_IDENTIFIER: AppMessages,
    AppMusic.BUNDLE_IDENTIFIER: AppMusic,
    AppNotes.BUNDLE_IDENTIFIER: AppNotes,
    AppNumbers.BUNDLE_IDENTIFIER: AppNumbers,
    AppPages.BUNDLE_IDENTIFIER: AppPages,
    AppPhotos.BUNDLE_IDENTIFIER: AppPhotos,
    AppPreview.BUNDLE_IDENTIFIER: AppPreview,
    AppQuickTimePlayer.BUNDLE_IDENTIFIER: AppQuickTimePlayer,
    AppReminders.BUNDLE_IDENTIFIER: AppReminders,
    AppSafari.BUNDLE_IDENTIFIER: AppSafari,
    AppScriptEditor.BUNDLE_IDENTIFIER: AppScriptEditor,
    AppShortcuts.BUNDLE_IDENTIFIER: AppShortcuts,
    AppStocks.BUNDLE_IDENTIFIER: AppStocks,
    AppSystemSettings.BUNDLE_IDENTIFIER: AppSystemSettings,
    AppTerminal.BUNDLE_IDENTIFIER: AppTerminal,
    AppTextEdit.BUNDLE_IDENTIFIER: AppTextEdit,
    AppTV.BUNDLE_IDENTIFIER: AppTV
}

class UiaCatalog:
    """
    """

    def __init__(self):
        self._application_types = BUNDLE_TO_APPLICATION_TYPES
        return
    
    def lookup_application_type_by_bundle_id(self, bundle_id: str) -> Type:

        app_type = None
        
        if bundle_id in self._application_types:
            app_type = self._application_types[bundle_id]
        else:
            app_type = UiaApplication

        return app_type