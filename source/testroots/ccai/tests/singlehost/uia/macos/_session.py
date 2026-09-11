"""
    .. module:: _session
    :platform: Darwin
    :synopsis: Environment gates for the macOS application-automation tests.

    These tests drive real applications through the Accessibility API.
    Whether that is possible is a property of the host session -- the
    application being installed, the process being trusted for Accessibility,
    a window-server session the API can serve -- not of the code under test,
    so an unavailable prerequisite is a SKIP, never a failure.  A host with
    the application installed and a usable Accessibility session runs the
    tests in full.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any

from ccai.errors.exceptions import SkipError


def require_application_installed(uia_controller: Any, application_name: str) -> None:
    """
        Skip unless the named application is installed on this host.

        The probe is the same metadata lookup the launch path performs, so a
        missing application is detected before anything is launched.

        :param uia_controller: The macOS automation engine.
        :param application_name: The display name of the application.
    """
    try:
        uia_controller.workspace.lookup_application_metadata_by_name(application_name)
    except ValueError:
        raise SkipError("{} is not installed on this host".format(application_name))
    return


def require_accessibility() -> None:
    """
        Skip unless the Accessibility API is usable from this process.

        Two distinct reasons are reported: the process is not trusted for
        Accessibility, or it is trusted but the API cannot answer queries in
        this session (a headless host with no window-server session).
    """
    from ccai.uia.platforms.macos.wrappers.uiaaccessibility import is_accessibility_trusted, is_accessibility_usable

    if is_accessibility_trusted(prompt=False) is False:
        raise SkipError("this process is not trusted for Accessibility (System Settings > Privacy & Security > Accessibility)")

    if is_accessibility_usable() is False:
        raise SkipError("the Accessibility API answers no queries in this session (headless host with no window-server session)")

    return
