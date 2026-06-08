
import sys
import os
import time

# Add source to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from ccai.uia.platforms.linux.agents.wm.waylandwindowmanageragent import WaylandWindowManagerAgent

def verify_mouse():
    print("Initializing Wayland Agent...")
    try:
        agent = WaylandWindowManagerAgent()
    except Exception as e:
        print(f"Failed to init agent: {e}")
        return

    print("Agent initialized.")
    
    # Verify Screen Geometry
    w, h = agent.get_screen_geometry()
    print(f"Screen Geometry (GDK): {w}x{h}")
    
    if not agent._uinput_fd:
        print("WARNING: UInput not available. Test may fail or fallback to XTest.")

    targets = [
        (400, 400, True),  # Sync (Reset to 0,0)
        (500, 400, False), # No Sync (Relative from 400,400 -> +100,0)
        (100, 100, True),  # Sync (Reset to 0,0)
        (150, 150, False)  # No Sync
    ]

    for x, y, sync in targets:
        print(f"Moving to ({x}, {y}) [Sync={sync}]...")
        agent.move_mouse(x, y, sync=sync)
        
        # Check tracking
        pos = agent.get_mouse_position()
        print(f"Internal Position Tracker: {pos}")
        if pos != (x, y):
            print(f"ERROR: Tracker mismatch! Expected ({x}, {y}), got {pos}")
        
        print("Clicking...")
        agent.click(x, y)
        
        print(f"Please verify mouse is at approx ({x}, {y})")
        time.sleep(2)

    print("Verification complete.")

if __name__ == "__main__":
    verify_mouse()
