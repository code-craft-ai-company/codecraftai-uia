from Xlib import display, XK

class MockAgent:
    def __init__(self):
        self._display = display.Display()
        self._keymap = {}
        self._setup_keymap()

    def _setup_keymap(self):
        # ... (simplified version of _setup_keymap from x11_agent.py)
        symbol_map = {
            '!': 'exclam', '"': 'quotedbl', '#': 'numbersign', '$': 'dollar',
            '%': 'percent', '&': 'ampersand', '\'': 'apostrophe', '(': 'parenleft',
            ')': 'parenright', '*': 'asterisk', '+': 'plus', ',': 'comma',
            '-': 'minus', '.': 'period', '/': 'slash', ':': 'colon',
            ';': 'semicolon', '<': 'less', '=': 'equal', '>': 'greater',
            '?': 'question', '@': 'at', '[': 'bracketleft', '\\': 'backslash',
            ']': 'bracketright', '^': 'asciicircum', '_': 'underscore',
            '`': 'grave', '{': 'braceleft', '|': 'bar', '}': 'braceright',
            '~': 'asciitilde'
        }
        
        def safe_map(char_key, keysym_str):
            try:
                keysym = XK.string_to_keysym(keysym_str)
                if keysym == 0: return
                keycode = self._display.keysym_to_keycode(keysym)
                if keycode != 0:
                    self._keymap[char_key] = keycode
            except Exception:
                # Characters with no keysym or keycode on the current keyboard layout are left unmapped.
                pass

        for key, sym in symbol_map.items():
            safe_map(key, sym)
            
        import string
        for char in string.ascii_letters + string.digits:
            safe_map(char, char)

    def _needs_shift(self, char):
        keycode = self._keymap.get(char)
        if not keycode:
            print(f"Skipping {char}: No keycode")
            return False
            
        # Get keysyms for the keycode
        # Index 0: Unshifted
        # Index 1: Shifted
        val_unshifted = self._display.keycode_to_keysym(keycode, 0)
        val_shifted = self._display.keycode_to_keysym(keycode, 1)
        
        str_unshifted = XK.keysym_to_string(val_unshifted) if val_unshifted else None
        str_shifted = XK.keysym_to_string(val_shifted) if val_shifted else None
        
        # We need to match the char against these keysym strings
        # The keysym string for '!' is 'exclam', which doesn't match '!'.
        # But for letters 'A' -> 'A', 'a' -> 'a'.
        
        print(f"Char: {char} -> Keycode: {keycode}")
        print(f"  Unshifted: {val_unshifted} ({str_unshifted})")
        print(f"  Shifted:   {val_shifted} ({str_shifted})")
        
        # Direct Match Approach?
        # If I strictly use the keysym that brought us here...
        
        # Reverse lookup?
        # We know `char` maps to `keycode`.
        # We want to know if `keycode` + Shift produces `char`.
        
        # Let's check which keysym in the keycode corresponds to our char.
        # But we don't know the keysym for `char` easily without the map.
        
        # Re-derive keysym for char using the map logic
        
        # In a real scenario, we might iterate over the map or store it inverted.
        # But wait, `_setup_keymap` computes `self._keymap` which assumes a specific keysym was used.
        # Let's inspect what `_keymap` actually stores. It stores `keycode`.
        
        # If I have '!', I found keycode 10 (for '1').
        # keycode 10 unshifted is '1', shifted is '!'.
        
        # If I have '1', I found keycode 10.
        # keycode 10 unshifted is '1', shifted is '!'.
        
        # So I need to know: Is '!' the unshifted or shifted symbol for keycode 10?
        # I can try to map '!' to a keysym using the same logic as setup_keymap.
        
        # Just use the symbol map again to resolve char -> keysym_name -> keysym_val
        symbol_map = {
            '!': 'exclam', '"': 'quotedbl', '#': 'numbersign', '$': 'dollar',
            '%': 'percent', '&': 'ampersand', '\'': 'apostrophe', '(': 'parenleft',
            ')': 'parenright', '*': 'asterisk', '+': 'plus', ',': 'comma',
            '-': 'minus', '.': 'period', '/': 'slash', ':': 'colon',
            ';': 'semicolon', '<': 'less', '=': 'equal', '>': 'greater',
            '?': 'question', '@': 'at', '[': 'bracketleft', '\\': 'backslash',
            ']': 'bracketright', '^': 'asciicircum', '_': 'underscore',
            '`': 'grave', '{': 'braceleft', '|': 'bar', '}': 'braceright',
            '~': 'asciitilde'
        }
        
        keysym_name = symbol_map.get(char, char)
        target_keysym = XK.string_to_keysym(keysym_name)
        
        if target_keysym == val_shifted:
            return True
        elif target_keysym == val_unshifted:
            return False
            
        # Fallback: Maybe it matches the string representation?
        if str_shifted == char: return True
        if str_unshifted == char: return False
        
        return False

agent = MockAgent()
test_chars = ['a', 'A', '1', '!', '@', 'b', 'B', '7', '&']
for c in test_chars:
    print(f"'{c}' needs shift: {agent._needs_shift(c)}")
