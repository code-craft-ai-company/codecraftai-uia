
import sys
import os
import time
import subprocess
import signal

# Add source to path for ccai import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Imports for the App side
try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, Gdk, GLib
except ImportError:
    pass

def run_app():
    """Runs the target GTK Application."""
    print("APP_PROCESS: Starting GTK App...")
    
    win = Gtk.Window(title="CodeCraftAI Target App")
    win.set_default_size(200, 200)
    
    # Check backend
    display = Gdk.Display.get_default()
    print(f"APP_PROCESS: Backend: {display.__class__.__name__}")
    
    fixed = Gtk.Fixed()
    win.add(fixed)
    
    def on_clicked(widget):
        print("APP_PROCESS: BUTTON_CLICKED_EVENT")
        sys.stdout.flush()
        
    btn = Gtk.Button(label="Target")
    btn.connect("clicked", on_clicked)
    btn.set_size_request(40, 80)
    
    # Position: 
    # Center 100,100. Button 40x80. Top-Left: 80, 60.
    fixed.put(btn, 80, 60)
    
    win.connect("destroy", Gtk.main_quit)
    win.set_position(Gtk.WindowPosition.CENTER)
    win.show_all()
    
    # Process events to ensure window is mapped
    while Gtk.events_pending():
        Gtk.main_iteration()
        
    # Get position
    # In Wayland, get_position might return 0,0 or be meaningless, but let's try
    pos = win.get_position()
    print(f"APP_PROCESS: Window Position (GDK): {pos}")
    
    # Also try getting the GdkWindow
    gdk_win = win.get_window()
    if gdk_win:
        # get_root_origin is more reliable for screen coords
        # In GTK+3 GdkWaylandWindow, this might still be 0,0 or relative, but worth checking
        try:
            origin = gdk_win.get_root_origin()
            print(f"APP_PROCESS: Window Root Origin (GDK): {origin}")
        except Exception:
             pass
        
    print("APP_PROCESS: App Ready.")
    sys.stdout.flush()
    Gtk.main()

