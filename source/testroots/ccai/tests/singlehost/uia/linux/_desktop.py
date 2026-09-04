"""
    .. module:: _desktop
    :platform: Linux
    :synopsis: Environment gates for the Linux desktop-automation tests.

    These tests drive real GTK applications through AT-SPI.  Whether that is
    possible is a property of the host session -- a display, an accessibility
    bus, the application binary -- not of the code under test, so an
    unavailable prerequisite is a SKIP, never a failure.  The libreoffice
    tests already followed that rule; this module makes it the single path
    for all of them.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


import os
import subprocess

from typing import Any, List, Optional

from ccai.errors.exceptions import SkipError


def require_pyatspi() -> None:
    """
        Skip unless the AT-SPI Python bindings import on this host.
    """
    try:
        import pyatspi  # noqa: F401
    except Exception as xcpt:  # ImportError, or a GI failure at import time
        raise SkipError("pyatspi is not usable on this host: {}".format(xcpt))
    return


def require_display() -> None:
    """
        Skip unless a graphical session is reachable from this process.
    """
    if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
        raise SkipError("no DISPLAY / WAYLAND_DISPLAY; desktop automation needs a session")
    return


def require_automation_engine() -> Any:
    """
        Return the platform automation engine, or skip when its agents
        cannot be initialised (no accessibility bus, unknown compositor).
    """
    from ccai.uia.factory import AutomationFactory

    try:
        rtnval = AutomationFactory.get_automation_engine()
    except ImportError as xcpt:
        raise SkipError("desktop automation unavailable: {}".format(xcpt))
    return rtnval


def launch_or_skip(argv: List[str], *, env: Optional[dict] = None) -> subprocess.Popen:
    """
        Launch a desktop application, skipping when its binary is absent.

        :param argv: The command line.
        :param env: Optional environment for the child.

        :returns: The running process.
    """
    try:
        rtnval = subprocess.Popen(argv, env=env)
    except FileNotFoundError:
        raise SkipError("{} is not installed on this host".format(argv[0]))
    return rtnval
