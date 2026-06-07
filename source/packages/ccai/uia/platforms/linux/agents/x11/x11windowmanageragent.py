
from typing import Any, List
import sys
import time

try:
    from Xlib import X, display, XK
    from Xlib.ext import xtest, randr
    from Xlib.protocol import event
except ImportError:
    pass

from ccai.uia.platforms.linux.agents.linuxbaseagents import WindowManagerAgent

class X11WindowManagerAgent(WindowManagerAgent):
    """
    Concrete implementation of WindowManagerAgent using python-xlib (X11).
    """
    def __init__(self):
        try:
             import os
             # Wayland adds a "fake" display (typically ":1") that freezes when trying to get a connection
             # Force use of :0 which is the XWayland display that actually works
             # Thanks to SamuMazzi - https://github.com/SamuMazzi for pointing out this issue
             display_str = ':0'
             self._display = display.Display(display_str)
        except Exception as e:
             import traceback
             print(f"X11 Agent initialization error: {e}")
             print(traceback.format_exc())
             raise ImportError(f"Failed to connect to X11 display: {e}")

    def _find_window_recursive(self, parent_window, name: str, debug=False) -> Any:
        try:
            children = parent_window.query_tree().children
            for child in children:

                try:
                    # Check if mapped/viewable first to avoid internal windows
                    try:
                        attrs = child.get_attributes()
                        if attrs.map_state != X.IsViewable:
                            continue
                    except:
                        pass

                    wm_name = child.get_wm_name()
                    if isinstance(wm_name, bytes):
                         wm_name = wm_name.decode('utf-8', 'ignore')
                    
                    wm_class = child.get_wm_class()
                    
                    if debug and (wm_name or wm_class):
                        print(f"  DEBUG Window: name='{wm_name}', class='{wm_class}'")
                         
                    match = False
                    if wm_name and name.lower() in wm_name.lower():
                        match = True
                    
                    if not match:
                        if wm_class:
                            for cls in wm_class:
                                if isinstance(cls, bytes):
                                     cls = cls.decode('utf-8', 'ignore')
                                if name.lower() in cls.lower():
                                    match = True
                                    break
                    
                    if match:
                         # Extra check: valid window?
                         return child
                    
                    # Recurse
                    found = self._find_window_recursive(child, name, debug=False)  # Only debug top level
                    if found:
                        return found
                except:
                    continue
        except:
            pass
        
        return None

    def get_all_windows(self) -> list:
        """Returns all windows from the root window."""
        windows = []
        try:
            root = self._display.screen().root
            self._collect_windows_recursive(root, windows)
        except:
            pass
        return windows
    
    def _collect_windows_recursive(self, parent_window, windows: list) -> None:
        """Helper to recursively collect all viewable windows."""
        try:
            children = parent_window.query_tree().children
            for child in children:
                try:
                    attrs = child.get_attributes()
                    if attrs.map_state == X.IsViewable:
                        wm_name = child.get_wm_name()
                        if wm_name:  # Only include windows with names
                            windows.append(child)
                    self._collect_windows_recursive(child, windows)
                except:
                    continue
        except:
            pass
    
    def get_default_display(self) -> Any:
        """Returns the display object."""
        return self._display

    def get_active_window(self) -> Any:
        try:
            return self._display.get_input_focus().focus
        except:
            return None

    def focus_window(self, window_name: str, max_attempts: int = 3, retry_delay: float = 0.5) -> bool:
        """
        Attempts to find and focus a window by name with retry logic.
        
        Args:
            window_name: Name to search for (partial match in WM_NAME or WM_CLASS)
            max_attempts: Maximum number of attempts to find the window
            retry_delay: Delay in seconds between retry attempts
            
        Returns:
            True if window was found and focused, False otherwise
        """
        for attempt in range(max_attempts):
            if attempt > 0:
                time.sleep(retry_delay)
            
            root = self._display.screen().root
            # Debug on first attempt to see what windows exist
            target_win = self._find_window_recursive(root, window_name, debug=False)
            
            if not target_win:
                if attempt == max_attempts - 1:
                    # Only print failure on final attempt to reduce spam
                    print(f"X11Agent: Window '{window_name}' not found (likely a Wayland app)")
                continue

            try:
                # 1. Map and Raise
                target_win.configure(stack_mode=X.Above)
                target_win.map()
                self._display.sync()
                
                # 2. Set Input Focus
                self._display.set_input_focus(target_win, X.RevertToParent, X.CurrentTime)
                self._display.sync()
                time.sleep(0.1)
                return True
            except Exception as e:
                if attempt == max_attempts - 1:
                    print(f"X11Agent: Focus failed: {e}")
                    return False
                continue
        
        return False

    def _setup_keymap(self):
        """
        Initializes the XlibKeyboardMap.
        """
        if hasattr(self, '_keymap_setup'):
            return

        self._keymap = {}
        
        # 1. Control Keys & Whitespace
        control_map = {
            'backspace': 'BackSpace',
            '\b':        'BackSpace',
            'tab':       'Tab',
            '\t':        'Tab',
            'enter':     'Return',
            'return':    'Return',
            '\n':        'Return',
            '\r':        'Return',
            'escape':    'Escape',
            'esc':       'Escape',
            '\x1b':      'Escape',
            'space':     'space',
            ' ':         'space',
            'up':        'Up',
            'down':      'Down',
            'left':      'Left',
            'right':     'Right',
            'home':      'Home',
            'end':       'End',
            'pageup':    'Page_Up',
            'pagedown':  'Page_Down',
            'insert':    'Insert',
            'delete':    'Delete',
            'print':     'Print',
            'f1':        'F1',
            'f2':        'F2',
            'f3':        'F3',
            'f4':        'F4',
            'f5':        'F5',
            'f6':        'F6',
            'f7':        'F7',
            'f8':        'F8',
            'f9':        'F9',
            'f10':       'F10',
            'f11':       'F11',
            'f12':       'F12',
        }

        # 2. Symbols and Punctuation
        self._symbol_map = {
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

        # 3. Alphanumeric (A-Z, a-z, 0-9)
        # Note: We rely on string matching.
        
        # Helper to safely map
        def safe_map(char_key, keysym_str):
            try:
                keysym = XK.string_to_keysym(keysym_str)
                if keysym == 0:
                     return
                keycode = self._display.keysym_to_keycode(keysym)
                if keycode != 0:
                    self._keymap[char_key] = keycode
            except:
                pass

        # Apply Control Map
        for key, sym in control_map.items():
            safe_map(key, sym)

        # Apply Symbol Map
        for key, sym in self._symbol_map.items():
            safe_map(key, sym)
            
        # Apply Alphanumeric
        import string
        for char in string.ascii_letters + string.digits:
            safe_map(char, char)
        
        self._shift_mask = X.ShiftMask
        self._shift_keycode = self._display.keysym_to_keycode(XK.string_to_keysym("Shift_L"))
        self._keymap_setup = True

    def _needs_shift(self, char: str) -> bool:
        """
        Determines if a character requires the Shift key to be pressed.
        """
        keycode = self._keymap.get(char)
        if not keycode:
            return False

        try:
            # Get keysyms for the keycode
            # Index 0: Unshifted, Index 1: Shifted
            keysym_unshifted = self._display.keycode_to_keysym(keycode, 0)
            keysym_shifted = self._display.keycode_to_keysym(keycode, 1)
            
            # Determine the keysym for the input char
            target_keysym = 0
            
            # 1. Try direct string to keysym (works for a-z, A-Z, 0-9)
            target_keysym = XK.string_to_keysym(char)
            
            # 2. If valid keysym not found directly (often 0 for symbols), lookup in map
            if target_keysym == 0:
                sym_name = self._symbol_map.get(char)
                if sym_name:
                    target_keysym = XK.string_to_keysym(sym_name)
            
            # 3. If we still don't have a valid keysym, this is likely a control key
            # Control keys (space, enter, etc.) don't need shift
            if target_keysym == 0:
                return False

            if target_keysym == keysym_shifted and target_keysym != keysym_unshifted:
                return True
            
            # If it matches unshifted, definitely False
            if target_keysym == keysym_unshifted:
                return False
            
            return False
            
        except Exception:
            return False

    def keydown(self, keycode: int, needs_shift: bool) -> None:
        """
        Presses a key down. If needs_shift is True, presses shift, presses key, then releases shift.
        """
        if needs_shift:
            # Press shift
            xtest.fake_input(self._display, X.KeyPress, self._shift_keycode)
            self._display.sync()
            
        # Press key
        xtest.fake_input(self._display, X.KeyPress, keycode)
        self._display.sync()
        
        if needs_shift:
            # Release shift (handled entirely in keydown)
            xtest.fake_input(self._display, X.KeyRelease, self._shift_keycode)
            self._display.sync()
    
    def keyup(self, keycode: int) -> None:
        """
        Releases a key. Shift is not released here as it's handled in keydown.
        """
        xtest.fake_input(self._display, X.KeyRelease, keycode)
        self._display.sync()

    def keypress(self, char: str) -> None:
        """
        Simulates a complete key press (down and up) for a single character.
        Handles shift key automatically based on character requirements.
        """
        self._setup_keymap()
        
        keycode = self._keymap.get(char)
        keysym = None
        
        # Fallback if not in map
        if not keycode:
             try:
                 keysym = XK.string_to_keysym(char)
                 keycode = self._display.keysym_to_keycode(keysym)
             except:
                 pass
        
        if not keycode:
            # print(f"Could not map char '{char}'")
            return

        needs_shift = self._needs_shift(char)
        
        self.keydown(keycode, needs_shift)
        time.sleep(0.01)
        self.keyup(keycode)
        time.sleep(0.05)

    def send_keys(self, window: Any, keys: str) -> None:
        """
        Sends a sequence of keys.
        Supports logical modifiers:
        % = Alt
        ^ = Control
        + = Shift
        The modifier applies to the NEXT character only.
        
        Supports escaping and special keys in {}:
        {+}  -> types +
        {%}  -> types %
        {^}  -> types ^
        {ENTER} -> types Enter
        {TAB}   -> types Tab
        
        Example: "%fa" -> Alt+f, then a.
        Example: "{+}" -> types +
        """
        self._setup_keymap()

        i = 0
        n = len(keys)
        while i < n:
            char = keys[i]
            modifier = None
            
            # 1. Handle Modifiers
            if char in ['%', '^', '+'] and i + 1 < n and keys[i+1] != '{':
                 # Only treat as modifier if NOT followed by { (heuristic)
                 # Actually, standard is +{KEY} means Shift+Key
                 # So simple check: is it a modifier char?
                 modifier = char
                 i += 1
                 if i >= n: break
                 char = keys[i]
            
            # Determine modifier keycode
            mod_keycode = 0
            if modifier == '%':
                 try: mod_keycode = self._display.keysym_to_keycode(XK.string_to_keysym("Alt_L"))
                 except: pass
            elif modifier == '^':
                 try: mod_keycode = self._display.keysym_to_keycode(XK.string_to_keysym("Control_L"))
                 except: pass
            elif modifier == '+':
                 try: mod_keycode = self._display.keysym_to_keycode(XK.string_to_keysym("Shift_L"))
                 except: pass

            # Press modifier
            if mod_keycode:
                 self.keydown(mod_keycode, False)
            
            # 2. Handle Token {KEY} or regular char
            if char == '{':
                # Find closing }
                end = keys.find('}', i)
                if end != -1:
                    token = keys[i+1:end]
                    # Handle escaped char or special key
                    if len(token) == 1:
                         self.keypress(token)
                    else:
                         # Map specific tokens if needed, e.g. ENTER
                         # self.keypress handles char strings, but maybe not names?
                         # Our keypress logic does heuristic mapping.
                         # Try mapping token.lower() to keymap
                         self.keypress(token) 
                    i = end + 1
                else:
                    # No closing brace, treat as literal {
                    self.keypress('{')
                    i += 1
            else:
                self.keypress(char)
                i += 1
            
            # Release modifier
            if mod_keycode:
                 self.keyup(mod_keycode)

    def click(self, x: int, y: int) -> None:
        try:
            xtest.fake_input(self._display, X.MotionNotify, x=x, y=y)
            self._display.sync()
            time.sleep(0.1)
            xtest.fake_input(self._display, X.ButtonPress, 1)
            self._display.sync()
            time.sleep(0.05)
            xtest.fake_input(self._display, X.ButtonRelease, 1)
            self._display.sync()
            time.sleep(0.1)
        except Exception as e:
            print(f"XTest click failed: {e}")

    def drag_and_drop(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5) -> None:
        """
        Simulate a drag and drop operation using mouse events.
        """
        try:
            # Move to start
            xtest.fake_input(self._display, X.MotionNotify, x=start_x, y=start_y)
            self._display.sync()
            time.sleep(0.2)
            
            # Press button 1
            xtest.fake_input(self._display, X.ButtonPress, 1)
            self._display.sync()
            time.sleep(0.2) # Hold before moving to ensure click registers
            
            # Interpolate movement
            steps = 20
            dt = duration / steps
            for i in range(steps):
                cx = int(start_x + (end_x - start_x) * (i + 1) / steps)
                cy = int(start_y + (end_y - start_y) * (i + 1) / steps)
                xtest.fake_input(self._display, X.MotionNotify, x=cx, y=cy)
                self._display.sync()
                time.sleep(dt)
            
            # Release button 1
            xtest.fake_input(self._display, X.ButtonRelease, 1)
            self._display.sync()
            time.sleep(0.1)
            
        except Exception as e:
            print(f"XTest drag_and_drop failed: {e}")

    def move_mouse(self, x: int, y: int) -> None:
        """
        Moves the mouse pointer to the specified coordinates.
        """
        try:
            xtest.fake_input(self._display, X.MotionNotify, x=x, y=y)
            self._display.flush()
        except Exception as e:
            print(f"XTest move_mouse failed: {e}")

    def get_displays(self) -> List[dict]:
        """
        Returns a list of connected displays using XRandR.
        """
        displays = []
        try:
            root = self._display.screen().root
            res = randr.get_screen_resources(root)
            
            # Helper to get primary output
            primary_output = None
            try:
                primary_output = randr.get_output_primary(root).output
            except:
                pass

            for output_id in res.outputs:
                try:
                    out_info = randr.get_output_info(self._display, output_id, res.config_timestamp)
                    if out_info.crtc == 0 or out_info.connection != 0: # 0=Connected
                        continue
                        
                    crtc_info = randr.get_crtc_info(self._display, out_info.crtc, res.config_timestamp)
                    
                    is_primary = (output_id == primary_output)
                    
                    displays.append({
                        'id': output_id,
                        'name': out_info.name,
                        'x': crtc_info.x,
                        'y': crtc_info.y,
                        'width': crtc_info.width,
                        'height': crtc_info.height,
                        'primary': is_primary
                    })
                except Exception as e:
                    # print(f"Error getting output info: {e}")
                    pass
        except Exception as e:
            print(f"XRandR get_displays failed: {e}")
            # Fallback to single screen
            screen = self._display.screen()
            displays.append({
                'id': 0,
                'name': 'Default',
                'x': 0,
                'y': 0,
                'width': screen.width_in_pixels,
                'height': screen.height_in_pixels,
                'primary': True
            })
            
        return displays

    def get_desktops(self) -> List[dict]:
        """
        Returns a list of desktops using EWMH (_NET_WM properties).
        """
        desktops = []
        try:
            root = self._display.screen().root
            
            # Helper to get property
            def get_prop(atom_name):
                atom = self._display.intern_atom(atom_name)
                prop = root.get_full_property(atom, X.AnyPropertyType)
                if prop:
                    return prop.value
                return None
                
            # 1. Number of Desktops
            num_desktops_val = get_prop('_NET_NUMBER_OF_DESKTOPS')
            num_desktops = num_desktops_val[0] if num_desktops_val else 1
            
            # 2. Current Desktop
            current_desktop_val = get_prop('_NET_CURRENT_DESKTOP')
            current_desktop_idx = current_desktop_val[0] if current_desktop_val else 0
            
            # 3. Desktop Names
            names_val = get_prop('_NET_DESKTOP_NAMES')
            # Xlib returns generic string or bytes, sometimes null-separated
            desktop_names = []
            if names_val:
                # Often null terminated string
                if isinstance(names_val, bytes):
                    names_val = names_val.decode('utf-8', 'ignore')
                desktop_names = names_val.split('\x00')
                # Remove empty strings from split
                desktop_names = [n for n in desktop_names if n]

            for i in range(num_desktops):
                name = str(i + 1)
                if i < len(desktop_names):
                    name = desktop_names[i]
                
                desktops.append({
                    'id': i,
                    'name': name,
                    'is_active': (i == current_desktop_idx)
                })
                
        except Exception as e:
            print(f"EWMH get_desktops failed: {e}")
            # Fallback
            desktops.append({'id': 0, 'name': 'Desktop 1', 'is_active': True})
            
        return desktops
