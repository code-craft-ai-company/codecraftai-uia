"""
    Display-free tests for :class:`LinuxElement`: weak agent references, keyboard
    delegation to the window-manager agent, search over a fake accessibility tree,
    the click fallback chain and value writes.  No AT-SPI or X11 is involved; the
    agents are the recording fakes from :mod:`ccai.testshared.fakes.uia.fakeelements`,
    or, for value writes, :class:`PyAtspiAccessibilityAgent` over the pyatspi
    stand-ins from :mod:`ccai.testshared.fakes.uia.fakepyatspi`.
"""

import gc
import types

from ccai import testbase

from ccai.uia.exceptions import InteractionError, PlatformNotSupportedError
from ccai.uia.platforms.linux.wrappers.uiaelement import LinuxElement

from ccai.testshared.fakes.uia.fakeelements import FakeAccessibilityAgent, FakeNativeNode, FakeWindowManagerAgent
from ccai.testshared.fakes.uia.fakepyatspi import FakeAccessible, FakeValueInterface, create_pyatspi_agent


def _build_window() -> FakeNativeNode:
    """
        A frame with a panel holding three buttons and a text display.
    """
    window = FakeNativeNode("Calculator", "frame")
    panel = window.add_child("", "panel")
    panel.add_child("OK", "push button", coordinates=(10, 20, 30, 40))
    panel.add_child("Cancel", "push button")
    panel.add_child("Calculate", "push button")
    panel.add_child("Display", "text", text="36")
    return window


def test_agents_are_held_weakly():
    """
        The element does not keep its agents alive; once they are collected the
        agent properties read as ``None``.
    """
    access = FakeAccessibilityAgent()
    wm = FakeWindowManagerAgent()
    element = LinuxElement(FakeNativeNode("x", "panel"), access, wm)

    testbase.assert_true(element.access_agent is access, "access agent resolves while alive")
    testbase.assert_true(element.wm_agent is wm, "wm agent resolves while alive")

    del access
    del wm
    gc.collect()

    testbase.assert_true(element.access_agent is None, "access agent released")
    testbase.assert_true(element.wm_agent is None, "wm agent released")

    return


def test_window_manager_agent_is_optional():
    """
        An element built without a window-manager agent reports ``None`` for it.
    """
    access = FakeAccessibilityAgent()
    element = LinuxElement(FakeNativeNode("x", "panel"), access, None)

    testbase.assert_true(element.wm_agent is None, "no wm agent")

    return


def test_agents_must_be_weak_referenceable():
    """
        Agents are held through ``weakref.ref``, so a ``types.SimpleNamespace`` fake
        is rejected at construction; test doubles for agents must be real classes.
    """
    raised = None
    try:
        LinuxElement(FakeNativeNode("x", "panel"), types.SimpleNamespace(), None)
    except TypeError as xcpt:
        raised = xcpt

    testbase.assert_true(raised is not None, "TypeError for a SimpleNamespace agent")

    return


def test_type_keys_requires_a_window_manager_agent():
    """
        Without a window-manager agent keyboard input is unsupported.
    """
    access = FakeAccessibilityAgent()
    element = LinuxElement(FakeNativeNode("x", "text"), access, None)

    raised = None
    try:
        element.type_keys("12")
    except PlatformNotSupportedError as xcpt:
        raised = xcpt

    testbase.assert_true(raised is not None, "PlatformNotSupportedError raised")

    return


def test_type_keys_delegates_to_the_window_manager_agent():
    """
        Keys are sent through the window-manager agent's ``send_keys``.
    """
    access = FakeAccessibilityAgent()
    wm = FakeWindowManagerAgent()
    element = LinuxElement(FakeNativeNode("x", "text"), access, wm)

    element.type_keys("12*3=")

    testbase.assert_equal(wm.sent, [(None, "12*3=")])

    return


def test_type_keys_wraps_agent_failures():
    """
        A failure inside the agent is reported as ``InteractionError`` carrying the
        original message.
    """
    access = FakeAccessibilityAgent()
    wm = FakeWindowManagerAgent(failure=RuntimeError("no keyboard"))
    element = LinuxElement(FakeNativeNode("x", "text"), access, wm)

    raised = None
    try:
        element.type_keys("1")
    except InteractionError as xcpt:
        raised = xcpt

    testbase.assert_true(raised is not None, "InteractionError raised")
    testbase.assert_true("no keyboard" in str(raised), "cause carried in the message")

    return


