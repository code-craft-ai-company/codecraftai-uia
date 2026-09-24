import atexit
import logging

from typing import Any

from ccai.uia.factory import AutomationFactory

logger = logging.getLogger(__name__)

CONTROLLER_SINGLETON_INST = None


def UiaControllerSingleton() -> Any:
    """
        Returns the process-wide automation engine, creating it on first use.  The engine is shut down
        automatically when the interpreter exits; call :func:`shutdown_uia_controller` to release it earlier.

        :returns: The automation engine for the current platform.
    """
    global CONTROLLER_SINGLETON_INST
    if CONTROLLER_SINGLETON_INST is None:
        CONTROLLER_SINGLETON_INST = AutomationFactory.get_automation_engine()
        atexit.register(_shutdown_uia_controller_at_exit)

    return CONTROLLER_SINGLETON_INST


def shutdown_uia_controller() -> None:
    """
        Shuts down the process-wide automation engine, if one was created, releasing the operating-system
        resources it holds.  The next call to :func:`UiaControllerSingleton` creates a new engine.

        :raises: OSError when the engine's resources cannot be released.
    """
    global CONTROLLER_SINGLETON_INST
    engine = CONTROLLER_SINGLETON_INST
    CONTROLLER_SINGLETON_INST = None
    if engine is not None:
        engine.shutdown()
    return


def _shutdown_uia_controller_at_exit() -> None:
    """
        Exit hook that shuts down the process-wide automation engine.
    """
    try:
        shutdown_uia_controller()
    except Exception as xcpt:
        # The interpreter is exiting and the operating system reclaims the resources anyway; report the failure
        # instead of letting it surface as an unhandled exception during shutdown.
        logger.warning("Shutting down the UIA automation engine at exit failed: %r", xcpt)
    return
