"""
Wayland Window Manager Agent

Provides window management and input capabilities for Wayland sessions.
Inherits from X11WindowManagerAgent to support XWayland applications.
"""

from typing import Any, List
import os
import time
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
            
        # Initialize UInput
        self._uinput_fd = None
        self._setup_uinput()

        # Initialize GDK for screen/mouse info
        try:
            import gi
            gi.require_version('Gdk', '3.0')
            from gi.repository import Gdk
            self._gdk = Gdk
            self._display = Gdk.Display.get_default()
        except ImportError:
            print("Warning: GDK not available. Screen/Mouse functions will range limited.")
            self._gdk = None
            self._display = None

        # Initialize Wnck for window management (if available)
        try:
            import gi
            try:
                gi.require_version('Wnck', '3.0')
                from gi.repository import Wnck
                self._wnck = Wnck
                self._wnck_screen = Wnck.Screen.get_default()
                # Wnck needs a main loop or force update to populate
                if self._wnck_screen:
                    self._wnck_screen.force_update()
            except (ImportError, ValueError):
                 print("Warning: Wnck not available. Native window finding disabled.")
                 self._wnck = None
        except Exception as e:
            print(f"Warning: Wnck init failed: {e}")
            self._wnck = None
            
        # Scaling factor for uinput events vs screen pixels.
        # Observed ~2x scaling in testing (1 pixel request = 2 screen pixels moved).
        # Defaulting to 0.5 to compensate.
        self._input_scale_factor = 0.5

    def find_native_window(self, name_pattern: str) -> Any:
        """
        Attempts to find a native window object (WnckWindow) matching the name pattern.
        """
        if not self._wnck or not self._wnck_screen:
            return None
            
        self._wnck_screen.force_update()
        windows = self._wnck_screen.get_windows()
        
        for win in windows:
            title = win.get_name()
            if title and name_pattern in title:
                return win
                
        return None

    def get_screen_geometry(self) -> tuple:
        """Returns (width, height) of the primary screen using GDK."""
        if self._display:
            try:
                # GDK 3.0 way
                monitor = self._display.get_primary_monitor() or self._display.get_monitor(0)
                if monitor:
                    geo = monitor.get_geometry()
                    return (geo.width, geo.height)
            except Exception as e:
                print(f"GDK get_screen_geometry failed: {e}")
        return (1920, 1080) # Fallback

    def get_mouse_position(self) -> tuple:
        """
        Returns the current mouse position.
        Attempts to use GDK first. If GDK returns (0,0) (common in Wayland),
        falls back to internal tracking.
        """
        if self._display:
            try:
                seat = self._display.get_default_seat()
                pointer = seat.get_pointer()
                screen, x, y = pointer.get_position()
                
                # If valid non-zero (or strictly if GDK works), update tracker
                # Problem: In Wayland, it might legitimately be 0,0.
                # But it usually returns 0,0 ALWAYS if restricted.
                # We can check if we moved there.
                
                # Heuristic: If GDK matches our internal tracker, trust it? 
                # Or just trust GDK if it changes? 
                # For now, if GDK says 0,0 and we think we are at 500,500, trust us.
                
                if (x, y) != (0, 0):
                    self._last_x = x
                    self._last_y = y
                    return (x, y)
                    
            except Exception:
                pass
                
        # Fallback to internal tracker
        return (self._last_x, self._last_y)

    def _setup_uinput(self):
        """Sets up the uinput virtual mouse device."""
        import struct
        import fcntl
        import time
        
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
            # print("DEBUG: Wayland UInput device created.")
            
        except ImportError:
            pass # Should not happen as we use stdlib
        except PermissionError:
            print("WARNING: Failed to open /dev/uinput (Permission denied). Mouse control will be limited.")
            self._uinput_fd = None
        except Exception as e:
            print(f"WARNING: Failed to setup uinput: {e}")
            self._uinput_fd = None

    def _emit(self, type, code, value):
        """Emits a uinput event."""
        if self._uinput_fd is None: return
        import struct
        timestamp = time.time()
        sec = int(timestamp)
        usec = int((timestamp - sec) * 1000000)
        event = struct.pack('llHHi', sec, usec, type, code, value)
        os.write(self._uinput_fd, event)

    def _emit_syn(self):
        self._emit(0x00, 0, 0) # EV_SYN, SYN_REPORT


    def move_mouse(self, x: int, y: int, sync: bool = True) -> None:
        """
        Moves mouse to (x, y).
        
        :param x: Target X coordinate.
        :param y: Target Y coordinate.
        :param sync: If True (default), forces a reset to (0,0) before moving to ensure absolute positioning accuracy.
                     If False, moves relative to the last known position (faster, but relies on tracker accuracy).
        """
        if self._uinput_fd is None:
            # Fallback to XTest if uinput failed
            return super().move_mouse(x, y)
            
        try:
            if sync:
                # Strategy: Throw cursor to top-left (0,0) with large negative delta
                # This 'resets' our known position state.
                # We send multiple large negative moves to ensure we hit the corner
                # regardless of screen size or acceleration.
                
                # 1. Reset to Top-Left
                for _ in range(10):
                     self._emit(0x02, 0x00, -5000) # REL_X
                     self._emit(0x02, 0x01, -5000) # REL_Y
                     self._emit_syn()
                     time.sleep(0.005)

                time.sleep(0.05)
                # We are now confirmed at 0,0
                self._last_x = 0
                self._last_y = 0

            # 2. Move to Target (x, y)
            # Calculate delta from current known position
            dx = x - self._last_x
            dy = y - self._last_y
            
            # Apply scaling to the TOTAL distance to move
            target_rel_x = int(dx * self._input_scale_factor)
            target_rel_y = int(dy * self._input_scale_factor)
            
            # Move in a few steps for smoothness/reliability
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
                
            # Final remainder
            if rem_x or rem_y:
                self._emit(0x02, 0x00, rem_x)
                self._emit(0x02, 0x01, rem_y)
                self._emit_syn()
            
            # Update internal state (store the LOGICAL position, not scaled)
            self._last_x = x
            self._last_y = y
            
            time.sleep(0.05)
            

            
            
        except Exception as e:
            print(f"Wayland move_mouse failed: {e}")

    def move_relative(self, dx: int, dy: int) -> None:
        """
        Moves the mouse relative to its current position.
        Updates internal tracker.
        """
        if self._uinput_fd is None:
             # XTest doesn't really have a relative move exposed easily via this agent structure
             # But for Wayland task we need this.
             return

        try:
             # Apply scaling
             scaled_dx = int(dx * self._input_scale_factor)
             scaled_dy = int(dy * self._input_scale_factor)
             
             self._emit(0x02, 0x00, scaled_dx) # REL_X
             self._emit(0x02, 0x01, scaled_dy) # REL_Y
             self._emit_syn()
             
             self._last_x += dx
             self._last_y += dy
        except Exception as e:
             print(f"Wayland move_relative failed: {e}")

    def click(self, x: int, y: int) -> None:
        """
        Moves mouse and clicks using uinput.
        """
        if self._uinput_fd is None:
            return super().click(x, y)
            
        try:
            self.move_mouse(x, y)
            time.sleep(0.1)
            
            # EV_KEY=0x01, BTN_LEFT=0x110
            self._emit(0x01, 0x110, 1) # Press
            self._emit_syn()
            time.sleep(0.05)
            
            self._emit(0x01, 0x110, 0) # Release
            self._emit_syn()
            time.sleep(0.1)
        except Exception as e:
            print(f"Wayland click failed: {e}")

    def drag_and_drop(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5) -> None:
        if self._uinput_fd is None:
            return super().drag_and_drop(start_x, start_y, end_x, end_y, duration)

        try:
            self.move_mouse(start_x, start_y)
            time.sleep(0.2)
            
            # Press
            self._emit(0x01, 0x110, 1)
            self._emit_syn()
            time.sleep(0.2)
            
            # Interpolate
            steps = 20
            dt = duration / steps
            
            # We need to re-read current position or just trust our math?
            # Trust math for relative interpolation
            curr_x, curr_y = start_x, start_y
            
            for i in range(steps):
                next_x = int(start_x + (end_x - start_x) * (i + 1) / steps)
                next_y = int(start_y + (end_y - start_y) * (i + 1) / steps)
                
                dx = next_x - curr_x
                dy = next_y - curr_y
                
                self._emit(0x02, 0x00, dx)
                self._emit(0x02, 0x01, dy)
                self._emit_syn()
                
                curr_x, curr_y = next_x, next_y
                time.sleep(dt)
                
            # Release
            self._emit(0x01, 0x110, 0)
            self._emit_syn()
            time.sleep(0.1)
            
        except Exception as e:
            print(f"Wayland drag_and_drop failed: {e}")

    def __del__(self):
        try:
            if self._uinput_fd is not None:
                # Destroy device?
                # CONST UI_DEV_DESTROY = 0x5502
                import fcntl
                fcntl.ioctl(self._uinput_fd, 0x5502)
                os.close(self._uinput_fd)
        except:
            pass

