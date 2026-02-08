
import platform
import subprocess
import time
import os

from automojo import testbase
from automojo.uia.factory import AutomationFactory


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
        # If gnome-calculator not installed, skip or fail depending on strictness
        # For now, fail as tests should have environment ready
        testbase.assert_equal(True, False, "gnome-calculator not found")

    try:
        # Give it time to appear
        time.sleep(2.0)
        testbase.assert_equal(proc.poll() is None, True)

        automation = AutomationFactory.get_automation_engine()
        
        # Retry finding window a few times
        main_window = None
        for _ in range(5):
             time.sleep(1.0)
             app = automation.get_application_by_name("gnome-calculator")
             if not app:
                 app = automation.get_application_by_name("Calculator")
             
             if app:
                 windows = app.get_windows()
                 if windows:
                     main_window = windows[0]
                     break
        
        testbase.assert_equal(main_window is not None, True, "Could not find gnome-calculator window")

        # Verify detection type via the agent
        # The window wrapper (LinuxElement) has _wm_agent. 
        # Ideally we access via specific API if available, or check private agent as this is a platform test
        
        wm_agent = main_window._wm_agent
        if hasattr(wm_agent, 'detect_window_type'):
             # Should be 'x11' because we forced GDK_BACKEND=x11
             win_type = wm_agent.detect_window_type(main_window.name)
             print(f"Window '{main_window.name}' detected as: {win_type}")
             testbase.assert_equal(win_type, 'x11', "Forced X11 app should be detected as 'x11'")
        else:
             print("Warning: WM Agent does not support detection (Pure X11 agent?)")
             # If it's pure X11 agent, it doesn't have detect_window_type, essentially defaulting to X11 handling
             pass

    finally:
        proc.terminate()
        proc.wait()


def test_linux_window_detection_default():
    """
        Verifies window detection for default launch (likely Wayland in this environment).
        Note: If the system is X11, this will detect x11. If Wayland, likely wayland.
        We mainly verify it returns a valid type.
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
        
        # Retry finding window
        main_window = None
        for _ in range(5):
             time.sleep(1.0)
             app = automation.get_application_by_name("gnome-calculator")
             if not app:
                 app = automation.get_application_by_name("Calculator")
             
             if app:
                 windows = app.get_windows()
                 if windows:
                     main_window = windows[0]
                     break
        
        testbase.assert_equal(main_window is not None, True, "Could not find gnome-calculator window")

        wm_agent = main_window._wm_agent
        if hasattr(wm_agent, 'detect_window_type'):
             win_type = wm_agent.detect_window_type(main_window.name)
             print(f"Default Window detected as: {win_type}")
             
             # We expect either 'x11' or 'wayland'
             is_valid = win_type in ['x11', 'wayland']
             testbase.assert_equal(is_valid, True, f"Invalid window type detected: {win_type}")
             
             # In our specific environment (Wayland), we expect 'wayland' for native apps
             # But tests might run elsewhere, so we just ensure it's valid. 
             # (Optional: check env to be stricter)
             if os.environ.get("WAYLAND_DISPLAY"):
                  # On Wayland, default gnome-calculator usually runs as native Wayland
                  # unless forced otherwise or missing wayland plugin?
                  # We'll just log it for now.
                  pass

    finally:
        proc.terminate()
        proc.wait()
