from ccai.uia.model.declarative import (
    DeclarativeApplication,
    WindowHint,
    TextHint,
    ButtonHint,
    MenuBarHint,
    MenuHint,
    MenuItemHint,
    ElementHint
)

AX_WINDOW_ROLE = "AXWindow"
AX_BUTTON_ROLE = "AXButton"
AX_STATIC_TEXT_ROLE = "AXStaticText"


class MicrosoftExcel(DeclarativeApplication):
    """
        Declarative mapping for Microsoft Excel (MacOS).
    """

    APPLICATION_NAME = "Microsoft Excel"
    APPLICATION_COMMAND = "open -a 'Microsoft Excel'"

    StartDialog = WindowHint(role=AX_WINDOW_ROLE, identifier="DocStage")
    """Excel start dialog shown before a workbook is opened."""

    MainWindow = WindowHint(role=AX_WINDOW_ROLE)
    """Primary Excel window."""

    StartBlankWorkbook = ButtonHint(name="Blank Workbook", role=AX_BUTTON_ROLE)
    StartCreate = ButtonHint(name="Create", role=AX_BUTTON_ROLE)
    StartCancel = ButtonHint(name="Cancel", role=AX_BUTTON_ROLE)
    StartTabNew = ButtonHint(name="New", role="AXRadioButton")
    StartTabRecent = ButtonHint(name="Recent", role="AXRadioButton")
    StartTabOpen = ButtonHint(name="Open", role="AXRadioButton")

    @classmethod
    def resolve_workbook_window(cls, app):
        """
            Resolves the primary workbook window, skipping the start dialog when present.

            :param app: The Excel application instance.
            :returns: The workbook window or None.
        """
        if app is None:
            return None

        focused = None
        try:
            focused = app.accessibility.find_first_by_role(role="AXWindow", include_self=False)
        except Exception:
            focused = None

        if focused is not None:
            try:
                title = focused.title
            except Exception:
                title = ""

            if title != "Open new and recent files":
                native_obj = getattr(focused, "native_obj", None)
                identifier = ""
                if native_obj is not None and hasattr(native_obj, "identifier"):
                    try:
                        identifier = native_obj.identifier
                    except Exception:
                        identifier = ""

                if identifier != "DocStage":
                    return focused

        try:
            windows = app.get_windows()
        except Exception:
            windows = []

        for window in windows:
            try:
                title = window.title
            except Exception:
                title = ""

            if title == "Open new and recent files":
                continue

            native_obj = getattr(window, "native_obj", None)
            identifier = ""
            if native_obj is not None and hasattr(native_obj, "identifier"):
                try:
                    identifier = native_obj.identifier
                except Exception:
                    identifier = ""

            if identifier == "DocStage":
                continue

            return window

        return None

    @classmethod
    def resolve_focused_window(cls, app):
        """
            Resolves the focused window and identifies it by known hints.

            :param app: The Excel application instance.
            :returns: A tuple of (window_type, window) or (None, None).
        """
        if app is None:
            return None, None

        focused = None
        try:
            focused = app.accessibility.find_first_by_role(role="AXWindow", include_self=False)
        except Exception:
            focused = None

        if focused is None:
            return None, None

        try:
            title = focused.title
        except Exception:
            title = ""

        if title == "Open new and recent files":
            return "start_dialog", focused

        native_obj = getattr(focused, "native_obj", None)
        identifier = ""
        if native_obj is not None and hasattr(native_obj, "identifier"):
            try:
                identifier = native_obj.identifier
            except Exception:
                identifier = ""

        if identifier == "DocStage":
            return "start_dialog", focused

        return "workbook", focused

    RibbonTabGroup = ElementHint(role="AXTabGroup")
    """Ribbon tab group containing tab selectors."""

    RibbonTabHome = ButtonHint(name="Home", role="AXRadioButton")
    RibbonTabInsert = ButtonHint(name="Insert", role="AXRadioButton")
    RibbonTabDraw = ButtonHint(name="Draw", role="AXRadioButton")
    RibbonTabPageLayout = ButtonHint(name="Page Layout", role="AXRadioButton")
    RibbonTabFormulas = ButtonHint(name="Formulas", role="AXRadioButton")
    RibbonTabData = ButtonHint(name="Data", role="AXRadioButton")
    RibbonTabReview = ButtonHint(name="Review", role="AXRadioButton")
    RibbonTabView = ButtonHint(name="View", role="AXRadioButton")
    RibbonTabAcrobat = ButtonHint(name="Acrobat", role="AXRadioButton")

    MenuBar = MenuBarHint(role="AXMenuBar")
    """Main application menu bar."""

    MenuApple = MenuItemHint(name="Apple", role="AXMenuBarItem")
    MenuExcel = MenuItemHint(name="Excel", role="AXMenuBarItem")
    MenuFile = MenuItemHint(name="File", role="AXMenuBarItem")
    MenuEdit = MenuItemHint(name="Edit", role="AXMenuBarItem")
    MenuView = MenuItemHint(name="View", role="AXMenuBarItem")
    MenuInsert = MenuItemHint(name="Insert", role="AXMenuBarItem")
    MenuFormat = MenuItemHint(name="Format", role="AXMenuBarItem")
    MenuTools = MenuItemHint(name="Tools", role="AXMenuBarItem")
    MenuData = MenuItemHint(name="Data", role="AXMenuBarItem")
    MenuWindow = MenuItemHint(name="Window", role="AXMenuBarItem")
    MenuHelp = MenuItemHint(name="Help", role="AXMenuBarItem")

    AppleMenu = MenuHint(role="AXMenu")
    ExcelMenu = MenuHint(role="AXMenu")
    FileMenu = MenuHint(role="AXMenu")
    EditMenu = MenuHint(role="AXMenu")
    ViewMenu = MenuHint(role="AXMenu")
    InsertMenu = MenuHint(role="AXMenu")
    FormatMenu = MenuHint(role="AXMenu")
    ToolsMenu = MenuHint(role="AXMenu")
    DataMenu = MenuHint(role="AXMenu")
    WindowMenu = MenuHint(role="AXMenu")
    HelpMenu = MenuHint(role="AXMenu")
    """File menu container (resolve from MenuFile)."""

    # Apple menu items
    AppleAboutThisMac = MenuItemHint(name="About This Mac", role="AXMenuItem")
    AppleSystemSettings = MenuItemHint(name="System Settings…", role="AXMenuItem")
    AppleForceQuit = MenuItemHint(name="Force Quit…", role="AXMenuItem")

    # Excel menu items
    ExcelAbout = MenuItemHint(name="About Microsoft Excel", role="AXMenuItem")
    ExcelPreferences = MenuItemHint(name="Preferences...", role="AXMenuItem")
    ExcelHide = MenuItemHint(name="Hide Excel", role="AXMenuItem")

    FileNew = MenuItemHint(name="New", role="AXMenuItem")
    FileNewFromTemplate = MenuItemHint(name="New from Template...", role="AXMenuItem")
    FileOpen = MenuItemHint(name="Open...", role="AXMenuItem")
    FileClose = MenuItemHint(name="Close", role="AXMenuItem")
    FileSave = MenuItemHint(name="Save", role="AXMenuItem")
    FileSaveAs = MenuItemHint(name="Save As...", role="AXMenuItem")
    FileRename = MenuItemHint(name="Rename...", role="AXMenuItem")

    # Edit menu items
    EditCut = MenuItemHint(name="Cut", role="AXMenuItem")
    EditCopy = MenuItemHint(name="Copy", role="AXMenuItem")
    EditPaste = MenuItemHint(name="Paste", role="AXMenuItem")
    EditSelectAll = MenuItemHint(name="Select All", role="AXMenuItem")

    # View menu items
    ViewNormal = MenuItemHint(name="Normal", role="AXMenuItem")
    ViewPageLayout = MenuItemHint(name="Page Layout", role="AXMenuItem")
    ViewRibbon = MenuItemHint(name="Ribbon", role="AXMenuItem")
    ViewFormulaBar = MenuItemHint(name="Formula Bar", role="AXMenuItem")

    # Insert menu items
    InsertSheet = MenuItemHint(name="Sheet", role="AXMenuItem")
    InsertChart = MenuItemHint(name="Chart", role="AXMenuItem")
    InsertTable = MenuItemHint(name="Table", role="AXMenuItem")

    # Format menu items
    FormatCells = MenuItemHint(name="Cells...", role="AXMenuItem")
    FormatRow = MenuItemHint(name="Row", role="AXMenuItem")
    FormatColumn = MenuItemHint(name="Column", role="AXMenuItem")

    # Tools menu items
    ToolsSpelling = MenuItemHint(name="Spelling...", role="AXMenuItem")
    ToolsCheckAccessibility = MenuItemHint(name="Check Accessibility", role="AXMenuItem")

    # Data menu items
    DataSort = MenuItemHint(name="Sort...", role="AXMenuItem")
    DataAutoFilter = MenuItemHint(name="AutoFilter", role="AXMenuItem")
    DataClearFilters = MenuItemHint(name="Clear Filters", role="AXMenuItem")

    # Window menu items
    WindowMinimize = MenuItemHint(name="Minimize", role="AXMenuItem")
    WindowZoom = MenuItemHint(name="Zoom", role="AXMenuItem")
    WindowNewWindow = MenuItemHint(name="New Window", role="AXMenuItem")

    # Help menu items
    HelpExcel = MenuItemHint(name="Excel Help", role="AXMenuItem")
    HelpFeedback = MenuItemHint(name="Feedback", role="AXMenuItem")

    # Formula bar controls
    ButtonFx = ButtonHint(name="FxButton", role=AX_BUTTON_ROLE)
    ButtonEnter = ButtonHint(name="EnterButton", role=AX_BUTTON_ROLE)
    ButtonCancel = ButtonHint(name="CancelButton", role=AX_BUTTON_ROLE)
    ButtonExpand = ButtonHint(name="ExpandButton", role=AX_BUTTON_ROLE)

    # Quick access / common controls
    ButtonSave = ButtonHint(name="Save", role=AX_BUTTON_ROLE)
    ButtonSaveAs = ButtonHint(name="Save As", role=AX_BUTTON_ROLE)
    ButtonHome = ButtonHint(name="Home", role=AX_BUTTON_ROLE)
    ButtonShare = ButtonHint(name="Share", role=AX_BUTTON_ROLE)
    ButtonComments = ButtonHint(name="Comments", role=AX_BUTTON_ROLE)
    ButtonFeedback = ButtonHint(name="Feedback", role=AX_BUTTON_ROLE)

    # Zoom and status bar
    ButtonZoomOut = ButtonHint(name="Zoom Out", role=AX_BUTTON_ROLE)
    ButtonZoomIn = ButtonHint(name="Zoom In", role=AX_BUTTON_ROLE)
    ButtonZoom100 = ButtonHint(name="100%", role=AX_BUTTON_ROLE)
    StatusReady = TextHint(name="Ready", role=AX_STATIC_TEXT_ROLE)

    # Editing controls
    ButtonCut = ButtonHint(name="Cut", role=AX_BUTTON_ROLE)
    ButtonIncreaseFont = ButtonHint(name="Increase Font Size", role=AX_BUTTON_ROLE)
    ButtonDecreaseFont = ButtonHint(name="Decrease Font Size", role=AX_BUTTON_ROLE)
    ButtonIncreaseIndent = ButtonHint(name="Increase Indent", role=AX_BUTTON_ROLE)
    ButtonDecreaseIndent = ButtonHint(name="Decrease Indent", role=AX_BUTTON_ROLE)
    ButtonPercentStyle = ButtonHint(name="Percent Style", role=AX_BUTTON_ROLE)
    ButtonCommaStyle = ButtonHint(name="Comma Style", role=AX_BUTTON_ROLE)
    ButtonIncreaseDecimal = ButtonHint(name="Increase Decimal", role=AX_BUTTON_ROLE)
    ButtonDecreaseDecimal = ButtonHint(name="Decrease Decimal", role=AX_BUTTON_ROLE)

    # Miscellaneous controls
    ButtonAddIns = ButtonHint(name="Add-ins", role=AX_BUTTON_ROLE)
    ButtonAddInsUnicode = ButtonHint(name="Add‑ins", role=AX_BUTTON_ROLE)
    ButtonCopilot = ButtonHint(name="Copilot", role=AX_BUTTON_ROLE)
    ButtonCreatePdf = ButtonHint(name="Create PDF and share link", role=AX_BUTTON_ROLE)
    ButtonCantRepeat = ButtonHint(name="Can't Repeat", role=AX_BUTTON_ROLE)

    # Document title label (AXIdentifier)
    DocumentTitleLabel = TextHint(name="CUIDocumentShellWindowTitleLabel", role=AX_STATIC_TEXT_ROLE)
