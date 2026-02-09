
import tkinter as tk
import threading
import time
import sys
import os

# Add source to path for automojo import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from automojo.uia.factory import AutomationFactory
from automojo.uia.platforms.linux.agents.wm.waylandwindowmanageragent import WaylandWindowManagerAgent

def run_tkinter_app():
    root = tk.Tk()
    root.title("Automojo Click Verify")
    # Position at 200, 200 with size 200x200
    root.geometry("200x200+200+200")
    
    # 40x80 button centered
    # Center of 200x200 is 100,100.
    # Button 40 wide, 80 high
    # Top-left of button: x=100-20=80, y=100-40=60
    btn = tk.Button(root, text="Click Me", command=lambda: print("BUTTON CLICKED!"))
    btn.place(x=80, y=60, width=40, height=80)
    
    root.mainloop()

def test_click():
    # Start app in thread
    t = threading.Thread(target=run_tkinter_app, daemon=True)
    t.start()
    
    print("Waiting for app to launch...")
    time.sleep(2.0)
    
    automation = AutomationFactory.get_automation_engine()
    agent = automation._wm_agent
    
    print("Finding application...")
    # Tkinter generic name is usually 'tk' or the title
    app = automation.get_application_by_name("Automojo Click Verify")
    if not app:
        # Fallback to searching all (Tkinter sometimes tricky with names)
        # Try generic python/tk name?
        app = automation.get_application_by_name("tk")
        
    if not app:
        print("ERROR: Could not find Tkinter application.")
        return

    print("Finding window...")
    # In some AT-SPI implementations, the app object is the window or has the window as child
    # Let's dump children to debug if needed
    window = app.find_element(role='frame')
    if not window:
        # Maybe the app object itself is the frame?
        if app.role_name == 'frame':
            window = app
    
    if not window:
        print("ERROR: Could not find window.")
        return
        
    print(f"Window found: {window.name} at {window.bounds}")
    
    print("Finding button...")
    button = window.find_element(role='push button')
    if not button:
        button = window.find_element(role='button')
        
    if not button:
        print("ERROR: Could not find button.")
        return
        
    print(f"Button found: '{button.name}' at {button.bounds}")
    
    # Calculate screen relative coordinates
    # bounds is (x, y, w, h)
    bx, by, bw, bh = button.bounds
    
    center_x = bx + bw // 2
    center_y = by + bh // 2
    
    print(f"Calculated Center: ({center_x}, {center_y})")
    
    print("Moving mouse to center (Sync=True)...")
    agent.move_mouse(center_x, center_y, sync=True)
    time.sleep(0.5)
    
    print("Clicking...")
    # Use agent click directly to verify the coordinate click
    agent.click(center_x, center_y)
    
    print("Click sent. Check console for 'BUTTON CLICKED!'")
    time.sleep(2.0)

if __name__ == "__main__":
    test_click()
