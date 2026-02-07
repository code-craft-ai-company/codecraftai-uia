# Automojo UIA API Contract

## Factory And Singleton
- `automojo.uia.factory.AutomationFactory.get_automation_engine() -> AutomationEngine`
  - Returns a platform-specific automation engine.
  - MacOS: returns `MacOSAutomation`.
  - Windows/Linux: raises `NotImplementedError`.
- `automojo.uia.wellknown.UiaControllerSingleton() -> Any`
  - Returns a singleton instance of the platform-specific engine.

## Base Interfaces
Defined in `/Users/myron/repos/automojo-uia/source/packages/automojo/uia/platforms/base.py`.

- `UIObject`
  - `__repr__() -> str`
- `UIElement(UIObject)`
  - `name: str`
  - `is_visible: bool`
  - `is_enabled: bool`
  - `click() -> None`
  - `type_keys(keys: str) -> None`
- `UIWindow(UIElement)`
  - `title: str`
  - `close() -> None`
  - `maximize() -> None`
  - `minimize() -> None`
  - `restore() -> None`
- `UIApplication(UIObject)`
  - `name: str`
  - `identifier: str`
  - `launch() -> None`
  - `terminate() -> None`
  - `activate() -> None`
  - `get_windows() -> List[UIWindow]`
- `AutomationEngine`
  - `get_application_by_name(application_name: str) -> UIApplication`

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

## Error Behavior
- Unsupported platforms raise `NotImplementedError`.
- Metadata lookup raises `ValueError` when no application metadata is found.
- Metadata query raises `TimeoutError` on query timeout.
