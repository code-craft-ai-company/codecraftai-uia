"""
    .. module:: fakeuinput
    :platform: Darwin, Linux, Unix
    :synopsis: A stand-in for the ``/dev/uinput`` device, for display-free tests of the
               uinput lifecycle of :class:`WaylandGnomeWindowManagerAgent`.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


import errno
import os
import sys
import types

from contextlib import ExitStack
from typing import Any, List, Optional, Tuple
from unittest.mock import patch

from ccai.uia.platforms.linux.agents.wayland.gnome import waylandgnomewindowmanageragent as agentmodule
from ccai.uia.platforms.linux.agents.x11.x11windowmanageragent import X11WindowManagerAgent

from ccai.testshared.fakes.uia.fakeclock import FakeClock


UINPUT_PATH = "/dev/uinput"

# The uinput ioctl requests the agent issues, as defined in linux/uinput.h.
UI_DEV_CREATE = 0x5501
UI_DEV_DESTROY = 0x5502


class FakeUinputDevice:
    """
        Stands in for ``/dev/uinput``.  Opening the device path hands out a real
        descriptor on :data:`os.devnull`, so a test can check whether the agent
        closed it, and the ``fcntl`` stand-in records every ioctl request.  An
        ioctl for ``fail_request`` raises ``OSError`` the way the kernel rejects
        a request.
    """

    def __init__(self, fail_request: Optional[int] = None):
        self._fail_request = fail_request
        self._real_open = os.open
        self.fd: Optional[int] = None
        self.ioctls: List[Tuple[int, int]] = []
        self.fcntl_module = types.SimpleNamespace(ioctl=self.ioctl)
        return

    def open(self, path: str, flags: int, *args: Any, **kwargs: Any) -> int:
        """
            Replaces :func:`os.open`: the device path opens :data:`os.devnull`, any
            other path is opened for real.
        """
        if path == UINPUT_PATH:
            self.fd = self._real_open(os.devnull, os.O_WRONLY)
            rtnval = self.fd
        else:
            rtnval = self._real_open(path, flags, *args, **kwargs)
        return rtnval

    def ioctl(self, fd: int, request: int, arg: Any = 0, mutate_flag: bool = True) -> int:
        """
            Replaces :func:`fcntl.ioctl`: records the request and fails the configured one.
        """
        self.ioctls.append((fd, request))
        if request == self._fail_request:
            raise OSError(errno.EINVAL, "uinput rejected ioctl request 0x{:x}".format(request))
        return 0

    def requests(self) -> List[int]:
        """
            The ioctl requests issued so far, in call order.
        """
        rtnval = []
        for _fd, request in self.ioctls:
            rtnval.append(request)
        return rtnval

    def is_open(self) -> bool:
        """
            True when the descriptor handed out for the device is still open.
        """
        rtnval = True
        try:
            os.fstat(self.fd)
        except OSError:
            rtnval = False
        return rtnval


class FakeBrokerClient:
    """
        Stands in for the Automation Broker client; the uinput tests never call it.
    """

    def __init__(self):
        return


def _no_x_display(agent: X11WindowManagerAgent) -> None:
    """
        Replaces :meth:`X11WindowManagerAgent.__init__` so no X display is opened;
        the Wayland agent records that XWayland is unavailable.
    """
    raise ImportError("no X display in the uinput tests")


def enter_fake_wayland_session(stack: ExitStack, device: FakeUinputDevice) -> None:
    """
        Patches, for the life of ``stack``, everything
        :class:`WaylandGnomeWindowManagerAgent` touches outside of Python so it can
        be constructed and closed on any POSIX host: ``WAYLAND_DISPLAY`` is set,
        the X11 base constructor and the broker client are stubbed, ``gi`` is
        unavailable, ``/dev/uinput`` and ``fcntl`` are served by ``device``, and
        the agent module's ``time`` is a :class:`FakeClock`.

        :param stack: The exit stack that owns the patches.
        :param device: The uinput stand-in.
    """
    stack.enter_context(patch.dict(os.environ, {"WAYLAND_DISPLAY": "wayland-test"}))
    stack.enter_context(patch.object(X11WindowManagerAgent, "__init__", _no_x_display))
    stack.enter_context(patch.object(agentmodule, "BrokerClient", FakeBrokerClient))
    stack.enter_context(patch.object(agentmodule, "time", FakeClock()))
    stack.enter_context(patch.object(os, "open", device.open))
    stack.enter_context(patch.dict(sys.modules, {"gi": None, "fcntl": device.fcntl_module}))
    return
