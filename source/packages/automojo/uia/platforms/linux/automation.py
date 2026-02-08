
from typing import Optional
from automojo.uia.platforms.base import AutomationEngine, UIApplication
from automojo.uia.platforms.linux.wrappers.uiaapplication import LinuxApplication
from automojo.uia.platforms.linux.agents.linuxbaseagents import AccessibilityAgent, WindowManagerAgent
from automojo.uia.platforms.linux.agents.accessibility.pyatspi_agent import PyAtspiAccessibilityAgent
from automojo.uia.platforms.linux.agents.wm.x11windowmanageragent import X11WindowManagerAgent
from automojo.uia.platforms.linux.agents.wm.waylandwindowmanageragent import WaylandWindowManagerAgent
from automojo.uia.platforms.linux.platformdetect import PlatformDetector

class LinuxAutomation(AutomationEngine):
    """
    Automation engine for Linux using Agent Architecture.
    Automatically detects and supports both X11 and Wayland sessions.
    """
    def __init__(self):
        self._access_agent: AccessibilityAgent = None
        self._wm_agent: WindowManagerAgent = None
        self._initialize_agents()

    def _initialize_agents(self):
        """
        Initialize accessibility and window manager agents based on platform.
        
        On Wayland session: Uses WaylandWindowManagerAgent (supports both Wayland and XWayland apps)
        On X11 session: Uses X11WindowManagerAgent
        """
        # Always initialize accessibility agent (works on all platforms)
        try:
             self._access_agent = PyAtspiAccessibilityAgent()
        except ImportError:
             print("Warning: PyAtspi not available.")
        
        if not self._access_agent:
             raise ImportError("Accessibility Agent could not be initialized.")
        
        # Detect platform and initialize appropriate window manager agent
        platform_info = PlatformDetector.get_summary()
        session_type = platform_info['session_type']
        
        print(f"Platform Detection: {session_type}")
        
        if session_type == 'wayland':
            # Use Wayland agent (inherits X11, handles both Wayland and XWayland apps)
            try:
                self._wm_agent = WaylandWindowManagerAgent()
                if hasattr(self._wm_agent, '_has_xwayland') and self._wm_agent._has_xwayland:
                    print(f"✓ Wayland Agent initialized with XWayland support")
                else:
                    print(f"✓ Wayland Agent initialized (AT-SPI only mode)")
            except Exception as e:
                print(f"Warning: Wayland Agent initialization failed: {e}")
                
        elif session_type == 'x11':
            # Use X11 agent for pure X11 sessions
            try:
                self._wm_agent = X11WindowManagerAgent()
                print(f"✓ X11 Agent initialized")
            except Exception as e:
                print(f"Warning: X11 Agent initialization failed: {e}")
        else:
            print(f"Warning: Unknown session type '{session_type}', no WM agent initialized")

    def get_application_by_name(self, application_name: str) -> UIApplication:
        """
            Gets an application by its name from the Accessibility Agent.
        """
        app_node = self._access_agent.get_application_by_name(application_name)
        if app_node:
             return LinuxApplication(app_node, self._access_agent, self._wm_agent)
        return None

