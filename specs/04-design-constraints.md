# Linux UI Automation - Design Constraints & Learnings

## Architecture Decisions

### Agent-Based Design ✅
**Decision:** Use agents (AccessibilityAgent, WindowManagerAgent) that elements delegate to, rather than elements directly calling platform APIs.

**Benefits:**
- Separation of concerns - elements don't need to know platform details
- Easy to mock/test - inject different agents
- Flexibility - can swap X11Agent for WaylandAgent without changing elements

**Implementation:**
- Elements store references to `_access_agent` and `_wm_agent`
- All platform-specific calls go through agents

---

## Platform Constraints

### AT-SPI (Accessibility)

**Works Well:**
- ✅ Application and window discovery
- ✅ Element tree traversal
- ✅ Table interface for LibreOffice Calc
- ✅ Text interface for reading cell content
- ✅ State queries (visible, enabled)
- ✅ Component interface for bounds/coordinates

**Limitations:**
- ⚠️ `cell.text` property returns empty for LibreOffice cells - must use `queryText().getText(0, -1)` instead
- ⚠️ `Component.grabFocus()` works for widgets but may not activate windows system-wide

### X11 Window Management

**Works Well:**
- ✅ Keyboard input (keydown/keyup/keypress)
- ✅ Dynamic shift key detection via keymap inspection
- ✅ Mouse click simulation
- ✅ Window finding for standard applications (gnome-calculator)

**Known Issues:**
- ❌ **Window finding fails for LibreOffice** 
  - `_find_window_recursive()` searches WM_NAME and WM_CLASS
  - None of these match: "Untitled 1 — LibreOffice Calc", "Calc", "soffice"
  - Possible causes: mangled names, special characters (em dash "—"), timing issues
  - **Impact**: Cannot activate LibreOffice windows, keyboard input doesn't work

**Retry Logic:**
- Window finding uses 3 attempts with 0.5s delay
- Still insufficient for LibreOffice

---

## Class Hierarchy Decisions

### DisplayElement as Common Base
**Rationale:** Both screen-level objects (windows/apps) and controls need bounds, position, size, visibility.

### ScreenElement for Windows/Apps
**Rationale:** Windows and applications are fundamentally different from controls - they manage z-order, have different lifecycle.

### TableElement Inherits UITable (not LinuxElement)
**Decision:** Make TableElement inherit UITable directly rather than LinuxElement.

**Rationale:**
- Tables are specialized enough to warrant direct inheritance
- Clearer type semantics - `TableElement` IS-A `UITable`
- Avoids diamond inheritance complexity

**Trade-off:** Some property duplication (bounds, position, size), but gain clarity.

---

## Test Constraints

### LibreOffice Calc Test Issues
**File:** `test_linux_libreoffice_calc_table_entry`

**Problem Flow:**
1. AT-SPI finds window/table correctly ✅
2. `main_window.activate()` calls `X11Agent.focus_window()` ❌
3. Window not found, focus fails ❌
4. `type_keys()` sends global X11 events that go nowhere ❌
5. Cell values remain empty ❌

**Workaround Options:**
1. Fix X11 window finding (preferred, but root cause unknown)
2. Use AT-SPI focus instead of X11 (may not give system-wide focus)
3. Send keys per-element via AT-SPI EditableText (limited support)
4. Use external tools (wmctrl, xdotool) for window management

### Calculator Test Success
The gnome-calculator test passes, confirming:
- X11 window finding works for standard apps
- Keyboard input (including shift detection) works correctly
- The architecture is sound

---

## Key Learnings

### 1. LibreOffice Has Unique Window Management
Unlike standard GTK apps, LibreOffice windows don't match expected X11 naming patterns. Need specialized handling.

### 2. AT-SPI vs X11 Trade-offs
- **AT-SPI**: Great for element discovery and inspection, limited for global input/focus
- **X11**: Global input/focus control, but fragile window finding
- **Best approach**: Use both - AT-SPI for discovery, X11 for control

### 3. Cell Text Reading Requires Text Interface
LibreOffice cells don't expose text via the standard `.text` property. Must explicitly:
```python
text_iface = cell.queryText()
if text_iface:
    return text_iface.getText(0, -1)
```

### 4. Timing Matters
- Window activation needs time to propagate
- Cell value updates in LibreOffice need ~1s to commit
- Retry logic is essential for reliability

---

## Dependencies

### Required Python Packages
- `python-xlib` - X11 window management and input
- `pyatspi` - AT-SPI accessibility interface
- Both must be installed for Linux automation to work

### System Requirements
- X11 display server (not Wayland, though future Wayland support possible)
- AT-SPI2 daemon running
- Applications must support AT-SPI (most GTK/Qt apps do)

---

## Future Improvements

### Priority 1: Fix LibreOffice Window Finding
Investigate actual WM_NAME/WM_CLASS used by LibreOffice:
```bash
xprop | grep -i wm_name
xprop | grep -i wm_class
```

### Priority 2: Fallback Focus Mechanism
If X11 focus fails, try AT-SPI window focus as fallback.

### Priority 3: Per-Element Keyboard Input
Implement keyboard input via AT-SPI EditableText for widgets that support it, reducing dependency on global X11 input.

### Priority 4: Wayland Support
Create WaylandAgent to replace X11Agent for Wayland systems. Will require different window management approach (likely wlroots or similar).

### Priority 5: Role-Based Factory
Add factory method to create specialized element types based on AT-SPI role:
```python
if role == "push button":
    return LinuxButton(...)
elif role == "table":
    return TableElement(...)
```
