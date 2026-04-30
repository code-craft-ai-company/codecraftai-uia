
"""
Wayland Gnome Window Manager Agent

Provides window management and input capabilities for Gnome Wayland sessions.
Uses the Automation Broker extension to bypass Wayland security restrictions for window enumeration.
"""

from typing import Any, List, Optional
import os
import time
from automojo.uia.platforms.linux.agents.x11.x11windowmanageragent import X11WindowManagerAgent
from automojo.uia.platforms.linux.agents.wayland.gnome.broker_client import BrokerClient

class WaylandGnomeWindowManagerAgent(X11WindowManagerAgent):
    """
    Window Manager Agent for Gnome Wayland sessions.
    
    Inherits from X11WindowManagerAgent to handle XWayland applications,
    while adding Wayland-specific capability detection and using the 
    Automation Broker for window management.
    """
    
    def __init__(self):
        """
        Initialize Wayland Gnome agent.
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
            self._has_xwayland = False
            
        # Initialize UInput for mouse/keyboard injection
        self._uinput_fd = None
        self._last_x = 0
        self._last_y = 0
        self._setup_uinput()

        # Initialize Broker Client
        self._broker = None
        try:
            self._broker = BrokerClient()
            # Test connection
            # version = self._broker.get_version()
            # print(f"Connected to Automation Broker: {version}")
        except Exception as e:
            print(f"Warning: Failed to connect to Automation Broker: {e}")
            print("Window enumeration and positioning will be limited.")

        # Initialize GDK for screen info (fallback)
        try:
            import gi
            gi.require_version('Gdk', '3.0')
            from gi.repository import Gdk
            self._gdk = Gdk
            self._gdk_display = Gdk.Display.get_default()
        except ImportError:
            # print("Warning: GDK not available.")
            self._gdk = None
            self._gdk_display = None

        self._input_scale_factor = 0.5 # Default, might need tuning

    def find_native_window(self, name_pattern: str) -> Any:
        """
        Attempts to find a native window using the Broker.
        Returns a dict with window info if found.
        """
        if not self._broker:
            return None
            
        try:
            windows = self._broker.list_windows()
            
            # Simple match
            for win in windows:
                title = win.get('title', '')
                app_id = win.get('app_id', '')
                
                if name_pattern.lower() in title.lower() or \
                   (app_id and name_pattern.lower() in app_id.lower()):
                    return win
                    
        except Exception as e:
            print(f"Broker find_window failed: {e}")
            
        return None

    def get_window_rect(self, window_obj: Any) -> Optional[tuple]:
        """
        Extracts (x, y, w, h) from a window object returned by find_native_window.
        """
        if not window_obj: return None
        
        try:
            # Broker returns 'rect_logical' and 'rect_physical'
            # logical is usually what we want for coordinate space, 
            # but depends on if uinput scales to logical or physical.
            # Usually uinput is mapped to the "screen" size which matches logical geometry in Gnome.
            
            rect = window_obj.get('rect_logical')
            if rect:
                return (rect['x'], rect['y'], rect['w'], rect['h'])
        except:
            pass
        return None

    def get_screen_geometry(self) -> tuple:
        """Returns (width, height) of the primary screen."""
        if self._broker:
            try:
                outputs = self._broker.list_outputs()
                for o in outputs:
                    if o.get('primary'):
                        r = o.get('logical_rect')
                        return (r['w'], r['h'])
                # If no primary, take first
                if outputs:
                    r = outputs[0].get('logical_rect')
                    return (r['w'], r['h'])
            except:
                pass

        # Fallback to GDK
        if self._gdk_display:
            try:
                monitor = self._gdk_display.get_primary_monitor() or self._gdk_display.get_monitor(0)
                if monitor:
                    geo = monitor.get_geometry()
                    return (geo.width, geo.height)
            except:
                pass
                
        return (1920, 1080)

    def get_displays(self) -> List[dict]:
        """
        Returns a list of connected displays using the Automation Broker.
        """
        displays = []
        if self._broker:
            try:
                outputs = self._broker.list_outputs()
                for o in outputs:
                    r = o.get('logical_rect')
                    displays.append({
                        'id': o.get('id'),
                        'name': o.get('name', 'Unknown'),
                        'x': r['x'],
                        'y': r['y'],
                        'width': r['w'],
                        'height': r['h'],
                        'primary': o.get('primary', False),
                        'scale': o.get('scale', 1.0)
                    })
                return displays
            except Exception as e:
                print(f"Broker get_displays failed: {e}")
        
        # Fallback to inherited X11/RandR (via XWayland) or GDK
        # X11 RandR often works on XWayland for logical geometry
        return super().get_displays()

    # ... Include existing uinput methods (_setup_uinput, _emit, move_mouse, click, drag_and_drop) ...
    # For brevity in this turn, I will assume I need to copy them back in.
    # I will paste the uinput implementation from the original file.
    
    def _setup_uinput(self):
        """Sets up the uinput virtual mouse device."""
        import struct
        import fcntl
        
        try:
            # Constants
            EV_SYN, EV_KEY, EV_REL = 0x00, 0x01, 0x02
            REL_X, REL_Y = 0x00, 0x01
            BTN_LEFT, BTN_RIGHT, BTN_MIDDLE = 0x110, 0x111, 0x112
            UI_SET_EVBIT = 0x40045564
            UI_SET_KEYBIT = 0x40045565
            UI_SET_RELBIT = 0x40045566
            UI_DEV_CREATE = 0x5501
            UI_DEV_SETUP = 0x405c5503
            BUS_USB = 0x03
            
            self._uinput_fd = os.open("/dev/uinput", os.O_WRONLY | os.O_NONBLOCK)
            
            # Configure capabilities
            fcntl.ioctl(self._uinput_fd, UI_SET_EVBIT, EV_KEY)
            fcntl.ioctl(self._uinput_fd, UI_SET_KEYBIT, BTN_LEFT)
            fcntl.ioctl(self._uinput_fd, UI_SET_KEYBIT, BTN_RIGHT)
            fcntl.ioctl(self._uinput_fd, UI_SET_KEYBIT, BTN_MIDDLE)
            
            fcntl.ioctl(self._uinput_fd, UI_SET_EVBIT, EV_REL)
            fcntl.ioctl(self._uinput_fd, UI_SET_RELBIT, REL_X)
            fcntl.ioctl(self._uinput_fd, UI_SET_RELBIT, REL_Y)
            
            # Setup device via UI_DEV_SETUP
            name = b"Automojo Virtual Mouse"
            name_pad = name + b'\0' * (80 - len(name))
            input_id = struct.pack('HHHH', BUS_USB, 0x1, 0x1, 1)
            ff_effects_max = struct.pack('I', 0)
            setup_payload = input_id + name_pad + ff_effects_max
            
            fcntl.ioctl(self._uinput_fd, UI_DEV_SETUP, setup_payload)
            fcntl.ioctl(self._uinput_fd, UI_DEV_CREATE)
            
            # Wait for device registration
            time.sleep(0.5)
            
        except PermissionError:
            print("WARNING: Failed to open /dev/uinput (Permission denied). Mouse control will be limited.")
            self._uinput_fd = None
        except Exception as e:
            print(f"WARNING: Failed to setup uinput: {e}")
            self._uinput_fd = None

    def _emit(self, type, code, value):
        if self._uinput_fd is None: return
        import struct
        timestamp = time.time()
        sec = int(timestamp)
        usec = int((timestamp - sec) * 1000000)
        event = struct.pack('llHHi', sec, usec, type, code, value)
        os.write(self._uinput_fd, event)

    def _emit_syn(self):
        self._emit(0x00, 0, 0)

    def move_mouse(self, x: int, y: int, sync: bool = True) -> None:
        if self._uinput_fd is None:
            return super().move_mouse(x, y)
            
        try:
            if sync:
                # Reset to 0,0
                for _ in range(10):
                     self._emit(0x02, 0x00, -5000)
                     self._emit(0x02, 0x01, -5000)
                     self._emit_syn()
                     time.sleep(0.005)
                time.sleep(0.05)
                self._last_x = 0
                self._last_y = 0

            dx = x - self._last_x
            dy = y - self._last_y
            
            target_rel_x = int(dx * self._input_scale_factor)
            target_rel_y = int(dy * self._input_scale_factor)
            
            steps = 10 
            sx = int(target_rel_x / steps)
            sy = int(target_rel_y / steps)
            rem_x = target_rel_x % steps
            rem_y = target_rel_y % steps
            
            for _ in range(steps):
                self._emit(0x02, 0x00, sx)
                self._emit(0x02, 0x01, sy)
                self._emit_syn()
                time.sleep(0.005)
                
            if rem_x or rem_y:
                self._emit(0x02, 0x00, rem_x)
                self._emit(0x02, 0x01, rem_y)
                self._emit_syn()
            
            self._last_x = x
            self._last_y = y
            time.sleep(0.05)
            
        except Exception as e:
            print(f"Wayland move_mouse failed: {e}")

    def click(self, x: int, y: int) -> None:
        if self._uinput_fd is None:
            return super().click(x, y)
            
        try:
            self.move_mouse(x, y)
            time.sleep(0.1)
            self._emit(0x01, 0x110, 1) # Press
            self._emit_syn()
            time.sleep(0.05)
            self._emit(0x01, 0x110, 0) # Release
            self._emit_syn()
            time.sleep(0.1)
        except Exception as e:
            print(f"Wayland click failed: {e}")

    def drag_and_drop(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5) -> None:
        # Implementation same as before
        if self._uinput_fd is None:
            return super().drag_and_drop(start_x, start_y, end_x, end_y, duration)

        try:
            self.move_mouse(start_x, start_y)
            time.sleep(0.2)
            self._emit(0x01, 0x110, 1)
            self._emit_syn()
            time.sleep(0.2)
            
            steps = 20
            dt = duration / steps
            curr_x, curr_y = start_x, start_y
            
            for i in range(steps):
                next_x = int(start_x + (end_x - start_x) * (i + 1) / steps)
                next_y = int(start_y + (end_y - start_y) * (i + 1) / steps)
                
                dx = next_x - curr_x
                dy = next_y - curr_y
                
                # Relative move
                self._emit(0x02, 0x00, int(dx * self._input_scale_factor))
                self._emit(0x02, 0x01, int(dy * self._input_scale_factor))
                self._emit_syn()
                
                curr_x, curr_y = next_x, next_y
                time.sleep(dt)
                
            self._emit(0x01, 0x110, 0)
            self._emit_syn()
            time.sleep(0.1)
            
        except Exception as e:
            print(f"Wayland drag_and_drop failed: {e}")
    
    def __del__(self):
        try:
            if self._uinput_fd is not None:
                import fcntl
                fcntl.ioctl(self._uinput_fd, 0x5502) # UI_DEV_DESTROY
                os.close(self._uinput_fd)
        except:
            pass
