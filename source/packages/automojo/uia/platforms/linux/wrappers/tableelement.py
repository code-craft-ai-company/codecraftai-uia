import weakref
from typing import Any, Tuple, Optional, List
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
        self.click()
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


class TableElement(LinuxElement, UITable):
    """
    Specialized wrapper for table elements (e.g., LibreOffice Calc spreadsheets).
    Provides table-specific manipulation methods using AT-SPI Table interface.
    """
    
    def __init__(self, native_obj: Any, access_agent: AccessibilityAgent, wm_agent: WindowManagerAgent, parent: Optional[UIElement] = None):
        super().__init__(native_obj, access_agent, wm_agent, parent)
        
    # Inherit standard UIElement methods from LinuxElement (bounds, click, etc.)

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
    
    def get_range(self, start_row: int, start_column: int, end_row: int, end_column: int) -> List[CellElement]:
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
                # Try to select it via Selection interface
                try:
                    selection = self._native_obj.querySelection()
                    if selection:
                        # Get the child index for this cell
                        index = table.getIndexAt(row, col)
                        # print(f"DEBUG: Selecting child index {index} for cell ({row}, {col})")
                        did_select = selection.selectChild(index)
                        if did_select:
                             return True
                        # If selectChild returned False, continue to fallback
                        # print(f"DEBUG: selectChild({index}) returned False")
                except Exception as e:
                    # print(f"DEBUG: select_from_table inner error: {e}")
                    pass
        except Exception as e:
            # print(f"DEBUG: select_from_table outer error: {e}")
            pass
        
        # Fallback: Try to get cell and click it
        # print(f"DEBUG: select_from_table fallback to click ({row}, {col})")
        cell = self.get_cell(row, col)
        if cell:
            try:
                cell.click()
                return True
            except Exception as e:
                # print(f"DEBUG: Fallback click failed: {e}")
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