def run_test():
    """Runs the automation test against the subprocess app."""
    print("TEST_PROCESS: Launching subprocess...")
    # Use -u for unbuffered output
    proc = subprocess.Popen([sys.executable, "-u", __file__, "--app"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    try:
        # Wait for app to be ready
        print("TEST_PROCESS: Waiting for app initialization...")
        # Simple read loop to look for "App Ready"
        start_time = time.time()
        app_ready = False
        import select
        
        while time.time() - start_time < 10:
            reads = [proc.stdout.fileno()]
            ret = select.select(reads, [], [], 0.5)
            if ret[0]:
                line = proc.stdout.readline()
                if line:
                    print(f"  [APP] {line.strip()}")
                    if "App Ready" in line:
                        app_ready = True
                        break
        
        if not app_ready:
            print("TEST_PROCESS: App failed to start within timeout.")
            return

        time.sleep(2.0) # Grace period for AT-SPI registration
        
        print("TEST_PROCESS: Initializing Automation...")
        from ccai.uia.factory import AutomationFactory
        from ccai.uia.platforms.linux.wrappers.uiawindow import LinuxWindow
        
        automation = AutomationFactory.get_automation_engine()
        agent = automation._wm_agent
        
        # Find Window using new Automation method
        print("TEST_PROCESS: Finding 'CodeCraftAI Target App' using automation.find_window()...")
        window = automation.find_window("CodeCraftAI Target App")
        
        if not window:
            print("TEST_PROCESS: ERROR - Window not found via automation.find_window.")
            return

        print(f"TEST_PROCESS: Wrapper created for '{window.name}' Bounds: {window.bounds}")
        print(f"TEST_PROCESS: Window Position (AT-SPI): ({window.bounds[0]}, {window.bounds[1]})")
        
        # Check Native Window
        if window.native_window:
             print(f"TEST_PROCESS: Native Window Object Found: {window.native_window}")
             try:
                 # WnckWindow get_geometry returns (xp, yp, widthp, heightp)
                 # Note: It might be get_geometry() or get_client_window_geometry()
                 geo = window.native_window.get_geometry()
                 print(f"TEST_PROCESS: Native Window Geometry (Wnck): {geo}")
             except Exception as e:
                 print(f"TEST_PROCESS: Failed to get native geometry: {e}")
        else:
             print("TEST_PROCESS: Native Window Object NOT found (Expected in pure Wayland if Wnck fails).")
             
        # New Wayland Code Usage: Validating Screen Geometry
        # Note: win_pos is not directly available from the new window object,
        # but window.bounds provides similar information.
        # If a GDK-specific position is needed, it would require a different approach.
        
        # New Wayland Code Usage: Validating Screen Geometry
        screen_w, screen_h = agent.get_screen_geometry()
        print(f"TEST_PROCESS: Agent Screen Geometry (GDK): {screen_w}x{screen_h}")
        
        # Find Button
        # Search by name to avoid 'Minimize'/'Close' buttons in title bar
        btn = window.find_element(role='push button', name="Target")
        if not btn:
             # Try fallback without role if specific role mismatch
             btn = window.find_element(name="Target")
             
        if not btn:
            print("TEST_PROCESS: ERROR - Button not found.")
            return
            
        print(f"TEST_PROCESS: Button found '{btn.name}' at {btn.bounds}")
        
        # User calibration 4: At (215, 210):
        bx, by, bw, bh = btn.bounds
        # Mouse was 5px Too Low -> Center Y = 210 - 5 = 205.
        # X was good (70).
        # Offset X: 70.
        # Offset Y: 45.
        calibration_x = 70
        calibration_y = 45
        
        cx = bx + bw // 2 + calibration_x
        cy = by + bh // 2 + calibration_y
        
        print(f"TEST_PROCESS: Calculated Center (Final Calibrated): ({cx}, {cy})")
        
        # Execution
        print("TEST_PROCESS: Moving mouse (Sync=True)...")
        agent.move_mouse(cx, cy, sync=True)
        time.sleep(0.5)
        
        # Prompt user before clicking
        print(f"\n[USER CHECK REQURIED] The mouse should be EXACTLY at the center of the 'Target' button.")
        print(f"Coordinates: ({cx}, {cy})")
        input("Press Enter to click the button...")
        
        print("TEST_PROCESS: Clicking (Robust)...")
        # Use explicit down/up with delay to ensure registration
        # agent.click(cx, cy) might be too fast or sync might jitter
        
        # Ensure we are there (redundant but safe)
        agent.move_mouse(cx, cy, sync=False) 
        
        # Press
        agent._emit(0x01, 0x110, 1) # BTN_LEFT down
        agent._emit_syn()
        time.sleep(0.1)
        # Release
        agent._emit(0x01, 0x110, 0) # BTN_LEFT up
        agent._emit_syn()
        
        # Verification
        # Read stdout from app to see if it clicked
        print("TEST_PROCESS: Verifying click via app output...")
        time.sleep(1.0)
        
        # Non-blocking read attempt or just check what we have
        # A bit tricky with readline blocking, but we expect data.
        # We can loop briefly
        click_confirmed = False
        start_verify = time.time()
        while time.time() - start_verify < 2:
            # We use polling on stdout
            import select
            reads = [proc.stdout.fileno()]
            ret = select.select(reads, [], [], 0.1)
            if ret[0]:
                line = proc.stdout.readline()
                print(f"  [APP] {line.strip()}")
                if "BUTTON_CLICKED_EVENT" in line:
                    click_confirmed = True
                    break
        
        if click_confirmed:
            print("\nTEST_PROCESS: SUCCESS! Button click confirmed by app.")
        else:
            print("\nTEST_PROCESS: FAILURE! verification event not received.")

    except Exception as e:
        print(f"TEST_PROCESS: Exception: {e}")
    finally:
        print("TEST_PROCESS: Cleaning up...")
        if proc:
            proc.terminate()
            proc.wait()

if __name__ == "__main__":
    if "--app" in sys.argv:
        run_app()
    else:
        run_test()
