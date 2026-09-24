
from typing import Optional
from ccai.uia.platforms.base import AutomationEngine
from ccai.uia.platforms.linux.wrappers.uiaapplication import LinuxApplication
from ccai.uia.platforms.linux.agents.linuxbaseagents import AccessibilityAgent, WindowManagerAgent
from ccai.uia.platforms.linux.agents.common.pyatspi_agent import PyAtspiAccessibilityAgent
from ccai.uia.platforms.linux.agents.x11.x11windowmanageragent import X11WindowManagerAgent
from ccai.uia.platforms.linux.platformdetect import PlatformDetector

class LinuxAutomation(AutomationEngine):
    """
    Automation engine for Linux using Agent Architecture.
    Automatically detects and supports both X11 and Wayland sessions.
    """
    def __init__(self):
        self._access_agent: AccessibilityAgent = None
        self._wm_agent: WindowManagerAgent = None
        self._shut_down = False
        self._initialize_agents()

    def shutdown(self) -> None:
        """
            Closes the window manager and accessibility agents, releasing what they hold (for example the Wayland
            agent's ``/dev/uinput`` virtual mouse).  The engine must not be used afterwards.  Calling
            :meth:`shutdown` more than once is safe.

            :raises: OSError when an agent's resources cannot be released; the other agent is still closed.
        """
        if self._shut_down:
            return
        self._shut_down = True

        wm_agent = self._wm_agent
        access_agent = self._access_agent
        try:
            if wm_agent is not None:
                wm_agent.close()
        finally:
            if access_agent is not None:
                access_agent.close()
        return

    def _initialize_agents(self):
        """
        Initialize accessibility and window manager agents based on platform.
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
        compositor = platform_info['compositor']
        
        print(f"Platform Detection: Type={session_type}, Compositor={compositor}")
        
        if session_type == 'wayland':
            if compositor == 'mutter' or compositor == 'gnome':
                try:
                    from ccai.uia.platforms.linux.agents.wayland.gnome.waylandgnomewindowmanageragent import WaylandGnomeWindowManagerAgent
                    self._wm_agent = WaylandGnomeWindowManagerAgent()
                    print(f"✓ Wayland Gnome Agent initialized")
                except Exception as e:
                    print(f"Warning: Wayland Gnome Agent initialization failed: {e}")
            else:
                 try:
                    from ccai.uia.platforms.linux.agents.wayland.other.waylandotherwindowmanageragent import WaylandOtherWindowManagerAgent
                    self._wm_agent = WaylandOtherWindowManagerAgent()
                    print(f"✓ Wayland Other Agent initialized ({compositor})")
                 except Exception as e:
                    print(f"Warning: Wayland Other Agent initialization failed: {e}")

        elif session_type == 'x11':
            # Use X11 agent for pure X11 sessions
            try:
                self._wm_agent = X11WindowManagerAgent()
                print(f"✓ X11 Agent initialized")
            except Exception as e:
                print(f"Warning: X11 Agent initialization failed: {e}")
        else:
            print(f"Warning: Unknown session type '{session_type}', no WM agent initialized")

    def get_application_by_name(self, application_name: str) -> Optional[LinuxApplication]:
        """
            Gets an application by its name from the Accessibility Agent.
        """
        app_node = self._access_agent.get_application_by_name(application_name)
        if app_node:
             return LinuxApplication(app_node, self._access_agent, self._wm_agent)
        return None

    def find_window(self, name_pattern: str) -> Optional['LinuxWindow']:
        """
        Finds a window by name pattern.
        Returns a LinuxWindow wrapper containing both the Accessibility object
        and the Native Window object (if available).
        """
        from ccai.uia.platforms.linux.wrappers.uiawindow import LinuxWindow
        
        # 1. Find Accessibility Object (AT-SPI)
        # We search across all desktop children
        # This implementation requires PyAtspiAccessibilityAgent to have a suitable method
        # or we iterate manually here.
        
        found_node = None
        # Use existing agent methods if possible, or iterate
        # PyAtspiAgent doesn't have global find_window exposed, let's implement a search here using it
        
        # Iterate apps
        try:
            desktop = self._access_agent.get_root()
            for i in range(desktop.childCount):
                app = desktop.getChildAtIndex(i)
                # Iterate windows in app
                for j in range(app.childCount):
                    win = app.getChildAtIndex(j)
                    if win.getRoleName() == 'frame' and name_pattern in win.name:
                        found_node = win
                        break
                if found_node: break
        except Exception as e:
            print(f"Error searching AT-SPI: {e}")
            
        if not found_node:
            print(f"Window '{name_pattern}' not found in Accessibility Tree.")
            return None
            
        # 2. Find Native Window Object
        native_window = None
        if self._wm_agent is not None and hasattr(self._wm_agent, 'find_native_window'):
            native_window = self._wm_agent.find_native_window(name_pattern)

        # 3. Create Wrapper
        return LinuxWindow(found_node, self._access_agent, self._wm_agent, native_window=native_window)

    def get_displays(self) -> list:
        """
        Returns a list of connected displays.
        """
        if self._wm_agent:
            return self._wm_agent.get_displays()
        return []

    def get_desktops(self) -> list:
        """
        Returns a list of desktops/workspaces.
        """
        if self._wm_agent:
            return self._wm_agent.get_desktops()
        return []

