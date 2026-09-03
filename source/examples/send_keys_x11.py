
import sys
import time
import os

try:
    from Xlib import X, display, XK
    from Xlib.ext import xtest
    from Xlib.protocol import event
except ImportError:
    print("Error: python-xlib not installed")
    sys.exit(1)

def find_window(disp, name):
    root = disp.screen().root
    window_list = root.query_tree().children
    for win in window_list:
        try:
            # Check WM_NAME
            wm_name = win.get_wm_name()
            if wm_name and name.lower() in wm_name.lower():
                return win
            
            # Check WM_CLASS
            wm_class = win.get_wm_class()
            if wm_class:
                for cls in wm_class:
                    if name.lower() in cls.lower():
                        return win
        except Exception:
            pass
    return None

def send_keys(window_name, keys):
    disp = display.Display()
    target_win = find_window(disp, window_name)
    
    if not target_win:
        print(f"Window '{window_name}' not found")
        # Try to find via _NET_CLIENT_LIST if the basic query failed (for some WMs)
        # But basic query usually works for top-level. 
        # Fallback: Just assume active window if name is empty
        if not window_name:
             target_win = disp.get_input_focus().focus
        else:
             sys.exit(1)

    # Focus window explicitly via X11
    # 1. Map and Raise
    target_win.configure(stack_mode=X.Above)
    target_win.map()
    disp.sync()
    
    # 2. Set Input Focus
    disp.set_input_focus(target_win, X.RevertToParent, X.CurrentTime)
    disp.sync()
    time.sleep(0.2)
    
    # 3. Click center to be sure (XTest)
    geom = target_win.get_geometry()
    # Need absolute coordinates. Translate from window 0,0 to root
    coords = target_win.translate_coords(disp.screen().root, 0, 0)
    center_x = coords.x + (geom.width // 2)
    center_y = coords.y + (geom.height // 2)
    
    xtest.fake_input(disp, X.MotionNotify, x=center_x, y=center_y)
    disp.sync()
    xtest.fake_input(disp, X.ButtonPress, 1)
    disp.sync()
    time.sleep(0.1)
    xtest.fake_input(disp, X.ButtonRelease, 1)
    disp.sync()
    time.sleep(0.2)
    
    print(f"Typing '{keys}' into '{window_name}' at {center_x},{center_y}")
    
    for char in keys:
        keysym = None
        if char == '*': keysym = XK.string_to_keysym("asterisk")
        elif char == '=': keysym = XK.string_to_keysym("equal")
        elif char == '+': keysym = XK.string_to_keysym("plus")
        elif char == '-': keysym = XK.string_to_keysym("minus")
        elif char == '/': keysym = XK.string_to_keysym("slash") 
        elif char == 'Return': keysym = XK.string_to_keysym("Return")
        else: keysym = XK.string_to_keysym(char)

        if keysym is None:
            continue

        keycode = disp.keysym_to_keycode(keysym)
        if keycode == 0:
            continue
        
        xtest.fake_input(disp, X.KeyPress, keycode)
        xtest.fake_input(disp, X.KeyRelease, keycode)
        disp.sync()
        time.sleep(0.1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 send_keys_x11.py <window_name_substring> <keys>")
        sys.exit(1)
    
    send_keys(sys.argv[1], sys.argv[2])
