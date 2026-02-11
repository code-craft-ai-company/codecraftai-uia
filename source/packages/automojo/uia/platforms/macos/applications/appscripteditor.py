
from automojo.uia.platforms.macos.wrappers.uiaapplication import MacApplication

class AppScriptEditor(MacApplication):
    """
        Represents and instance of the 'Script Editor' application.
    """

    APPLICATION_NAME = "Script Editor"
    BUNDLE_IDENTIFIER = "com.apple.ScriptEditor2"
