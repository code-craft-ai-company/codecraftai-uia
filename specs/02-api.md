# Automojo UIA API Contract

## Factory And Singleton
- `automojo.uia.factory.AutomationFactory.get_automation_engine() -> AutomationEngine`
  - Returns a platform-specific automation engine.
  - MacOS: returns `MacOSAutomation`.
  - Linux: returns `LinuxAutomation`.
  - Windows: raises `NotImplementedError`.
- `automojo.uia.wellknown.UiaControllerSingleton() -> Any`
  - Returns a singleton instance of the platform-specific engine.

---

## Linux Automation (✅ Implemented)

### Architecture
Linux implementation uses an agent-based architecture:
- **AccessibilityAgent** - Wraps AT-SPI for element inspection and interaction
- **WindowManagerAgent** - Wraps X11/Wayland for window management and input
- Platform wrappers delegate to agents for platform-specific operations

### Linux Elements
Defined in `/home/myron/repos/automojo-uia/source/packages/automojo/uia/platforms/linux/wrappers/`.

- `LinuxElement(UIElement)`
  - Implements all DisplayElement and UIElement abstract methods
  - Additional properties: `role`, `role_name`, `native_obj`
  - Additional methods: `grab_focus()`, `set_value(value: float)`, `find_descendant(name, role, max_depth)`
  - Uses AT-SPI (pyatspi) for accessibility tree traversal

- `TableElement(UITable)`
  - Specialized implementation for table/grid controls (e.g., LibreOffice Calc)
  - Additional methods: `clear_selection()`, `select_from_table(row, col)`, `get_table_cell(row, col)`
  - Uses AT-SPI Table interface for table-specific operations

- `LinuxWindow(UIWindow)`
  - Window wrapper using AT-SPI accessibility tree
  - Window activation attempts X11 focus with fallback to application name

- `LinuxApplication(UIApplication)`  
  - Application wrapper using AT-SPI application objects

### Linux Automation Engine
- `LinuxAutomation(AutomationEngine)`
  - `get_application_by_name(application_name: str) -> LinuxApplication`
  - Uses AT-SPI registry to find running applications

### X11 Window Manager Agent
Defined in `/home/myron/repos/automojo-uia/source/packages/automojo/uia/platforms/linux/agents/wm/x11_agent.py`.

- `X11WindowManagerAgent(WindowManagerAgent)`
  - Keyboard input:
    - `keydown(key: str) -> None`
    - `keyup(key: str) -> None`
    - `keypress(key: str) -> None`
    - `send_keys(window, keys: str) -> None`
    - Dynamic shift detection via X11 keymap inspection
  - Window management:
    - `focus_window(window_name: str) -> bool` - With retry logic (3 attempts)
    - `get_active_window() -> Any`
  - Mouse:
    - `click(x: int, y: int) -> None`

### Known Constraints
- **Window Finding Issue**: X11 window finding fails for LibreOffice applications despite working for standard apps like gnome-calculator. Root cause under investigation.
- **Focus Dependency**: Global keyboard input via X11 requires window focus. Alternative per-element input via AT-SPI EditableText may be needed.

---

## Base Interfaces
Defined in `/home/myron/repos/automojo-uia/source/packages/automojo/uia/platforms/base.py`.

### Foundation Classes

- `UIObject` (Abstract base for all UI objects)
  - `__repr__() -> str`

- `DisplayElement(UIObject)` (Foundation for all displayable UI objects)
  - `bounds: Tuple[int, int, int, int]` - Bounding rectangle (x, y, width, height)
  - `position: Tuple[int, int]` - Position (x, y)
  - `size: Tuple[int, int]` - Size (width, height)
  - `is_visible: bool`

- `ScreenElement(DisplayElement)` (Screen-level objects: windows, applications)
  - `bring_to_front() -> None`
  - `send_to_back() -> None`

- `UIElement(DisplayElement)` (UI controls/widgets)
  - `name: str`
  - `is_enabled: bool`
  - `click() -> None`
  - `type_keys(keys: str) -> None`

### UI Component Classes

All inherit from `UIElement`:

- `UIButton`
  - `label: str`
  - `double_click() -> None`

- `UIText`
  - `text: str`
  - `is_editable: bool`
  - `get_text() -> str`
  - `set_text(text: str) -> None`
  - `clear() -> None`

- `UIList`
  - `item_count: int`
  - `get_item(index: int) -> Optional[UIElement]`
  - `select_item(index: int) -> None`
  - `scroll_to_item(index: int) -> None`

- `UITable`
  - `row_count: int`
  - `column_count: int`
  - `get_cell(row: int, column: int) -> Optional[UIElement]`
  - `select_cell(row: int, column: int) -> None`
  - `get_cell_value(row: int, column: int) -> str`

- `UIMenuBar`
  - `get_menu(name: str) -> Optional[UIMenu]`
  - `get_menus() -> List[UIMenu]`

