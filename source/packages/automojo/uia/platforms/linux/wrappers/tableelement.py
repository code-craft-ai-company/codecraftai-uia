import weakref
from typing import Any, Tuple, Optional
from automojo.uia.platforms.base import UITable, UICell, UIElement
from automojo.uia.platforms.linux.wrappers.uiaelement import LinuxElement
from automojo.uia.platforms.linux.agents.linuxbaseagents import AccessibilityAgent, WindowManagerAgent


class CellElement(LinuxElement, UICell):
    """
    Wrapper for table cells in Linux automation.
    """
    def __init__(self, native_obj: Any, access_agent: AccessibilityAgent, wm_agent: WindowManagerAgent, row: int, col: int, parent: Optional[UIElement] = None):
        super().__init__(native_obj, access_agent, wm_agent, parent)
        self._row = row
        self._col = col

    @property
    def row(self) -> int:
        return self._row

    @property
    def column(self) -> int:
        return self._col

    @property
    def text(self) -> str:
        return self.get_text()

    def get_text(self) -> str:
        # Try Text interface first (LibreOffice cells use this)
        try:
            text_iface = self._native_obj.queryText()
            if text_iface:
                return text_iface.getText(0, -1)
        except Exception:
            pass
        
        # Fallback to name
        return self.name if self.name else ""

    def set_text(self, text: str) -> None:
        # For spreadsheet cells, we usually need to type the value
        # But we can try EditableText? 
        # For consistency with current tests, we'll use type_keys with enter
        self.click()
        # Give focus a moment
        import time
        time.sleep(0.1)
        self.type_keys(text + "\n")
  
    def clear(self) -> None:
        # Todo: Implement clear (maybe delete key?)
        pass

    @property
    def is_editable(self) -> bool:
        # Check states
        states = self.access_agent.get_states(self._native_obj)
        for state in states:
            if str(state) == "editable" or str(state).endswith("EDITABLE"):
                return True
        return False
    
    def __repr__(self):
        return f"CellElement<Row={self.row}, Col={self.column}, Text='{self.text}'>"


