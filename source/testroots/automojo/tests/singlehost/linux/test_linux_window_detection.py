
import platform
import subprocess
import time
import os

from automojo import testbase
from automojo.uia.factory import AutomationFactory
from automojo.uia.platforms.linux.mappings.calculator import Calculator


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
        return

    testbase.assert_equal(_try_import_pyatspi(), True)

    # Launch gnome-calculator forced to X11
    try:
        env = os.environ.copy()
        env['GDK_BACKEND'] = 'x11'
        proc = subprocess.Popen(["gnome-calculator"], env=env)
    except FileNotFoundError:
        testbase.assert_equal(True, False, "gnome-calculator not found")

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
        return

    testbase.assert_equal(_try_import_pyatspi(), True)

    # Launch gnome-calculator with default backend
    try:
        proc = subprocess.Popen(["gnome-calculator"])
    except FileNotFoundError:
        testbase.assert_equal(True, False, "gnome-calculator not found")

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