def test_name_text_and_role_come_from_the_access_agent():
    """
        The element's identity properties are read through the accessibility agent.
    """
    node = FakeNativeNode("Display", "text", text="36", states=["visible"])
    access = FakeAccessibilityAgent()
    element = LinuxElement(node, access, None)

    testbase.assert_equal(element.name, "Display")
    testbase.assert_equal(element.text, "36")
    testbase.assert_equal(element.role_name, "text")
    testbase.assert_true(element.is_visible, "visible state")
    testbase.assert_false(element.is_enabled, "no enabled state")

    return


def test_find_element_matches_name_grammar():
    """
        ``find_element`` honours ``~substring``, ``prefix*`` and ``*suffix`` names
        as well as exact names and roles, and returns ``None`` for no match.
    """
    access = FakeAccessibilityAgent()
    window = LinuxElement(_build_window(), access, None)

    testbase.assert_equal(window.find_element(name="~anc").name, "Cancel")
    testbase.assert_equal(window.find_element(name="Calc*").name, "Calculate")
    testbase.assert_equal(window.find_element(name="*OK").name, "OK")
    testbase.assert_equal(window.find_element(role="text").name, "Display")
    testbase.assert_equal(window.find_element(name="OK", role="push button").name, "OK")
    testbase.assert_true(window.find_element(name="OK", role="text") is None, "name and role must both match")
    testbase.assert_true(window.find_element(name="Nope") is None, "no match")

    return


def test_find_elements_recursive_and_shallow():
    """
        ``find_elements`` searches the whole subtree by default and only direct
        children when ``recursive`` is false.
    """
    access = FakeAccessibilityAgent()
    window = LinuxElement(_build_window(), access, None)

    deep = window.find_elements(role="push button")
    shallow = window.find_elements(role="push button", recursive=False)
    panels = window.find_elements(role="panel", recursive=False)

    testbase.assert_equal([button.name for button in deep], ["OK", "Cancel", "Calculate"])
    testbase.assert_equal(shallow, [])
    testbase.assert_equal(len(panels), 1)

    return


def test_click_uses_the_accessibility_action_first():
    """
        When the accessibility action succeeds the window manager is not involved.
    """
    access = FakeAccessibilityAgent()
    wm = FakeWindowManagerAgent()
    window = LinuxElement(_build_window(), access, wm)
    button = window.find_element(name="OK")

    button.click()

    testbase.assert_equal(len(access.actions), 1)
    testbase.assert_equal(access.actions[0][1], 0)
    testbase.assert_equal(wm.clicks, [])

    return


def test_click_falls_back_to_the_window_manager_at_the_centre():
    """
        When the accessibility action fails the element's centre is clicked through
        the window-manager agent.
    """
    access = FakeAccessibilityAgent()
    access.action_result = False
    wm = FakeWindowManagerAgent()
    window = LinuxElement(_build_window(), access, wm)
    button = window.find_element(name="OK")

    button.click()

    testbase.assert_equal(wm.clicks, [(25, 40)])

    return


def test_click_raises_when_no_action_and_no_coordinates():
    """
        With no working action and no coordinates to fall back on, the click is an
        ``InteractionError``.
    """
    access = FakeAccessibilityAgent()
    access.action_result = False
    wm = FakeWindowManagerAgent()
    window = LinuxElement(_build_window(), access, wm)
    button = window.find_element(name="Cancel")

    raised = None
    try:
        button.click()
    except InteractionError as xcpt:
        raised = xcpt

    testbase.assert_true(raised is not None, "InteractionError raised")

    return


def test_set_value_writes_through_the_accessibility_agent():
    """
        ``set_value`` writes the element's Value interface through the
        accessibility agent.
    """
    agent = create_pyatspi_agent()
    value_iface = FakeValueInterface()
    element = LinuxElement(FakeAccessible("Zoom", "slider", value_iface=value_iface), agent, None)

    element.set_value(125)

    testbase.assert_equal(value_iface.currentValue, 125.0)

    return


def test_set_value_raises_when_the_value_interface_is_missing():
    """
        An element without the Value interface raises the agent's
        ``InteractionError`` (naming the element and value, chained to the original
        error) instead of printing the failure and returning.
    """
    agent = create_pyatspi_agent()
    element = LinuxElement(FakeAccessible("Title", "label"), agent, None)

    raised = None
    try:
        element.set_value(3.5)
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
        A Value interface that rejects the assignment surfaces as an
        ``InteractionError`` chained to the original failure.
    """
    agent = create_pyatspi_agent()
    failure = RuntimeError("value is read-only")
    value_iface = FakeValueInterface(failure=failure)
    element = LinuxElement(FakeAccessible("Progress", "progress bar", value_iface=value_iface), agent, None)

    raised = None
    try:
        element.set_value(50)
    except InteractionError as xcpt:
        raised = xcpt

    testbase.assert_true(raised is not None, "InteractionError raised")
    testbase.assert_true(raised.__cause__ is failure, "original error chained")

    return
