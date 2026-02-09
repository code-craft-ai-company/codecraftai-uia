
import sys
import os
import time

# Add source to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from automojo.uia.platforms.linux.agents.wm.waylandwindowmanageragent import WaylandWindowManagerAgent

def debug_get_position():
    print("Initializing Wayland Agent...")
    try:
        agent = WaylandWindowManagerAgent()
    except Exception as e:
        print(f"Failed to init agent: {e}")
        return

    print("Reading mouse position for 10 seconds...")
    print("Please move your mouse around the screen!")
    
    try:
        if not agent._has_xwayland:
            print("WARNING: XWayland not detected. Cannot read mouse position via X11.")
            return

        root = agent._display.screen().root
        
        for i in range(10):
            data = root.query_pointer()._data
            x = data["root_x"]
            y = data["root_y"]
            print(f"[{i+1}/10] Mouse Position: ({x}, {y})")
            time.sleep(1)
            
    except Exception as e:
        print(f"Error reading position: {e}")

    print("Done.")

if __name__ == "__main__":
    debug_get_position()
