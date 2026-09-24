"""
    .. module:: test_automation_shutdown
        :synopsis: Tests for the automation engine shutdown hook: LinuxAutomation.shutdown closes its agents,
                   the base engine supports ``with`` blocks, and the process-wide engine is shut down at exit.
"""

import atexit

from ccai import testbase

from ccai.uia import wellknown
from ccai.uia.platforms.base import AutomationEngine
from ccai.uia.platforms.linux.automation import LinuxAutomation
from ccai.testbase.mocking import create_module_patch


class FakeAgent:
    """
        An agent that records how often it was closed and can be told to fail.
    """

    def __init__(self, fail: bool = False):
        self.close_count = 0
        self.fail = fail
        return

    def close(self) -> None:
        self.close_count += 1
        if self.fail:
            raise OSError("cannot release the device")
        return


class FakeEngine(AutomationEngine):
    """
        A minimal engine that records shutdown calls.
    """

    def __init__(self, fail: bool = False):
        self.shutdown_count = 0
        self.fail = fail
        return

    def get_application_by_name(self, application_name: str):
        return None

    def shutdown(self) -> None:
        self.shutdown_count += 1
        if self.fail:
            raise OSError("cannot release the device")
        return


def _linux_engine(wm_agent, access_agent) -> LinuxAutomation:
    """
        Builds a LinuxAutomation around fake agents without running the platform detection in __init__.
    """
    engine = LinuxAutomation.__new__(LinuxAutomation)
    engine._wm_agent = wm_agent
    engine._access_agent = access_agent
    engine._shut_down = False
    return engine


def test_linux_shutdown_closes_both_agents_once():
    """
        shutdown() closes the window manager and accessibility agents, and a second call does nothing.
    """
    wm_agent = FakeAgent()
    access_agent = FakeAgent()
    engine = _linux_engine(wm_agent, access_agent)

    engine.shutdown()
    engine.shutdown()

    testbase.assert_equal(wm_agent.close_count, 1)
    testbase.assert_equal(access_agent.close_count, 1)
    return


def test_linux_shutdown_closes_the_accessibility_agent_when_the_window_manager_agent_fails():
    """
        A failure closing the window manager agent propagates, and the accessibility agent is still closed.
    """
    wm_agent = FakeAgent(fail=True)
    access_agent = FakeAgent()
    engine = _linux_engine(wm_agent, access_agent)

    raised = None
    try:
        engine.shutdown()
    except OSError as xcpt:
        raised = xcpt

    testbase.assert_true(raised is not None, "the window manager agent failure propagates")
    testbase.assert_equal(access_agent.close_count, 1)
    return


def test_linux_shutdown_without_agents():
    """
        An engine whose agents failed to initialize shuts down without error.
    """
    engine = _linux_engine(None, None)
    engine.shutdown()
    testbase.assert_equal(engine._shut_down, True)
    return


def test_engine_with_block_shuts_down():
    """
        Leaving a ``with`` block shuts the engine down, also when the block raises, and the exception is kept.
    """
    engine = FakeEngine()
    with engine as entered:
        testbase.assert_true(entered is engine, "the with block gets the engine")
    testbase.assert_equal(engine.shutdown_count, 1)

    engine = FakeEngine()
    raised = None
    try:
        with engine:
            raise ValueError("inside the block")
    except ValueError as xcpt:
        raised = xcpt
    testbase.assert_true(raised is not None, "the exception from the block is not suppressed")
    testbase.assert_equal(engine.shutdown_count, 1)
    return


def test_base_engine_shutdown_does_nothing():
    """
        Engines that hold no resources inherit a shutdown() that does nothing.
    """

    class PlainEngine(AutomationEngine):
        def get_application_by_name(self, application_name: str):
            return None

    PlainEngine().shutdown()
    return


def test_singleton_registers_the_exit_hook_once_and_shutdown_releases_it():
    """
        The process-wide engine registers one exit hook when it is created; shutdown_uia_controller() shuts it
        down and the next call creates a new engine.
    """
    saved = wellknown.CONTROLLER_SINGLETON_INST
    saved_factory = wellknown.AutomationFactory
    wellknown.CONTROLLER_SINGLETON_INST = None
    registered = []

    class FakeFactory:
        @staticmethod
        def get_automation_engine():
            return FakeEngine()

    wellknown.AutomationFactory = FakeFactory
    try:
        with create_module_patch(atexit, "register") as mock_register:
            mock_register.configure(side_effect=lambda func: registered.append(func))

            first = wellknown.UiaControllerSingleton()
            again = wellknown.UiaControllerSingleton()
            testbase.assert_true(first is again, "the same engine is returned while it is alive")
            testbase.assert_equal(len(registered), 1)

            wellknown.shutdown_uia_controller()
            testbase.assert_equal(first.shutdown_count, 1)
            testbase.assert_true(wellknown.CONTROLLER_SINGLETON_INST is None, "the singleton is released")

            wellknown.shutdown_uia_controller()
            testbase.assert_equal(first.shutdown_count, 1)

            second = wellknown.UiaControllerSingleton()
            testbase.assert_true(second is not first, "a new engine is created after shutdown")
    finally:
        wellknown.CONTROLLER_SINGLETON_INST = saved
        wellknown.AutomationFactory = saved_factory
    return


def test_exit_hook_reports_a_failed_shutdown_without_raising():
    """
        The exit hook logs a failed shutdown instead of raising while the interpreter exits.
    """
    saved = wellknown.CONTROLLER_SINGLETON_INST
    engine = FakeEngine(fail=True)
    wellknown.CONTROLLER_SINGLETON_INST = engine
    try:
        wellknown._shutdown_uia_controller_at_exit()
    finally:
        wellknown.CONTROLLER_SINGLETON_INST = saved

    testbase.assert_equal(engine.shutdown_count, 1)
    return
