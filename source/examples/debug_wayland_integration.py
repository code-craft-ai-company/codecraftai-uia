
import sys
import os
import time

# Add source to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from automojo.uia.platforms.linux.agents.wm.waylandwindowmanageragent import WaylandWindowManagerAgent

def debug_integration():
    print("Initializing Wayland Agent...")
    try:
        agent = WaylandWindowManagerAgent()
    except Exception as e:
        print(f"Failed to init agent: {e}")
        return

    print("Agent initialized.")
    if agent._uinput_fd:
        print(f"UInput FD: {agent._uinput_fd}")
    else:
        print("WARNING: UInput FD is None! Fallback to XTest/Broken state?")

    print("Moving mouse to (300, 300) in 3 seconds...")
    print("Look at the screen!")
    time.sleep(3)
    
    try:
        agent.move_mouse(300, 300)
        print("Move command sent.")
        
        time.sleep(1)
        print("Clicking at (400, 400)...")
        agent.click(400, 400)
        print("Click command sent.")
        
    except Exception as e:
        print(f"Operation failed: {e}")

    print("Done.")

if __name__ == "__main__":
    debug_integration()
