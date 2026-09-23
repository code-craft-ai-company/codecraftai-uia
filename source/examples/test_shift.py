from Xlib import display, XK

def needs_shift(disp, char):
    keysym = XK.string_to_keysym(char)
    if keysym == 0:
        print(f"No keysym for {char}")
        return False
    
    keycode = disp.keysym_to_keycode(keysym)
    if keycode == 0:
        print(f"No keycode for {char}")
        return False
        
    # Get keysyms for this keycode
    # index 0 is unshifted, index 1 is shifted
    # keycode_to_keysym(keycode, index)
    try:
        keysym_unshifted = disp.keycode_to_keysym(keycode, 0)
        keysym_shifted = disp.keycode_to_keysym(keycode, 1)
        
        print(f"Char: {char}, Keycode: {keycode}, Unshifted: {keysym_unshifted}, Shifted: {keysym_shifted}, Target: {keysym}")

        if keysym == keysym_shifted and keysym != keysym_unshifted:
            return True
        elif keysym == keysym_shifted and keysym == keysym_unshifted:
           # If it's the same for both, it probably doesn't strictly *need* shift, but
           # this might happen for keys that don't have a shifted variant or are the same.
           # Usually we assume False if it works without shift.
           return False
        
        # Check if it *only* appears in shifted position
        # Make sure it's not in unshifted position
        if keysym == keysym_unshifted:
             return False
             
        # What if it's in neither 0 nor 1? (e.g. AltGr) - ignoring for now
        
        return False
        
    except Exception as e:
        print(f"Error checking {char}: {e}")
        return False

# Test
disp = display.Display()
test_chars = ['a', 'A', '1', '!', ' ', '\n', '@', 'b', 'B', '7', '&']

for c in test_chars:
    needed = needs_shift(disp, c)
    print(f"'{c}' needs shift: {needed}")

