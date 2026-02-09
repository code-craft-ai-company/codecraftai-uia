import sys
import time
import gi
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk

def get_mouse_position():
    display = Gdk.Display.get_default()
    if not display:
        print("Cannot open display")
        return

    seat = display.get_default_seat()
    pointer = seat.get_pointer()
    
    print("Reading mouse position for 5 seconds...")
    for i in range(5):
        screen, x, y = pointer.get_position()
        print(f"[{i+1}/5] Gdk Mouse Position: ({x}, {y})")
        time.sleep(1)

if __name__ == "__main__":
    get_mouse_position()
