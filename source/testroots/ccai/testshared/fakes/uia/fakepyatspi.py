"""
    .. module:: fakepyatspi
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Stand-ins for pyatspi accessibles and registry, for display-free tests of
               :class:`PyAtspiAccessibilityAgent` and the Linux wrappers that call it.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


import types

from typing import Optional
from unittest.mock import patch

from ccai.uia.platforms.linux.agents.common import pyatspi_agent as agentmodule


class FakeValueInterface:
    """
        Stands in for the pyatspi Value interface; assigning ``currentValue`` records
        the value or raises the configured failure.
    """

    def __init__(self, failure: Optional[Exception] = None):
        self._current_value = 0.0
        self._failure = failure
        return

    @property
    def currentValue(self) -> float:
        return self._current_value

    @currentValue.setter
    def currentValue(self, value: float) -> None:
        if self._failure is not None:
            raise self._failure
        self._current_value = value
        return


class FakeAccessible:
    """
        Stands in for a pyatspi accessible.  ``queryValue`` returns the Value
        interface, or raises ``NotImplementedError`` like pyatspi does when the
        accessible does not provide it.
    """

    def __init__(self, name: str, role_name: str, value_iface: Optional[FakeValueInterface] = None):
        self.name = name
        self._role_name = role_name
        self._value_iface = value_iface
        return

    def getRoleName(self) -> str:
        return self._role_name

    def queryValue(self) -> FakeValueInterface:
        if self._value_iface is None:
            raise NotImplementedError("Value interface not supported")
        return self._value_iface


def create_pyatspi_agent() -> agentmodule.PyAtspiAccessibilityAgent:
    """
        Constructs a :class:`PyAtspiAccessibilityAgent` against a stand-in pyatspi
        registry, so the agent can be built on hosts without pyatspi.

        :returns: The agent.
    """
    fake_pyatspi = types.SimpleNamespace(Registry=object())
    with patch.object(agentmodule, "pyatspi", fake_pyatspi):
        rtnval = agentmodule.PyAtspiAccessibilityAgent()
    return rtnval