class TableElement(UITable):
    """
    Specialized wrapper for table elements (e.g., LibreOffice Calc spreadsheets).
    Provides table-specific manipulation methods using AT-SPI Table interface.
    """
    
    def __init__(self, native_obj: Any, access_agent: AccessibilityAgent, wm_agent: WindowManagerAgent, parent: Optional[UIElement] = None):
        # We need to initialize LinuxElement mixin if we inherited from it, 
        # but pure UITable inherits UIElement. TableElement structure in file is:
        # class TableElement(UITable):
        # But it implements Linux logic, so likely usually wraps LinuxElement or should inherit it?
        # Looking at previous file content, it inherited ONLY UITable, but took agents in init.
        # It replicates some LinuxElement properties.
        # Ideally it should inherit LinuxElement too to get weakref logic for agents.
        # Let's check imports. It imports LinuxElement.
        # If I change it to inherit LinuxElement, it simplifies things.
        # But for now, I will just implement the weakref pattern here too if it doesn't inherit.
        # Update: The file content shows `class TableElement(UITable):`
        # So I must implement weakref for agents here manually or change inheritance.
        # Changing inheritance to `class TableElement(LinuxElement, UITable):` is better but risky for MRO.
        # Let's stick to manual weakref here to match existing structure, OR use LinuxElement composition?
        # Actually, `TableElement` has `_native_obj` etc. It IS a LinuxElement in spirit.
        # Let's use weakref here manually to avoid big inheritance changes.
        
        super().__init__(parent)
        self._native_obj = native_obj
        self._access_agent = weakref.ref(access_agent)
        self._wm_agent = weakref.ref(wm_agent) if wm_agent else None
    
    @property
    def access_agent(self) -> AccessibilityAgent:
        return self._access_agent()

    @property
    def wm_agent(self) -> Optional[WindowManagerAgent]:
        if self._wm_agent:
            return self._wm_agent()
        return None

    # DisplayElement properties
    @property
    def bounds(self) -> Tuple[int, int, int, int]:
        """Returns (x, y, width, height) bounding rectangle."""
        coords = self.access_agent.get_coordinates(self._native_obj)
        if coords:
            return coords
        return (0, 0, 0, 0)

    @property
    def position(self) -> Tuple[int, int]:
        """Returns (x, y) position."""
        bounds = self.bounds
        return (bounds[0], bounds[1])

    @property
    def size(self) -> Tuple[int, int]:
        """Returns (width, height) size."""
        bounds = self.bounds
        return (bounds[2], bounds[3])
    
    @property
    def is_visible(self) -> bool:
        """True if the table is visible."""
        states = self.access_agent.get_states(self._native_obj)
        for state in states:
            if str(state) == "visible" or str(state).endswith("VISIBLE"):
                return True
        return False
    
    @property
    def name(self) -> str:
        """The name of the table."""
        return self.access_agent.get_name(self._native_obj)
    
    @property
    def is_enabled(self) -> bool:
        """True if the table is enabled."""
        states = self.access_agent.get_states(self._native_obj)
        for state in states:
            if str(state) == "enabled" or str(state).endswith("ENABLED"):
                return True
        return False
    
    # UITable properties
    @property
    def row_count(self) -> int:
        """Returns the number of rows in the table."""
        try:
            table = self._native_obj.queryTable()
            if table:
                return table.nRows
        except:
            pass
        return 0
    
    @property
    def column_count(self) -> int:
        """Returns the number of columns in the table."""
        try:
            table = self._native_obj.queryTable()
            if table:
                return table.nColumns
        except:
            pass
        return 0
    
    def click(self) -> None:
        """Clicks on the table."""
        if self.access_agent.do_action(self._native_obj, 0):
            return
        raise NotImplementedError("Click action not supported by this table.")
    
    def type_keys(self, keys: str) -> None:
        """Types keys into the table."""
        if not self.wm_agent:
            raise NotImplementedError("WM Agent not available for typing keys.")
        self.wm_agent.send_keys(None, keys)
    
    def get_cell(self, row: int, column: int) -> Optional[CellElement]:
        """Gets a cell element from a table at the specified row and column."""
        try:
            table = self._native_obj.queryTable()
            if table:
                cell = table.getAccessibleAt(row, column)
                if cell:
                    return CellElement(cell, self.access_agent, self.wm_agent, row, column, parent=self)
        except Exception as e:
            print(f"Error getting table cell ({row},{column}): {e}")
        return None
    
    def get_range(self, start_row: int, start_column: int, end_row: int, end_column: int) -> list[CellElement]:
        """Gets a range of cells."""
        cells = []
        for r in range(start_row, end_row + 1):
            for c in range(start_column, end_column + 1):
                cell = self.get_cell(r, c)
                if cell:
                    cells.append(cell)
        return cells

    def select_cell(self, row: int, column: int) -> None:
        """Selects a cell in a table at the given row and column."""
        self.select_from_table(row, column)
    
    def __repr__(self) -> str:
        return f"TableElement<{self.name}>"
    
    def clear_selection(self) -> None:
        """Clears the current selection in a table via AT-SPI Table interface."""
        try:
            table = self._native_obj.queryTable()
            selection = self._native_obj.querySelection()
            if selection:
                # Clear all selected children
                for i in range(selection.nSelectedChildren):
                    selection.deselectChild(i)
        except Exception:
            pass

    def select_from_table(self, row: int, col: int) -> bool:
        """Selects a cell in a table at the given row and column."""
        try:
            table = self._native_obj.queryTable()
            if table:
                # Get the cell at this position
                cell = table.getAccessibleAt(row, col)
                if cell:
                    # Try to select it via Selection interface
                    try:
                        selection = self._native_obj.querySelection()
                        if selection:
                            # Get the child index for this cell
                            index = table.getIndexAt(row, col)
                            selection.selectChild(index)
                            return True
                    except:
                        pass
                return True
        except Exception:
            pass
        return False

    def get_table_cell(self, row: int, col: int) -> CellElement:
        """Deprecated alias for get_cell."""
        return self.get_cell(row, col)

    def get_cell_value(self, row: int, col: int) -> str:
        """Gets the text value of a cell."""
        cell = self.get_cell(row, col)
        if cell:
            return cell.text
        return ""
