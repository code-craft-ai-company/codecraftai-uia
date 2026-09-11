"""
    Tests for the abstract object model in :mod:`ccai.uia.platforms.base`: the
    ``UIElement`` contract, weak parent references, the polling helpers driven by
    a fake clock, and ``UIApplication.resolve_to_hint``.
"""

import gc
import time
import types

from typing import List, Optional
from unittest.mock import patch

from ccai import testbase

from ccai.uia.exceptions import ElementNotFoundError
from ccai.uia.model.declarative import DialogHint, WindowHint
from ccai.uia.platforms.base import UIElement

from ccai.testshared.fakes.uia.fakeclock import FakeClock
from ccai.testshared.fakes.uia.fakeelements import FakeApplication, FakeElement


class _AppearingElement(FakeElement):
    """
        A parent whose children only become findable after a number of searches,
        to model an element that is still being built.
    """

    def __init__(self, name: str, role: str, parent: Optional[UIElement] = None, appear_after: int = 0):
        super().__init__(name, role, parent=parent)
        self._searches_until_visible = appear_after
        self.searches = 0
        return

    def find_elements(self, **kwargs) -> List[UIElement]:
        self.searches = self.searches + 1
        rtnval = []
        if self.searches > self._searches_until_visible:
            rtnval = super().find_elements(**kwargs)
        return rtnval


def test_uielement_is_abstract():
    """
        ``UIElement`` cannot be instantiated directly.
    """
    raised = None
    try:
        UIElement()
    except TypeError as xcpt:
        raised = xcpt

    testbase.assert_true(raised is not None, "TypeError for abstract instantiation")

    return


def test_partial_implementation_cannot_be_instantiated():
    """
        A subclass that leaves any abstract member unimplemented is rejected, and
        the error names the missing member.
    """

    class MissingClick(UIElement):

        @property
        def name(self) -> str:
            return "x"

        @property
        def is_enabled(self) -> bool:
            return True

        @property
        def bounds(self):
            return (0, 0, 0, 0)

        @property
        def position(self):
            return (0, 0)

        @property
        def size(self):
            return (0, 0)

        @property
        def is_visible(self) -> bool:
            return True

        def type_keys(self, keys: str) -> None:
            return

        def find_element(self, **kwargs) -> Optional[UIElement]:
            return None

        def find_elements(self, **kwargs) -> List[UIElement]:
            return []

        def __repr__(self) -> str:
            return "MissingClick"

    raised = None
    try:
        MissingClick()
    except TypeError as xcpt:
        raised = xcpt

    testbase.assert_true(raised is not None, "TypeError for partial implementation")
    testbase.assert_true("click" in str(raised), "the missing member is named")

    return


def test_concrete_element_defaults():
    """
        A complete implementation instantiates, exists by default, and has no parent
        unless one is given.
    """
    element = FakeElement("OK", "push button")

    testbase.assert_true(element.exists, "exists by default")
    testbase.assert_true(element.parent is None, "no parent")

    return


def test_parent_is_held_weakly():
    """
        An element's parent reference does not keep the parent alive; once the
        parent is collected, ``parent`` reads as ``None``.
    """
    parent = FakeElement("Root", "frame")
    child = FakeElement("OK", "push button", parent=parent)

    testbase.assert_true(child.parent is parent, "parent resolves while alive")

    del parent
    gc.collect()

    testbase.assert_true(child.parent is None, "parent released after collection")

    return


def test_screen_element_parent_is_held_weakly():
    """
        Screen-level objects such as applications hold their parent weakly too.
    """
    root = FakeElement("Desktop", "desktop")
    app = FakeApplication("calc", parent=root)

    testbase.assert_true(app.parent is root, "parent resolves while alive")

    del root
    gc.collect()

    testbase.assert_true(app.parent is None, "parent released after collection")

    return


def test_parent_must_be_weak_referenceable():
    """
        Because parents are held through ``weakref.ref``, an object that cannot be
        weakly referenced, such as ``types.SimpleNamespace``, is rejected at
        construction.  Fakes used with this model must therefore be real classes.
    """
    raised = None
    try:
        FakeElement("OK", "push button", parent=types.SimpleNamespace(name="root"))
    except TypeError as xcpt:
        raised = xcpt

    testbase.assert_true(raised is not None, "TypeError for a SimpleNamespace parent")

    return


def test_wait_for_element_returns_the_element_when_found():
    """
        An element that is already present is returned without sleeping.
    """
    clock = FakeClock()
    root = FakeElement("Root", "frame")
    button = root.add_child("OK", "push button")

    with patch.object(time, "time", clock.time), patch.object(time, "sleep", clock.sleep):
        found = root.wait_for_element(timeout=2.0, interval=0.5, name="OK")

    testbase.assert_true(found is button, "the child is returned")
    testbase.assert_equal(clock.sleeps, [])

    return


