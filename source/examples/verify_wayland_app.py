
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import threading
import time
import sys
import os

# Add source to path for automojo import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from automojo.uia.factory import AutomationFactory
from automojo.uia.platforms.linux.wrappers.uiawindow import LinuxWindow

def run_test_logic():
    print("Test Logic: Waiting for app to launch...")
    time.sleep(3.0)
    
    automation = AutomationFactory.get_automation_engine()
    agent = automation._wm_agent
    
    print("Test Logic: Searching for application...")
    
    # Try to find the window directly in the desktop list if app name is elusive
    import pyatspi
    reg = pyatspi.Registry
    desktop = reg.getDesktop(0)
    
    target_window = None
    target_app_name = None
    
    for i in range(desktop.childCount):
        try:
            child = desktop.getChildAtIndex(i)
            # Check children for our window title
            if child.childCount > 0:
                for j in range(child.childCount):
                    try:
                        win = child.getChildAtIndex(j)
                        if win.name == "Automojo Wayland Click Verify":
                            target_window = win
                            target_app_name = child.name
                            print(f"Test Logic: Found window '{win.name}' in app '{child.name}'")
                            break
                    except: pass
            if target_window: break
        except: pass

    if not target_window:
        print("Test Logic: ERROR - Could not find window. Dumping top-level apps:")
        for i in range(desktop.childCount):
            try:
                print(f"  - {desktop.getChildAtIndex(i).name}")
            except: pass
        # Exit app
        GLib.idle_add(Gtk.main_quit)
        return

    # Wrap found window
    # We found the native atspi window object.
    # We need to constructing the wrapper carefully.
    # LinuxWindow expects a native object that has role frame/window.
    
    # Also need accessibility agent
    acc_agent = automation._access_agent
    
    window = LinuxWindow(target_window, acc_agent, agent)
    print(f"Test Logic: Window wrapper created. Bounds: {window.bounds}")
    
    print("Test Logic: Finding button...")
    # Find button
    button = window.find_element(role='push button')
    if not button:
        print("Test Logic: Button not found via find_element. Trying explicit child dump...")
        children = acc_agent.get_children(target_window)
        for c in children:
            print(f"  Child: {c.name} Role: {c.getRoleName()}")
        GLib.idle_add(Gtk.main_quit)
        return
        
    print(f"Test Logic: Button found: '{button.name}' at {button.bounds}")
    
    # Calculate screen relative coordinates
    bx, by, bw, bh = button.bounds
    center_x = bx + bw // 2
    center_y = by + bh // 2
    
    print(f"Test Logic: Calculated Center: ({center_x}, {center_y})")
    
    print("Test Logic: Moving mouse to center (Sync=True)...")
    agent.move_mouse(center_x, center_y, sync=True)
    time.sleep(0.5)
    
    print("Test Logic: Clicking...")
    agent.click(center_x, center_y)
    
    print("Test Logic: Click sent.")
    time.sleep(2.0)
    print("Test Logic: Closing app.")
    GLib.idle_add(Gtk.main_quit)

def on_button_clicked(widget):
    print("BUTTON CLICKED!")

def main():
    win = Gtk.Window(title="Automojo Wayland Click Verify")
    win.set_default_size(200, 200)
    
    display = Gdk.Display.get_default()
    print(f"GTK Backend: {display.__class__.__name__}")
    
    fixed = Gtk.Fixed()
    win.add(fixed)
    
    button = Gtk.Button(label="Click Me")
    button.connect("clicked", on_button_clicked)
    button.set_size_request(40, 80)
    
    # Position: 
    # Window 200x200. Center 100,100.
    # Button 40x80. Top-Left at 80, 60.
    fixed.put(button, 80, 60)
    
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    win.move(200, 200)
    
    # Start test thread
    t = threading.Thread(target=run_test_logic, daemon=True)
    t.start()
    
    Gtk.main()

if __name__ == "__main__":
    main()
