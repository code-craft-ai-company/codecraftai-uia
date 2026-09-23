"""
    Display-free tests for :meth:`PyAtspiAccessibilityAgent.set_value`.  The agent
    module's ``pyatspi`` binding is patched with a stand-in registry so the agent
    can be constructed on hosts without pyatspi, and the accessibles are small
    fakes of the pyatspi Value interface.
"""

import types

from typing import Optional
from unittest.mock import patch

from ccai import testbase

from ccai.uia.exceptions import InteractionError
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


def _create_agent() -> agentmodule.PyAtspiAccessibilityAgent:
    """
        Constructs the agent against a stand-in pyatspi registry.

        :returns: The agent.
    """
    fake_pyatspi = types.SimpleNamespace(Registry=object())
    with patch.object(agentmodule, "pyatspi", fake_pyatspi):
        rtnval = agentmodule.PyAtspiAccessibilityAgent()
    return rtnval


def test_set_value_assigns_the_value_interface():
    """
        The value is written to the element's Value interface as a float.
    """
    agent = _create_agent()
    value_iface = FakeValueInterface()
    slider = FakeAccessible("Volume", "slider", value_iface=value_iface)

    agent.set_value(slider, 7)

    testbase.assert_equal(value_iface.currentValue, 7.0)
    testbase.assert_true(isinstance(value_iface.currentValue, float), "value converted to float")

    return


def test_set_value_raises_when_the_value_interface_is_missing():
    """
        An element without the Value interface is reported as an ``InteractionError``
        naming the element and value, instead of the call silently doing nothing.
    """
    agent = _create_agent()
    label = FakeAccessible("Title", "label")

    raised = None
    try:
        agent.set_value(label, 3.5)
    except InteractionError as xcpt:
        raised = xcpt

    testbase.assert_true(raised is not None, "InteractionError raised")
    message = str(raised)
    testbase.assert_true("Title" in message, "element name in the message")
    testbase.assert_true("label" in message, "element role in the message")
    testbase.assert_true("3.5" in message, "value in the message")
    testbase.assert_true(isinstance(raised.__cause__, NotImplementedError), "original error chained")

    return


def test_set_value_raises_when_the_assignment_fails():
    """
        A Value interface that rejects the assignment is reported as an
        ``InteractionError`` chained to the original failure.
    """
    agent = _create_agent()
    failure = RuntimeError("value is read-only")
    slider = FakeAccessible("Progress", "progress bar", value_iface=FakeValueInterface(failure=failure))

    raised = None
    try:
        agent.set_value(slider, 50)
    except InteractionError as xcpt:
        raised = xcpt

    testbase.assert_true(raised is not None, "InteractionError raised")
    testbase.assert_true(raised.__cause__ is failure, "original error chained")
    testbase.assert_true("value is read-only" in str(raised), "cause carried in the message")

    return
