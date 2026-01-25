
from automojo.uia.platforms.macos.wrappers.uiaapplication import UiaApplication

class AppScriptEditor(UiaApplication):
    """
        Represents and instance of the 'Script Editor' application.
    """

    APPLICATION_NAME = "Script Editor"
    BUNDLE_IDENTIFIER = "com.apple.ScriptEditor2"
