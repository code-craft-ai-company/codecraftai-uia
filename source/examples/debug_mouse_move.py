
import time
import sys
import os

# Add source to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from ccai.uia.platforms.linux.agents.wm.waylandwindowmanageragent import WaylandWindowManagerAgent

def debug_mouse_move():
    print("Initializing X11 Window Manager Agent...")
    try:
        agent = WaylandWindowManagerAgent()
    except Exception as e:
        print(f"Failed to initialize agent: {e}")
        return

    print("Getting screen dimensions...")
    try:
        display = agent._display
        screen = display.screen()
        width = screen.width_in_pixels
        height = screen.height_in_pixels
        print(f"Screen Resolution: {width}x{height}")
        
        # User requested specific coordinates
        cx = 200
        cy = 200
    except Exception as e:
        print(f"Could not get screen details: {e}")
        return

    print(f"Targeting center of screen: ({cx}, {cy})")
    print("You have 3 seconds to look at the screen...")
    time.sleep(3)
    
    print("Moving mouse now...")
    try:
        agent.move_mouse(cx, cy)
        print(f"Command sent: move_mouse({cx}, {cy})")
        
        # Wiggle it a bit to be sure
        time.sleep(1)
        print("Wiggling...")
        agent.move_mouse(cx + 50, cy)
        time.sleep(1)
        agent.move_mouse(cx - 50, cy)
        time.sleep(1)
        agent.move_mouse(cx, cy)
        
    except Exception as e:
        print(f"Movement failed: {e}")

    print("Done.")

if __name__ == "__main__":
    debug_mouse_move()
