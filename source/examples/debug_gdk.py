
import gi
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk

def probe_gdk():
    display = Gdk.Display.get_default()
    if not display:
        print("Error: No Gdk Display found.")
        return

    print(f"Display Name: {display.get_name()}")
    
    # Check session type
    is_wayland = display.get_name().lower().startswith("wayland")
    print(f"Is Wayland: {is_wayland}")
    
    # Screen Size
    screen = display.get_default_screen()
    print(f"Screen Size: {screen.get_width()}x{screen.get_height()}")
    
    # Monitors
    n_monitors = display.get_n_monitors()
    print(f"Monitors: {n_monitors}")
    for i in range(n_monitors):
        monitor = display.get_monitor(i)
        geo = monitor.get_geometry()
        print(f"  Monitor {i}: {geo.x},{geo.y} {geo.width}x{geo.height} Scale: {monitor.get_scale_factor()}")
        
    # Mouse Position
    seat = display.get_default_seat()
    pointer = seat.get_pointer()
    
    # get_position returns (screen, x, y)
    screen, x, y = pointer.get_position()
    print(f"Mouse Position (get_position): {x}, {y}")
    
    # This usually only works for windows owned by the app, but worth checking returns
    win, x, y, mask = screen.get_root_window().get_pointer()
    print(f"Root Window Pointer: {x}, {y}")

if __name__ == "__main__":
    probe_gdk()
