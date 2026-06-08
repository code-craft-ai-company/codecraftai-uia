
import sys
import os
import time
import math

# Add source to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from ccai.uia.platforms.linux.agents.wm.waylandwindowmanageragent import WaylandWindowManagerAgent

def draw_circle():
    print("Initializing Wayland Agent...")
    try:
        agent = WaylandWindowManagerAgent()
    except Exception as e:
        print(f"Failed to init agent: {e}")
        return

    # Circle config
    # Testing at 400, 400 as requested
    center_x, center_y = 400, 400
    radius = 100
    duration = 2.0
    steps = 100  # Number of segments
    
    print(f"Moving to center start: ({center_x + radius}, {center_y})")
    # Start at 0 degrees (right side of circle)
    start_x = int(center_x + radius)
    start_y = int(center_y)
    
    agent.move_mouse(start_x, start_y)
    time.sleep(1)
    
    print("Drawing circle...")
    
    current_x = start_x
    current_y = start_y
    
    dt = duration / steps
    
    for i in range(1, steps + 1):
        angle = 2 * math.pi * (i / steps)
        # Calculate target absolute point
        target_x = int(center_x + radius * math.cos(angle))
        target_y = int(center_y + radius * math.sin(angle))
        
        # Calculate delta
        dx = target_x - current_x
        dy = target_y - current_y
        
        # Move relative
        agent.move_relative(dx, dy)
        
        # Update current
        current_x = target_x
        current_y = target_y
        
        time.sleep(dt)

    print("Circle complete. Checking position...")
    pos = agent.get_mouse_position()
    print(f"Final Position: {pos}") 
    # Should be back at start_x, start_y approx
    
    print("Done.")

if __name__ == "__main__":
    draw_circle()
