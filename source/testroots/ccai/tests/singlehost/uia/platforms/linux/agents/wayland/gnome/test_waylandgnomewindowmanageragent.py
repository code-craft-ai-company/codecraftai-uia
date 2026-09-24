"""
    Display-free tests for the ``/dev/uinput`` lifecycle of
    :class:`WaylandGnomeWindowManagerAgent`: the explicit, idempotent
    :meth:`close`, context-manager support, the ``__del__`` fallback, and the
    release of the descriptor when the device setup fails part way.

    The device is the stand-in from :mod:`ccai.testshared.fakes.uia.fakeuinput`,
    which hands out a real descriptor (on the null device) and records the ioctl
    requests, so no uinput device, Wayland session or X display is needed.
"""

import gc
import os

from contextlib import ExitStack

from ccai import testbase
from ccai.errors.exceptions import SkipError

from ccai.uia.platforms.linux.agents.wayland.gnome.waylandgnomewindowmanageragent import WaylandGnomeWindowManagerAgent

from ccai.testshared.fakes.uia.fakeuinput import (
    UI_DEV_CREATE,
    UI_DEV_DESTROY,
    FakeUinputDevice,
    enter_fake_wayland_session,
)


def _require_posix_open_flags() -> None:
    """
        The agent opens ``/dev/uinput`` with ``os.O_NONBLOCK``, which Windows does
        not define, so the setup path can only be exercised on POSIX hosts.

        :raises: SkipError on hosts without ``os.O_NONBLOCK``.
    """
    if not hasattr(os, "O_NONBLOCK"):
        raise SkipError("the uinput setup uses os.O_NONBLOCK, which this host does not define")
    return


def test_close_destroys_the_device_and_closes_the_descriptor():
    """
        ``close`` issues ``UI_DEV_DESTROY`` for the device the constructor created
        and closes its descriptor.
    """
    _require_posix_open_flags()

    device = FakeUinputDevice()
    with ExitStack() as stack:
        enter_fake_wayland_session(stack, device)
        agent = WaylandGnomeWindowManagerAgent()

        testbase.assert_true(device.fd is not None, "the constructor opened /dev/uinput")
        testbase.assert_true(UI_DEV_CREATE in device.requests(), "the constructor created the device")
        testbase.assert_true(device.is_open(), "the descriptor is open before close()")

        agent.close()

        testbase.assert_equal(device.requests()[-1], UI_DEV_DESTROY)
        testbase.assert_equal(device.ioctls[-1][0], device.fd)
        testbase.assert_false(device.is_open(), "close() closed the descriptor")

    return


def test_close_is_idempotent():
    """
        A second ``close`` does nothing: the device is destroyed once and no
        error is raised.
    """
    _require_posix_open_flags()

    device = FakeUinputDevice()
    with ExitStack() as stack:
        enter_fake_wayland_session(stack, device)
        agent = WaylandGnomeWindowManagerAgent()

        agent.close()
        agent.close()

        destroy_count = device.requests().count(UI_DEV_DESTROY)
        testbase.assert_equal(destroy_count, 1)
        testbase.assert_false(device.is_open(), "the descriptor stays closed")

    return


def test_context_manager_closes_the_device_on_exit():
    """
        ``with agent`` yields the agent and closes it when the block exits.
    """
    _require_posix_open_flags()

    device = FakeUinputDevice()
    with ExitStack() as stack:
        enter_fake_wayland_session(stack, device)

        with WaylandGnomeWindowManagerAgent() as agent:
            testbase.assert_true(isinstance(agent, WaylandGnomeWindowManagerAgent), "the agent is yielded")
            testbase.assert_true(device.is_open(), "the device is open inside the block")

        testbase.assert_true(UI_DEV_DESTROY in device.requests(), "the device was destroyed on exit")
        testbase.assert_false(device.is_open(), "the descriptor was closed on exit")

    return


def test_context_manager_closes_the_device_and_propagates_an_error():
    """
        An exception raised inside the ``with`` block still closes the device and
        is not suppressed.
    """
    _require_posix_open_flags()

    device = FakeUinputDevice()
    with ExitStack() as stack:
        enter_fake_wayland_session(stack, device)

        raised = None
        try:
            with WaylandGnomeWindowManagerAgent():
                raise ValueError("failure inside the block")
        except ValueError as xcpt:
            raised = xcpt

        testbase.assert_true(raised is not None, "the error propagated out of the block")
        testbase.assert_false(device.is_open(), "the descriptor was closed on exit")

    return


def test_del_falls_back_to_close():
    """
        An agent that is dropped without ``close`` releases the device when it is
        finalized.
    """
    _require_posix_open_flags()

    device = FakeUinputDevice()
    with ExitStack() as stack:
        enter_fake_wayland_session(stack, device)
        agent = WaylandGnomeWindowManagerAgent()
        testbase.assert_true(device.is_open(), "the device is open while the agent is alive")

        del agent
        gc.collect()

        testbase.assert_true(UI_DEV_DESTROY in device.requests(), "the finalizer destroyed the device")
        testbase.assert_false(device.is_open(), "the finalizer closed the descriptor")

    return


def test_failed_setup_releases_the_descriptor():
    """
        When a configuration ioctl fails after ``/dev/uinput`` was opened, the
        descriptor is closed instead of dropped, and the agent falls back to no
        uinput device.
    """
    _require_posix_open_flags()

    device = FakeUinputDevice(fail_request=UI_DEV_CREATE)
    with ExitStack() as stack:
        enter_fake_wayland_session(stack, device)
        agent = WaylandGnomeWindowManagerAgent()

        testbase.assert_true(device.fd is not None, "/dev/uinput was opened")
        testbase.assert_false(device.is_open(), "the descriptor was released after the failed setup")

        # close() after a failed setup has nothing left to release.
        request_count = len(device.ioctls)
        agent.close()
        testbase.assert_equal(len(device.ioctls), request_count)

    return
