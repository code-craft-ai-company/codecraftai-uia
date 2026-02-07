
from typing import Any
try:
    import pyatspi
except ImportError:
    pyatspi = None

from automojo.uia.platforms.base import UIElement

class LinuxElement(UIElement):
    """
        Base wrapper for Linux UI elements using pyatspi.
    """
    def __init__(self, native_obj: Any):
        self._native_obj = native_obj

    @property
    def native_obj(self) -> Any:
        return self._native_obj

    @property
    def name(self) -> str:
        return self._native_obj.name

    @property
    def text(self) -> str:
        """
            Gets the text content of the element using Test or Value interface.
        """
        try:
            text_iface = self._native_obj.queryText()
            # getText(start_offset, end_offset). -1 usually means end.
            return text_iface.getText(0, -1)
        except Exception:
            pass
            
        try:
            value_iface = self._native_obj.queryValue()
            return str(value_iface.currentValue)
        except Exception:
            pass
            
        return ""

    @property
    def is_visible(self) -> bool:
        if not pyatspi:
            return False
        states = self._native_obj.getState()
        return states.contains(pyatspi.STATE_VISIBLE)

    @property
    def role(self) -> Any:
        try:
             return self._native_obj.getRole()
        except:
             return None

    @property
    def role_name(self) -> str:
        try:
             return self._native_obj.getRoleName()
        except:
             return "Unknown"

    @property
    def is_enabled(self) -> bool:
        if not pyatspi:
             return False
        states = self._native_obj.getState()
        return states.contains(pyatspi.STATE_ENABLED)
    
    def grab_focus(self) -> bool:
        """
            Attempts to grab focus for the element.
        """
        try:
            component = self._native_obj.queryComponent()
            return component.grabFocus()
        except Exception:
            return False

    def click(self) -> None:
        """
            Attempts to perform a click action via the Action interface.
        """
        try:
            action = self._native_obj.queryAction()
            if action.nActions > 0:
                action.doAction(0)
                return
        except Exception:
            pass
        
        raise NotImplementedError("Click action failed or not supported by this element.")

    def _char_to_keysym(self, char: str) -> str:
        """
            Maps a character to an X11 keysym string.
        """
        if char.isalnum():
            return char
        
        mapping = {
            ' ': 'space',
            '\n': 'Return',
            '\r': 'Return',
            '\t': 'Tab',
            '!': 'exclam',
            '"': 'quotedbl',
            '#': 'numbersign',
            '$': 'dollar',
            '%': 'percent',
            '&': 'ampersand',
            '\'': 'apostrophe',
            '(': 'parenleft',
            ')': 'parenright',
            '*': 'asterisk',
            '+': 'plus',
            ',': 'comma',
            '-': 'minus',
            '.': 'period',
            '/': 'slash',
            ':': 'colon',
            ';': 'semicolon',
            '<': 'less',
            '=': 'equal',
            '>': 'greater',
            '?': 'question',
            '@': 'at',
            '[': 'bracketleft',
            '\\': 'backslash',
            ']': 'bracketright',
            '^': 'asciicircum',
            '_': 'underscore',
            '`': 'grave',
            '{': 'braceleft',
            '|': 'bar',
            '}': 'braceright',
            '~': 'asciitilde'
        }
        return mapping.get(char, char)

    def type_keys(self, keys: str) -> None:
        """
            Types keys. Uses pyatspi.Registry.generateKeyboardEvent with explicit PRESS and RELEASE.
        """
        try:
            import pyatspi
            import time
        except Exception as exc:
            raise NotImplementedError("Type keys is not available because pyatspi is unavailable.") from exc

        try:
            self.grab_focus()
            registry = pyatspi.Registry
            use_key_string = hasattr(pyatspi, "KEY_STRING")
            use_press_release = hasattr(pyatspi, "KEY_PRESSRELEASE")
            for char in keys:
                if use_key_string:
                    registry.generateKeyboardEvent(0, char, pyatspi.KEY_STRING)
                else:
                    keysym = self._char_to_keysym(char)
                    if use_press_release:
                        registry.generateKeyboardEvent(0, keysym, pyatspi.KEY_PRESSRELEASE)
                    else:
                        try:
                            registry.generateKeyboardEvent(0, keysym, pyatspi.KEY_PRESS)
                            time.sleep(0.01)
                            registry.generateKeyboardEvent(0, keysym, pyatspi.KEY_RELEASE)
                        except Exception:
                            registry.generateKeyboardEvent(0, keysym, pyatspi.KEY_SYM)
                time.sleep(0.05)
        except Exception as exc:
            raise NotImplementedError("Type keys failed using the pyatspi Registry.") from exc

    def set_text(self, text: str) -> None:
        """
            Sets the text content of the element. 
            Tries Value interface for numbers, then EditableText, then keyboard simulation.
        """
        # 1. Try Value interface if text is numeric
        try:
            float_val = float(text)
            if self.set_value(float_val):
                return
        except ValueError:
            pass

        # 2. Try EditableText interface
        try:
            editable = self._native_obj.queryEditableText()
            editable.setTextContents(text)
            return
        except Exception:
            pass
            
        # 3. Fallback to typing if editable interface is missing
        try:
            self.type_keys(text)
            try:
                import pyatspi
                # keysym for Return is "Return"
                pyatspi.Registry.generateKeyboardEvent(0, "Return", pyatspi.KEY_SYM)
            except Exception:
                pass
            return
        except NotImplementedError:
            pass
        
        raise NotImplementedError("Element does not support setting text.")

    def set_value(self, value: float) -> bool:
        """
            Sets the value using the Value interface.
        """
        try:
            val_iface = self._native_obj.queryValue()
            val_iface.currentValue = value
            return True
        except Exception:
            return False

    def find_descendant(self, name: str = None, role:str = None, max_depth: int = 10) -> 'LinuxElement':
        """
            Recursively finds a descendant by name or role.
        """
        if max_depth < 0:
            return None
        
        count = self._native_obj.childCount
        for i in range(count):
            try:
                child = self._native_obj.getChildAtIndex(i)
                child_wrapper = LinuxElement(child)
                
                match = True
                if name and child.name != name:
                    match = False
                # Role check could be added here if we imported ROLE_* constants
                
                if match:
                    return child_wrapper
                
                found = child_wrapper.find_descendant(name, role, max_depth - 1)
                if found:
                    return found
            except Exception:
                 continue
                 
        return None

    def get_table_cell(self, row: int, col: int) -> 'LinuxElement':
        """
            Returns the cell at the specified row and column if this element supports the Table interface.
        """
        try:
            table = self._native_obj.queryTable()
            cell = None
            
            # Try standard getCellAt
            try:
                cell = table.getCellAt(row, col)
            except:
                pass

            # Fallback: getIndexAt -> getChildAtIndex
            if not cell:
                index = table.getIndexAt(row, col)
                if index >= 0:
                    try:
                        # Sometimes we need to get it from the parent's child list
                        cell = self._native_obj.getChildAtIndex(index)
                    except:
                        pass
            
            if cell:
                return LinuxElement(cell)
        except Exception:
            pass
        
        return None

    def select_from_table(self, row: int, col: int) -> bool:
        """
            Selects the child at (row, col) using the Selection interface of the table.
        """
        try:
            table = self._native_obj.queryTable()
            # Get 1-D index of the cell
            # Some implementations might need child index from component, but Table usually has getIndexAt
            index = table.getIndexAt(row, col)
            
            if index >= 0:
                selection = self._native_obj.querySelection()
                return selection.selectChild(index)
        except Exception:
             pass
        
        return False

    def clear_selection(self) -> bool:
        """
            Clears the selection using the Selection interface.
        """
        try:
             selection = self._native_obj.querySelection()
             return selection.clearSelection()
        except Exception:
             pass
        return False

    def __repr__(self) -> str:
        return f"LinuxElement<{self.name}>"
