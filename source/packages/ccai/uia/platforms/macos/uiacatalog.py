
from typing import Type

from ccai.uia.platforms.macos.wrappers.uiaapplication import MacApplication

from ccai.uia.platforms.macos.applications.appautomator import AppAutomator
from ccai.uia.platforms.macos.applications.appcalculator import AppCalculator
from ccai.uia.platforms.macos.applications.appcalendar import AppCalendar
from ccai.uia.platforms.macos.applications.appconsole import AppConsole
from ccai.uia.platforms.macos.applications.appcontacts import AppContacts
from ccai.uia.platforms.macos.applications.appdictionary import AppDictionary
from ccai.uia.platforms.macos.applications.appfinder import AppFinder
from ccai.uia.platforms.macos.applications.appfontbook import AppFontBook
from ccai.uia.platforms.macos.applications.appkeynote import AppKeynote
from ccai.uia.platforms.macos.applications.appmail import AppMail
from ccai.uia.platforms.macos.applications.appmaps import AppMaps
from ccai.uia.platforms.macos.applications.appmessages import AppMessages
from ccai.uia.platforms.macos.applications.appmusic import AppMusic
from ccai.uia.platforms.macos.applications.appnotes import AppNotes
from ccai.uia.platforms.macos.applications.appnumbers import AppNumbers
from ccai.uia.platforms.macos.applications.apppages import AppPages
from ccai.uia.platforms.macos.applications.appphotos import AppPhotos
from ccai.uia.platforms.macos.applications.apppreview import AppPreview
from ccai.uia.platforms.macos.applications.appquicktimeplayer import AppQuickTimePlayer
from ccai.uia.platforms.macos.applications.appreminders import AppReminders
from ccai.uia.platforms.macos.applications.appsafari import AppSafari
from ccai.uia.platforms.macos.applications.appscripteditor import AppScriptEditor
from ccai.uia.platforms.macos.applications.appshortcuts import AppShortcuts
from ccai.uia.platforms.macos.applications.appstocks import AppStocks
from ccai.uia.platforms.macos.applications.appsystemsettings import AppSystemSettings
from ccai.uia.platforms.macos.applications.appterminal import AppTerminal
from ccai.uia.platforms.macos.applications.apptextedit import AppTextEdit
from ccai.uia.platforms.macos.applications.apptv import AppTV

from ccai.uia.platforms.macos.appscript.asdatabaseevents import AsDatabaseEvents
from ccai.uia.platforms.macos.appscript.asimageevents import AsImageEvents
from ccai.uia.platforms.macos.appscript.assystemevents import AsSystemEvents

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
    AppTV.BUNDLE_IDENTIFIER: AppTV,
    AsDatabaseEvents.BUNDLE_IDENTIFIER: AsDatabaseEvents,
    AsImageEvents.BUNDLE_IDENTIFIER: AsImageEvents,
    AsSystemEvents.BUNDLE_IDENTIFIER: AsSystemEvents
}

class MacCatalog:
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
            app_type = MacApplication

        return app_type
