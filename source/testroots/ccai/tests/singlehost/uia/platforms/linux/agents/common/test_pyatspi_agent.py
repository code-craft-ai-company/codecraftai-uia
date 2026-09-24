"""
    Display-free tests for :meth:`PyAtspiAccessibilityAgent.set_value`.  The agent
    is built by :func:`create_pyatspi_agent`, which patches the agent module's
    ``pyatspi`` binding with a stand-in registry so the agent can be constructed on
    hosts without pyatspi, and the accessibles are small fakes of the pyatspi
    Value interface from :mod:`ccai.testshared.fakes.uia.fakepyatspi`.
"""

from ccai import testbase

from ccai.uia.exceptions import InteractionError

from ccai.testshared.fakes.uia.fakepyatspi import FakeAccessible, FakeValueInterface, create_pyatspi_agent


def test_set_value_assigns_the_value_interface():
    """
        The value is written to the element's Value interface as a float.
    """
    agent = create_pyatspi_agent()
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
    agent = create_pyatspi_agent()
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
    agent = create_pyatspi_agent()
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