def test_wait_for_element_polls_until_the_element_appears():
    """
        Searches repeat at ``interval`` until the element shows up.
    """
    clock = FakeClock()
    root = _AppearingElement("Root", "frame", appear_after=3)
    button = root.add_child("OK", "push button")

    with patch.object(time, "time", clock.time), patch.object(time, "sleep", clock.sleep):
        found = root.wait_for_element(timeout=10.0, interval=0.5, name="OK")

    testbase.assert_true(found is button, "the child is returned once visible")
    testbase.assert_equal(clock.sleeps, [0.5, 0.5, 0.5])
    testbase.assert_equal(root.searches, 4)

    return


def test_wait_for_element_raises_after_timeout():
    """
        When the element never appears, ``ElementNotFoundError`` is raised after the
        deadline and the search criteria are in the message.
    """
    clock = FakeClock()
    root = FakeElement("Root", "frame")

    raised = None
    with patch.object(time, "time", clock.time), patch.object(time, "sleep", clock.sleep):
        try:
            root.wait_for_element(timeout=2.0, interval=0.5, name="Missing")
        except ElementNotFoundError as xcpt:
            raised = xcpt

    testbase.assert_true(raised is not None, "ElementNotFoundError raised")
    testbase.assert_true("Missing" in str(raised), "criteria in the message")
    testbase.assert_equal(clock.sleeps, [0.5, 0.5, 0.5, 0.5])

    return


def test_wait_for_element_ignores_elements_that_do_not_exist():
    """
        A match whose ``exists`` is false is not accepted; the wait keeps polling.
    """
    clock = FakeClock()
    root = FakeElement("Root", "frame")
    root.add_child("Ghost", "push button", exists=False)

    raised = None
    with patch.object(time, "time", clock.time), patch.object(time, "sleep", clock.sleep):
        try:
            root.wait_for_element(timeout=1.0, interval=0.5, name="Ghost")
        except ElementNotFoundError as xcpt:
            raised = xcpt

    testbase.assert_true(raised is not None, "a non-existent match is not returned")
    testbase.assert_equal(clock.sleeps, [0.5, 0.5])

    return


def test_wait_until_gone_returns_true_when_hidden_or_absent():
    """
        An element that is invisible, or no longer exists, is reported gone at once.
    """
    clock = FakeClock()
    hidden = FakeElement("Dialog", "dialog", visible=False)
    absent = FakeElement("Dialog", "dialog", exists=False)

    with patch.object(time, "time", clock.time), patch.object(time, "sleep", clock.sleep):
        hidden_gone = hidden.wait_until_gone(timeout=2.0, interval=0.5)
        absent_gone = absent.wait_until_gone(timeout=2.0, interval=0.5)

    testbase.assert_true(hidden_gone, "hidden element is gone")
    testbase.assert_true(absent_gone, "absent element is gone")
    testbase.assert_equal(clock.sleeps, [])

    return


def test_wait_until_gone_returns_false_on_timeout():
    """
        An element that stays visible makes ``wait_until_gone`` return ``False`` at
        the deadline instead of raising.
    """
    clock = FakeClock()
    dialog = FakeElement("Dialog", "dialog")

    with patch.object(time, "time", clock.time), patch.object(time, "sleep", clock.sleep):
        gone = dialog.wait_until_gone(timeout=2.0, interval=0.5)

    testbase.assert_false(gone, "still present at the deadline")
    testbase.assert_equal(clock.sleeps, [0.5, 0.5, 0.5, 0.5])

    return


def test_application_declarative_model_defaults_to_none_and_is_settable():
    """
        An application starts with no declarative model and accepts one.
    """
    app = FakeApplication("calc")

    class Model:
        pass

    testbase.assert_true(app.declarative_model is None, "no model by default")

    app.declarative_model = Model

    testbase.assert_true(app.declarative_model is Model, "model stored")

    return


def test_resolve_to_hint_finds_the_matching_window_or_dialog_hint():
    """
        ``resolve_to_hint`` scans the model for the ``WindowHint`` or ``DialogHint``
        that matches the given window.
    """
    app = FakeApplication("calc")

    class Model:
        MainWindow = WindowHint(role="frame", name="Calculator")
        AboutDialog = DialogHint(name="About")
        NotAHint = "ignored"

    app.declarative_model = Model

    main_hint = app.resolve_to_hint(FakeElement("Calculator", "frame"))
    about_hint = app.resolve_to_hint(FakeElement("About", "dialog"))
    unknown_hint = app.resolve_to_hint(FakeElement("Preferences", "frame"))

    testbase.assert_true(main_hint is Model.MainWindow, "main window hint")
    testbase.assert_true(about_hint is Model.AboutDialog, "about dialog hint")
    testbase.assert_true(unknown_hint is None, "no hint for an unknown window")

    return


def test_resolve_to_hint_without_model_or_window_returns_none():
    """
        With no model, or no window, there is nothing to resolve.
    """
    app = FakeApplication("calc")
    window = FakeElement("Calculator", "frame")

    testbase.assert_true(app.resolve_to_hint(window) is None, "no model")

    class Model:
        MainWindow = WindowHint(role="frame", name="Calculator")

    app.declarative_model = Model

    testbase.assert_true(app.resolve_to_hint(None) is None, "no window")

    return
