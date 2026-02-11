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

## Declarative Automation (✅ Implemented)
Defined in `/home/myron/repos/automojo-uia/source/packages/automojo/uia/model/declarative.py`.

### Principles
Declarative automation allows defining the UI structure using "Hints" rather than procedural search logic.

### Classes
- `DeclarativeApplication`
  - Base class for application models.
  - `APPLICATION_NAME`: Name of the application to attach/launch.
  - `attach(engine) -> Optional[UIApplication]`: Attaches to the running app.
  - `launch_or_attach(engine) -> Optional[UIApplication]`: Launches or attaches.

- `ElementHint[T]`
  - Represents a UI element definition.
  - Generic `T` specifies the expected return type (e.g., `UIButton`).
  - `resolve(parent) -> Optional[T]`: Finds the element within the parent.
  - **Attributes**:
    - `name`: Name to match.
    - `role`: Role to match.
    - `path`: XPath-style search path (precedence over name/role).

- **Specialized Hints**:
  - `WindowHint`, `DialogHint`, `ButtonHint`, `TextHint`, `MenuBarHint`, `MenuHint`, `MenuItemHint`.

### XPath Syntax
Hints support a custom XPath-style syntax via the `path` attribute:
- `//`: Recursive descendant search.
- `/`: Direct child search.
- `.`: Relative to current context.
- `{key:value}`: Property filtering.
  - `*`: Wildcard (any property or value).
  - `~`: Contains operator (e.g., `{name:~Save}`).
- **Examples**:
  - `//{name:OK}`: Find descendant named "OK".
  - `/*/{role:button}`: Find grandchild that is a button.
  - `./{role:panel}`: Find direct child panel.

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
  - Implements all DisplayElement and UIElement abstract methods.
  - **Standard Search API**: `find_element(**kwargs)`, `find_elements(**kwargs)`.
  - Additional properties: `role`, `role_name`, `native_obj`.
  - Uses AT-SPI (pyatspi) for accessibility tree traversal.

- `TableElement(UITable)`
  - Specialized implementation for table/grid controls.

- `LinuxWindow(UIWindow)`
  - Window wrapper using AT-SPI accessibility tree.

- `LinuxApplication(UIApplication)`  
  - Application wrapper using AT-SPI application objects.

### Linux Automation Engine
- `LinuxAutomation(AutomationEngine)`
  - `get_application_by_name(application_name: str) -> LinuxApplication`
  - Uses AT-SPI registry to find running applications.

### X11 Window Manager Agent
Defined in `/home/myron/repos/automojo-uia/source/packages/automojo/uia/platforms/linux/agents/wm/x11_agent.py`.

---

## Base Interfaces
Defined in `/home/myron/repos/automojo-uia/source/packages/automojo/uia/platforms/base.py`.

### Foundation Classes

- `UIObject` (Abstract base for all UI objects)
  - `__repr__() -> str`

- `DisplayElement(UIObject)` (Foundation for all displayable UI objects)
  - `bounds`, `position`, `size`, `is_visible`

- `ScreenElement(DisplayElement)` (Screen-level objects: windows, applications)
  - `bring_to_front()`, `send_to_back()`

- `UIElement(DisplayElement)` (UI controls/widgets)
  - `name`, `is_enabled`, `exists`
  - `click()`, `type_keys(keys: str)`
  - **Search**:
    - `find_element(**kwargs) -> Optional[UIElement]`
    - `find_elements(**kwargs) -> List[UIElement]`
  - **Wait**:
    - `wait_for_element(timeout=10.0, **kwargs) -> UIElement`
    - `wait_until_gone(timeout=10.0) -> bool`

### UI Component Classes
All inherit from `UIElement`:
- `UIButton`, `UIText`, `UIList`, `UITable`, `UIMenuBar`, `UIMenu`, `UISubMenu`, `UIMenuItem`.

### Screen-Level Classes
- `UIWindow(ScreenElement)`
- `UIApplication(ScreenElement)`

---

## MacOS Automation
Defined in `/Users/myron/repos/automojo-uia/source/packages/automojo/uia/platforms/macos/automation.py`.

- `MacOSAutomation(AutomationEngine)`
  - `get_application_by_name(...)`

## MacOS Application Wrappers
Defined under `/Users/myron/repos/automojo-uia/source/packages/automojo/uia/platforms/macos/`.

- `MacApplication(UIApplication)`
  - Represents a running application.
  - Implements `find_element` and `find_elements` (delegates to accessibility).

- `MacWindow(UIWindow)`
  - Represents a window.

- `UiaAccessibilityElement`
  - Implements standard `find_element` and `find_elements` APIs with **wildcard support** (`*`, `~`).
  - Implements `UIElement` interface.

---

## Error Behavior
- `UIAException`: Base exception class.
- `ElementNotFoundError`: Raised when an element cannot be found.
- `InteractionError`: Raised when interaction (click, type) fails.
- `PlatformNotSupportedError`: Raised for unsupported actions.