- `UIMenu`
  - `is_open: bool`
  - `open() -> None`
  - `close() -> None`
  - `get_item(name: str) -> Optional[UIMenuItem]`
  - `get_items() -> List[UIMenuItem]`

- `UISubMenu(UIMenu)`
  - `parent_menu: Optional[UIMenu]`
  - Inherits all UIMenu properties and methods

- `UIMenuItem`
  - `is_checked: bool`
  - `is_separator: bool`
  - `invoke() -> None`

### Screen-Level Classes

- `UIWindow(ScreenElement)`
  - `name: str`
  - `title: str`
  - `click() -> None`
  - `type_keys(keys: str) -> None`
  - `close() -> None`
  - `maximize() -> None`
  - `minimize() -> None`
  - `restore() -> None`

- `UIApplication(ScreenElement)`
  - `name: str`
  - `identifier: str`
  - `click() -> None`
  - `type_keys(keys: str) -> None`
  - `launch() -> None`
  - `terminate() -> None`
  - `activate() -> None`
  - `get_windows() -> List[UIWindow]`

- `AutomationEngine`
  - `get_application_by_name(application_name: str) -> UIApplication`

---

## MacOS Automation
Defined in `/Users/myron/repos/automojo-uia/source/packages/automojo/uia/platforms/macos/automation.py`.

- `MacOSAutomation(AutomationEngine)`
  - `catalog: UiaCatalog`
  - `database_events: AsDatabaseEvents`
  - `image_events: AsImageEvents`
  - `system_events: AsSystemEvents`
  - `workspace: UiaWorkspace`
  - `get_application_by_name(application_name: str, auto_launch: bool = True, metadata_refresh: bool = False) -> UiaApplication`
    - Returns a `UiaApplication` wrapper.
    - If running, returns a typed wrapper using `UiaCatalog`.
    - If not running and `auto_launch=True`, attempts to launch.
  - `lookup_scripting_process_by_name(application_name: str) -> SbProcess | None`
    - Returns a scripting process wrapper if found.

## MacOS Workspace And Metadata
Defined in `/Users/myron/repos/automojo-uia/source/packages/automojo/uia/platforms/macos/wrappers/`.

- `UiaWorkspace`
  - `runningApplications() -> List[UiaApplication]`
  - `launch_application_by_name(application_name: str, metadata_refresh: bool = False) -> UiaApplication`
  - `lookup_application_metadata_by_name(application_name: str, metadata_refresh: bool = False) -> UiaMetadataItem`
  - `query_application_metadata() -> Dict[str, UiaMetadataItem]`
- `UiaMetadataQuery`
  - `run() -> List[UiaMetadataItem]`
  - Raises `TimeoutError` on query timeout.

## MacOS Application Wrappers
Defined under `/Users/myron/repos/automojo-uia/source/packages/automojo/uia/platforms/macos/`.

- `UiaApplication`
  - Properties: `bundle_identifier`, `bundle_url`, `executable_url`, `icon`, `is_frontmost`, `launch_date`,
    `localized_name`, `owns_menu_bar`, `process_identifier`, `sb_process`
  - Actions: `activate()`, `focus()`, `hide()`, `quit()`, `terminate()`, `unfocus()`, `unhide()`
  - `get_windows() -> List[UiaWindow]`
  - `windows() -> List[SbWindow]` (scripting windows from the application process)
  - `find_first_by_role(...)`, `find_by_title(...)`, `find_by_tytle(...)`, `find_by_contents(...)`
  - `send_keys(keys: str) -> None`
- `UiaAccessibilityApplication`
  - `windows() -> List[UiaAccessibilityElement]`
- `UiaAccessibilityElement`
  - `name`, `role`, `is_visible`, `is_enabled`
  - `click()`, `type_keys(keys: str)`, `focus()`
  - `children() -> List[UiaAccessibilityElement]`
  - `find_first_by_role(role: str, include_self: bool = False) -> Optional[UiaAccessibilityElement]`
  - `find_by_title(title: str, include_self: bool = False, expression: bool = False) -> List[UiaAccessibilityElement]`
  - `find_by_tytle(title: str, include_self: bool = False, expression: bool = False) -> List[UiaAccessibilityElement]`
  - `find_by_contents(contents: str, include_self: bool = False, expression: bool = False) -> List[UiaAccessibilityElement]`
- `UiaWindow`
  - `is_minimized() -> bool`
  - `is_focused() -> bool`
  - `find_first_by_role(...)`, `find_by_title(...)`, `find_by_tytle(...)`, `find_by_contents(...)`
- `UiaCatalog`
  - Maps MacOS bundle identifiers to wrapper subclasses for well-known apps.

---

## Error Behavior
- Unsupported platforms raise `NotImplementedError`.
- Metadata lookup raises `ValueError` when no application metadata is found.
- Metadata query raises `TimeoutError` on query timeout.
