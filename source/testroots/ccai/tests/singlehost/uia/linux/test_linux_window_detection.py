
import platform
import subprocess
import time
import os

from ccai import testbase
from ccai.errors.exceptions import SkipError
from ccai.tests.singlehost.uia.linux._desktop import (
    launch_or_skip, require_automation_engine, require_display, require_pyatspi,
)
from ccai.uia.factory import AutomationFactory
from ccai.uia.platforms.linux.mappings.calculator import Calculator


def _try_import_pyatspi() -> bool:
    try:
        import pyatspi  # noqa: F401
        return True
    except Exception:
        return False


def test_linux_window_detection_x11():
    """
        Verifies that window detection correctly identifies X11 windows 
        when an application is forced to run with GDK_BACKEND=x11.
        Refactored to use Declarative Mapping.
    """
    if platform.system() != "Linux":
        raise SkipError("the Linux desktop tests need a Linux host")

    require_pyatspi()
    require_display()

    # Launch gnome-calculator forced to X11
    env = os.environ.copy()
    env['GDK_BACKEND'] = 'x11'
    proc = launch_or_skip(["gnome-calculator"], env=env)

    try:
        # Give it time to appear
        time.sleep(2.0)
        testbase.assert_equal(proc.poll() is None, True)

        automation = AutomationFactory.get_automation_engine()
        
        # Declarative Attach
        app = Calculator.attach(automation)
        testbase.assert_equal(app is not None, True, "Could not attach to Calculator")

        # MainWindow
        main_window = Calculator.MainWindow.resolve(app)
        
        # Fallback if window not found by strict mapping (though it should be)
        if not main_window:
             windows = app.get_windows()
             if windows:
                 main_window = windows[0]
        
        testbase.assert_equal(main_window is not None, True, "Could not find gnome-calculator window")

        # Verify detection type via the agent
        # The window wrapper (LinuxElement) has _wm_agent. 
        
        wm_agent = getattr(main_window, '_wm_agent', None)
        # WeakRef handling if needed, but property usually returns the agent or None
        if hasattr(main_window, 'wm_agent'):
             wm_agent = main_window.wm_agent
             
        if wm_agent and hasattr(wm_agent, 'detect_window_type'):
             # Should be 'x11' because we forced GDK_BACKEND=x11
             win_type = wm_agent.detect_window_type(main_window.name)
             print(f"Window '{main_window.name}' detected as: {win_type}")
             testbase.assert_equal(win_type, 'x11', "Forced X11 app should be detected as 'x11'")
        else:
             print("Warning: WM Agent does not support detection (Pure X11 agent?)")
             pass

    finally:
        proc.terminate()
        proc.wait()


def test_linux_window_detection_default():
    """
        Verifies window detection for default launch.
        Refactored to use Declarative Mapping.
    """
    if platform.system() != "Linux":
        raise SkipError("the Linux desktop tests need a Linux host")

    require_pyatspi()
    require_display()

    # Launch gnome-calculator with default backend
    proc = launch_or_skip(["gnome-calculator"])

    try:
        time.sleep(2.0)
        
        automation = AutomationFactory.get_automation_engine()
        
        # Declarative Attach
        app = Calculator.attach(automation)
        testbase.assert_equal(app is not None, True, "Could not attach to Calculator")

        main_window = Calculator.MainWindow.resolve(app)
        if not main_window:
             windows = app.get_windows()
             if windows:
                 main_window = windows[0]
        
        testbase.assert_equal(main_window is not None, True, "Could not find gnome-calculator window")

        wm_agent = getattr(main_window, 'wm_agent', None)
        if wm_agent and hasattr(wm_agent, 'detect_window_type'):
             win_type = wm_agent.detect_window_type(main_window.name)
             print(f"Default Window detected as: {win_type}")
             
             # We expect either 'x11' or 'wayland'
             is_valid = win_type in ['x11', 'wayland']
             testbase.assert_equal(is_valid, True, f"Invalid window type detected: {win_type}")
             
             if os.environ.get("WAYLAND_DISPLAY"):
                  pass

    finally:
        proc.terminate()
        proc.wait()

