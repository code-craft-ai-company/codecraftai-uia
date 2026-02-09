
import platform
import time
import math
from automojo import testbase
from automojo.uia.factory import AutomationFactory
from automojo.uia.platforms.linux.agents.wm.waylandwindowmanageragent import WaylandWindowManagerAgent

def test_wayland_mouse_circle():
    """
    Verifies Wayland mouse movement by drawing a circle using the 'move_relative' method.
    Checks if the internal position tracker remains consistent.
    """
    if platform.system() != "Linux":
        return

    automation = AutomationFactory.get_automation_engine()
    
    # Check if we are using the Wayland agent
    if not isinstance(automation._wm_agent, WaylandWindowManagerAgent):
        print("Skipping Wayland mouse test: Not running with WaylandWindowManagerAgent")
        return

    agent = automation._wm_agent
    
    # Circle config
    # Using 960, 540 as verified center for 1080p
    center_x, center_y = 960, 540
    radius = 100
    duration = 2.0
    steps = 50  # Reduced steps for test speed
    
    print(f"Moving to center start: ({center_x + radius}, {center_y})")
    start_x = int(center_x + radius)
    start_y = int(center_y)
    
    # 1. Initial move to start point (uses reset-to-origin internally)
    agent.move_mouse(start_x, start_y)
    time.sleep(1.0)
    
    # Verify start position
    start_pos = agent.get_mouse_position()
    testbase.assert_equal(start_pos, (start_x, start_y))
    
    print("Drawing circle...")
    current_x = start_x
    current_y = start_y
    dt = duration / steps
    
    for i in range(1, steps + 1):
        angle = 2 * math.pi * (i / steps)
        target_x = int(center_x + radius * math.cos(angle))
        target_y = int(center_y + radius * math.sin(angle))
        
        dx = target_x - current_x
        dy = target_y - current_y
        
        agent.move_relative(dx, dy)
        
        current_x = target_x
        current_y = target_y
        
        time.sleep(dt)

    # Verify final position
    final_pos = agent.get_mouse_position()
    print(f"Final Position: {final_pos}")
    
    # Allow for small integer rounding errors (should be exact with int math but safe to check range)
    # Actually, with the logic above, it should match the final target_x/y which wraps to start
    testbase.assert_equal(final_pos, (start_x, start_y))
