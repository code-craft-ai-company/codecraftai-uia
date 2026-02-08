"""
Wayland Window Manager Agent

Provides window management and input capabilities for Wayland sessions.
Inherits from X11WindowManagerAgent to support XWayland applications.
"""

from typing import Any, List
import os
from automojo.uia.platforms.linux.agents.wm.x11windowmanageragent import X11WindowManagerAgent


class WaylandWindowManagerAgent(X11WindowManagerAgent):
    """
    Window Manager Agent for Wayland sessions with XWayland support.
    
    Inherits from X11WindowManagerAgent to handle XWayland applications,
    while adding Wayland-specific capability detection.
    
    Architecture:
    - For XWayland apps: Uses inherited X11 methods (send_keys, click, etc.)
    - For native Wayland apps: Relies on AT-SPI (accessibility) for all operations
    
    Note: Wayland's security model prevents:
    - Enumerating windows (use AT-SPI to find apps/windows)
    - Arbitrary window focusing (use AT-SPI grabFocus instead)
    - Direct keyboard/mouse injection to Wayland apps (use AT-SPI actions)
    """
    
    def __init__(self):
        """
        Initialize Wayland agent with XWayland support.
        
        Attempts to connect to XWayland display (:0) for XWayland app support.
        If XWayland is not available, X11 operations will fail but AT-SPI
        operations will still work for native Wayland apps.
        """
        self._wayland_display = os.environ.get('WAYLAND_DISPLAY')
        if not self._wayland_display:
            raise RuntimeError(
                "Not running in Wayland session. "
                "WAYLAND_DISPLAY environment variable not set."
            )
        
        # Initialize X11 support for XWayland apps
        try:
            super().__init__()
            self._has_xwayland = True
        except Exception:
            # XWayland not available - AT-SPI only mode
            self._has_xwayland = False
            # Don't raise - we can still work with pure Wayland apps via AT-SPI
    
    def get_default_display(self) -> Any:
        """
        Get the Wayland display.
        
        Returns the WAYLAND_DISPLAY environment variable value.
        For X11 display (XWayland), use the inherited _display property.
        """
        return self._wayland_display
    
    def focus_window(self, window_name: str) -> bool:
        """
        Attempt to focus a window by name.
        
        For XWayland apps: Uses inherited X11 window finding
        For native Wayland apps: Returns False (use AT-SPI grabFocus instead)
        
        Returns:
            True if window was found via X11 and focused
            False if window not found in X11 (likely Wayland app)
        """
        if self.detect_window_type(window_name) == 'x11':
            # Try X11 window focus (works for XWayland apps)
            return super().focus_window(window_name)
            
        return False
    
    def send_keys(self, window: Any, keys: str) -> None:
        """
        Send keyboard input.
        
        Uses inherited X11 XTest for global keyboard simulation.
        Works for both XWayland and native Wayland apps since X11
        keyboard events are translated by the Wayland compositor.
        
        Args:
            window: Ignored (X11 XTest simulates globally)
            keys: String of keys to type
        """
        if not self._has_xwayland:
            raise NotImplementedError(
                "XWayland not available. Keyboard input requires XWayland. "
                "Use AT-SPI EditableText interface for native Wayland apps."
            )
        
        # Delegate to X11 agent's send_keys
        super().send_keys(window, keys)
    

    def detect_window_type(self, window_name: str) -> str:
        """
        Detect if a window is X11/XWayland or native Wayland.
        
        Args:
            window_name: Title of the window
            
        Returns:
            'x11' if found in X11 window list (X11 or XWayland)
            'wayland' if not found in X11 (native Wayland)
            'unknown' if we can't determine (e.g. XWayland not available)
        """
        if not self._has_xwayland:
            return 'wayland'
            
        # Check if it exists in X11
        if super()._find_window_recursive(self._display.screen().root, window_name):
            return 'x11'
            
        return 'wayland'

    def click(self, x: int, y: int) -> None:
        """
        Simulate a mouse click at coordinates.
        
        Uses inherited X11 XTest for global mouse simulation.
        
        Args:
            x: X coordinate
            y: Y coordinate
        """
        if not self._has_xwayland:
            raise NotImplementedError(
                "XWayland not available. Mouse click requires XWayland. "
                "Use AT-SPI Action interface for native Wayland apps."
            )
        
        # Delegate to X11 agent's click
        super().click(x, y)

