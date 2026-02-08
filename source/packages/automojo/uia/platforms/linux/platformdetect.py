"""
Platform detection utilities for Linux display servers and window managers.
"""

import os
from typing import Literal, Optional


DisplayServerType = Literal['wayland', 'x11', 'unknown']


class PlatformDetector:
    """Detects Linux display server and session type."""
    
    @staticmethod
    def get_session_type() -> DisplayServerType:
        """
        Detect the current session type.
        
        Returns:
            'wayland' if running in Wayland session
            'x11' if running in pure X11 session  
            'unknown' if cannot determine
        """
        # Primary method: Check XDG_SESSION_TYPE
        session = os.environ.get('XDG_SESSION_TYPE', '').lower()
        if session == 'wayland':
            return 'wayland'
        if session == 'x11':
            return 'x11'
        
        # Fallback: Check for Wayland display
        if os.environ.get('WAYLAND_DISPLAY'):
            return 'wayland'
        
        # Fallback: Check for X11 display only
        if os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY'):
            return 'x11'
        
        return 'unknown'
    
    @staticmethod
    def has_xwayland() -> bool:
        """
        Check if XWayland is available (X11 compatibility on Wayland).
        
        Returns:
            True if running Wayland with XWayland bridge available
        """
        session = PlatformDetector.get_session_type()
        if session == 'wayland':
            # On Wayland, DISPLAY being set indicates XWayland is running
            return bool(os.environ.get('DISPLAY'))
        return False
    
    @staticmethod
    def get_compositor() -> Optional[str]:
        """
        Attempt to detect the Wayland compositor.
        
        Returns:
            Compositor name if detected ('mutter', 'kwin', 'sway', etc.)
            None if cannot determine or not using Wayland
        """
        session = PlatformDetector.get_session_type()
        if session != 'wayland':
            return None
        
        # Check common environment variables
        desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
        
        if 'gnome' in desktop:
            return 'mutter'  # GNOME Shell uses Mutter
        elif 'kde' in desktop or 'plasma' in desktop:
            return 'kwin'
        elif 'sway' in desktop:
            return 'sway'
        
        # Try to detect from session
        session_desktop = os.environ.get('DESKTOP_SESSION', '').lower()
        if 'gnome' in session_desktop:
            return 'mutter'
        elif 'plasma' in session_desktop:
            return 'kwin'
        
        return None
    
    @staticmethod
    def should_use_x11_agent() -> bool:
        """
        Determine if X11 window manager agent should be used.
        
        Returns:
            True if pure X11 session or XWayland is available
        """
        session = PlatformDetector.get_session_type()
        if session == 'x11':
            return True
        if session == 'wayland':
            return PlatformDetector.has_xwayland()
        return False
    
    @staticmethod
    def should_use_wayland_agent() -> bool:
        """
        Determine if Wayland window manager agent should be used.
        
        Returns:
            True if running in Wayland session
        """
        return PlatformDetector.get_session_type() == 'wayland'
    
    @staticmethod
    def get_summary() -> dict:
        """
        Get a summary of detected platform information.
        
        Returns:
            Dictionary with platform detection results
        """
        session = PlatformDetector.get_session_type()
        return {
            'session_type': session,
            'has_xwayland': PlatformDetector.has_xwayland(),
            'compositor': PlatformDetector.get_compositor(),
            'wayland_display': os.environ.get('WAYLAND_DISPLAY'),
            'x11_display': os.environ.get('DISPLAY'),
            'use_x11_agent': PlatformDetector.should_use_x11_agent(),
            'use_wayland_agent': PlatformDetector.should_use_wayland_agent(),
        }
