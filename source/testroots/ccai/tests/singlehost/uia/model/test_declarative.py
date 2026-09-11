"""
    Display-free tests for the declarative model in :mod:`ccai.uia.model.declarative`:
    hint resolution against fake element trees (search precedence, name and role
    matching, the path grammar) and ``DeclarativeApplication`` attach / launch
    polling against a fake engine and a fake clock.
"""

import shlex
import subprocess
import time

from typing import List, Optional
from unittest.mock import patch

from ccai import testbase
from ccai.testbase.properties import run_property, st

from ccai.uia.model.declarative import (
    ButtonHint, CheckBoxHint, ComboBoxHint, DeclarativeApplication, DialogHint, ElementHint,
    HyperlinkHint, MenuBarHint, MenuHint, MenuItemHint, ProgressBarHint, RadioButtonHint,
    SliderHint, TabHint, TableHint, TextHint, TreeHint, WindowHint,
)
from ccai.uia.platforms.base import (
    UIButton, UICheckBox, UIComboBox, UIDialog, UIHyperlink, UIMenu, UIMenuBar, UIMenuItem,
    UIProgressBar, UIRadioButton, UISlider, UITab, UITable, UIText, UITree, UIWindow,
)

from ccai.testshared.fakes.uia.fakeclock import FakeClock
from ccai.testshared.fakes.uia.fakeelements import (
    FakeApplication, FakeAutomationEngine, FakeBothStyleElement, FakeElement,
    FakeLinuxStyleElement, FakeMacStyleElement,
)


def _build_linux_tree() -> FakeLinuxStyleElement:
    """
        A window with a panel holding OK and Cancel buttons and a text field.
    """
    window = FakeLinuxStyleElement("Calculator", "frame")
    panel = window.add_child("", "panel")
    panel.add_child("OK", "push button")
    panel.add_child("Cancel", "push button")
    panel.add_child("Display", "text")
    return window


class _FakePopen:
    """
        Records the command lines ``DeclarativeApplication.launch_or_attach`` launches.
    """

    launched: List[List[str]] = []

    def __init__(self, argv: List[str], **kwargs):
        type(self).launched.append(list(argv))
        return


def test_resolve_uses_find_descendant_with_name_and_role():
    """
        On a Linux-style parent the hint asks ``find_descendant`` for its name and
        role and returns what it finds.
    """
    window = _build_linux_tree()
    hint = ButtonHint(name="OK")

    found = hint.resolve(window)

    testbase.assert_true(found is not None, "OK button resolved")
    testbase.assert_equal(found.name, "OK")
    testbase.assert_equal(found.role, "push button")
    testbase.assert_equal(window.descendant_queries, [("OK", "push button")])

    return


def test_resolve_returns_none_when_nothing_matches():
    """
        A hint with no matching descendant resolves to ``None`` rather than raising.
    """
    window = _build_linux_tree()
    hint = ButtonHint(name="Apply")

    found = hint.resolve(window)

    testbase.assert_true(found is None, "no Apply button")

    return


def test_resolve_uses_access_name_when_name_is_absent():
    """
        ``access_name`` is the search name when ``name`` is not given.
    """
    window = _build_linux_tree()
    hint = ElementHint(access_name="Cancel")

    found = hint.resolve(window)

    testbase.assert_equal(found.name, "Cancel")
    testbase.assert_equal(window.descendant_queries, [("Cancel", None)])

    return


def test_resolve_falls_back_to_title_search_filtered_by_role():
    """
        On a MacOS-style parent the hint searches by title, and when it also carries a
        role, only a title match with that role is accepted.
    """
    window = FakeMacStyleElement("Document", "AXWindow")
    window.add_child("", "AXStaticText", title="Save")
    window.add_child("", "AXButton", title="Save")
    hint = ElementHint(name="Save", role="AXButton")

    found = hint.resolve(window)

    testbase.assert_equal(found.role, "AXButton")
    testbase.assert_equal(window.title_queries, ["Save"])
    testbase.assert_equal(window.role_queries, [])

    return


def test_resolve_falls_back_to_role_search_without_a_name():
    """
        With only a role to go on, a MacOS-style parent is asked for the first
        element of that role.
    """
    window = FakeMacStyleElement("Document", "AXWindow")
    window.add_child("", "AXStaticText")
    sheet = window.add_child("", "AXSheet")
    hint = ElementHint(role="AXSheet")

    found = hint.resolve(window)

    testbase.assert_true(found is sheet, "sheet found by role")
    testbase.assert_equal(window.title_queries, [])
    testbase.assert_equal(window.role_queries, ["AXSheet"])

    return


def test_resolve_search_precedence():
    """
        ``find_descendant`` is consulted first; the title search runs only when it
        finds nothing, and the role search only when the title search also fails.
    """
    window = FakeBothStyleElement("Document", "AXWindow")
    window.add_child("save-button", "AXButton", title="Save")
    hint = ElementHint(name="Save", role="AXButton")

    found = hint.resolve(window)

    testbase.assert_equal(found.title, "Save")
    testbase.assert_equal(window.descendant_queries, [("Save", "AXButton")])
    testbase.assert_equal(window.title_queries, ["Save"])
    testbase.assert_equal(window.role_queries, [])

    return


def test_resolve_with_path_walks_the_tree_instead_of_searching():
    """
        A hint with a path resolves through the path grammar and never calls the
        parent's search helpers.
    """
    window = _build_linux_tree()
    hint = ElementHint(path="//{name:Cancel}")

    found = hint.resolve(window)

    testbase.assert_equal(found.name, "Cancel")
    testbase.assert_equal(window.descendant_queries, [])

    return


def test_matches_checks_role_and_name():
    """
        ``matches`` requires both the role and the name to agree, and rejects ``None``.
    """
    hint = WindowHint(role="frame", name="Calculator")

    testbase.assert_true(hint.matches(FakeElement("Calculator", "frame")), "role and name agree")
    testbase.assert_false(hint.matches(FakeElement("Calculator", "dialog")), "role differs")
    testbase.assert_false(hint.matches(FakeElement("About", "frame")), "name differs")
    testbase.assert_false(hint.matches(None), "None never matches")

    return


def test_matches_accepts_title_in_place_of_name():
    """
        An element whose title carries the name matches even when its name is empty.
    """
    hint = WindowHint(role="frame", name="Calculator")
    window = FakeElement("", "frame", title="Calculator")

    testbase.assert_true(hint.matches(window), "title stands in for name")

    return


def test_matches_checks_identifier():
    """
        An identifier on the hint must equal the element's identifier.
    """
    hint = WindowHint(role="frame", identifier="main")

    testbase.assert_true(hint.matches(FakeElement("Any", "frame", identifier="main")), "identifier agrees")
    testbase.assert_false(hint.matches(FakeElement("Any", "frame", identifier="other")), "identifier differs")

    return


def test_specialised_hints_carry_default_roles():
    """
        Each specialised hint fixes the element type and the accessibility role it
        searches for.
    """
    expectations = [
        (WindowHint(), UIWindow, "window"),
        (DialogHint(), UIDialog, "dialog"),
        (ButtonHint(), UIButton, "push button"),
        (TextHint(), UIText, "text"),
        (MenuBarHint(), UIMenuBar, "menu bar"),
        (MenuHint(), UIMenu, "menu"),
        (MenuItemHint(), UIMenuItem, "menu item"),
        (TableHint(), UITable, "table"),
        (CheckBoxHint(), UICheckBox, "check box"),
        (RadioButtonHint(), UIRadioButton, "radio button"),
        (ComboBoxHint(), UIComboBox, "combo box"),
        (HyperlinkHint(), UIHyperlink, "link"),
        (TabHint(), UITab, "page tab list"),
        (TreeHint(), UITree, "tree"),
        (ProgressBarHint(), UIProgressBar, "progress bar"),
        (SliderHint(), UISlider, "slider"),
    ]

    for hint, type_class, role in expectations:
        testbase.assert_equal(hint.type_class, type_class, type(hint).__name__)
        testbase.assert_equal(hint.role, role, type(hint).__name__)

    return


def test_parse_path_segments():
    """
        ``//`` yields a descendant step, ``/`` a child step, a leading ``.`` a self
        step, and ``*`` an unfiltered step.
    """
    hint = ElementHint()

    descendant_then_children = hint._parse_path("//{name:A}/{role:panel}//*")
    testbase.assert_equal(descendant_then_children, [
        ("descendant", {"name": "A"}),
        ("child", {"role": "panel"}),
        ("descendant", {}),
    ])

    single_child = hint._parse_path("/x")
    testbase.assert_equal(single_child, [("child", {"name": "x"})])

    self_then_child = hint._parse_path(".{role:frame}/y")
    testbase.assert_equal(self_then_child, [("self", {"role": "frame"}), ("child", {"name": "y"})])

    return


def test_parse_filters():
    """
        Braced filters split on commas into a property dictionary; ``*`` is no
        filter; a bare token filters on name.
    """
    hint = ElementHint()

    braced = hint._parse_filters("{name:Cal*, role:push button}")
    testbase.assert_equal(braced, {"name": "Cal*", "role": "push button"})

    wildcard = hint._parse_filters("*")
    testbase.assert_equal(wildcard, {})

    bare = hint._parse_filters("Bare")
    testbase.assert_equal(bare, {"name": "Bare"})

    return


def test_match_filters_prefers_role_name():
    """
        A ``role`` filter compares against ``role_name`` when the element has one,
        so the human-readable AT-SPI name wins over the enum.
    """

    class RoleNamedElement:

        def __init__(self):
            self.role = "ROLE_PUSH_BUTTON"
            self.role_name = "push button"
            return

    hint = ElementHint()
    element = RoleNamedElement()

    testbase.assert_true(hint._match_filters(element, {"role": "push button"}), "matches role_name")
    testbase.assert_false(hint._match_filters(element, {"role": "ROLE_PUSH_BUTTON"}), "enum name is not used")

    return


def test_match_filters_wildcards():
    """
        ``Calc*`` matches a prefix, ``*tor`` a suffix, ``~cul`` a substring, ``*``
        anything; a missing property never matches.
    """
    hint = ElementHint()
    element = FakeElement("Calculator", "frame")

    testbase.assert_true(hint._match_filters(element, {"name": "Calc*"}), "prefix")
    testbase.assert_true(hint._match_filters(element, {"name": "*tor"}), "suffix")
    testbase.assert_true(hint._match_filters(element, {"name": "~cul"}), "contains")
    testbase.assert_true(hint._match_filters(element, {"name": "*"}), "any")
    testbase.assert_false(hint._match_filters(element, {"name": "Xalc*"}), "wrong prefix")
    testbase.assert_false(hint._match_filters(element, {"name": "~zzz"}), "missing substring")
    testbase.assert_false(hint._match_filters(element, {"nonexistent": "x"}), "missing property")

    return


def test_match_filters_equality_for_plain_values():
    """
        For values without wildcard characters an equality filter matches exactly
        the elements whose property equals the value.
    """
    hint = ElementHint()
    alphabet = "abcXYZ019 "

    def check(name: str, value: str) -> None:
        element = FakeElement(name, "frame")
        matched = hint._match_filters(element, {"name": value})
        testbase.assert_equal(matched, name == value, "name={!r} value={!r}".format(name, value))
        return

    run_property(check, max_examples=60,
                 name=st.text(alphabet=alphabet, min_size=0, max_size=4),
                 value=st.text(alphabet=alphabet, min_size=0, max_size=4))

    return


def test_attach_injects_the_declarative_model():
    """
        Attaching looks the application up by ``APPLICATION_NAME`` and stamps the
        model class onto the runtime object it gets back.
    """
    app = FakeApplication("gnome-calculator")
    engine = FakeAutomationEngine([app])

    class Calculator(DeclarativeApplication):
        APPLICATION_NAME = "gnome-calculator"

    attached = Calculator.attach(engine)

    testbase.assert_true(attached is app, "the engine's application is returned")
    testbase.assert_true(attached.declarative_model is Calculator, "model injected")
    testbase.assert_equal(engine.lookups, ["gnome-calculator"])

    return


def test_attach_returns_none_when_not_running():
    """
        When the engine has no such application, attach yields ``None``.
    """
    engine = FakeAutomationEngine([None])

    class Calculator(DeclarativeApplication):
        APPLICATION_NAME = "gnome-calculator"

    attached = Calculator.attach(engine)

    testbase.assert_true(attached is None, "not running")

    return


def test_attach_without_application_name_returns_none():
    """
        A model with no ``APPLICATION_NAME`` cannot attach and does not consult
        the engine.
    """
    engine = FakeAutomationEngine([FakeApplication("anything")])

    class Nameless(DeclarativeApplication):
        pass

    attached = Nameless.attach(engine)

    testbase.assert_true(attached is None, "nothing to attach to")
    testbase.assert_equal(engine.lookups, [])

    return


def test_launch_or_attach_returns_running_application_without_launching():
    """
        A running application is attached directly; no process is started.
    """
    app = FakeApplication("gnome-calculator")
    engine = FakeAutomationEngine([app])
    clock = FakeClock()
    _FakePopen.launched = []

    class Calculator(DeclarativeApplication):
        APPLICATION_NAME = "gnome-calculator"
        APPLICATION_COMMAND = "gnome-calculator"

    with patch.object(subprocess, "Popen", _FakePopen), patch.object(time, "sleep", clock.sleep):
        attached = Calculator.launch_or_attach(engine)

    testbase.assert_true(attached is app, "attached to the running application")
    testbase.assert_equal(_FakePopen.launched, [])
    testbase.assert_equal(clock.sleeps, [])

    return


def test_launch_or_attach_returns_none_without_a_command():
    """
        With nothing running and no ``APPLICATION_COMMAND`` there is nothing to
        launch, so the result is ``None`` and nothing is started.
    """
    engine = FakeAutomationEngine([None])
    clock = FakeClock()
    _FakePopen.launched = []

    class Calculator(DeclarativeApplication):
        APPLICATION_NAME = "gnome-calculator"

    with patch.object(subprocess, "Popen", _FakePopen), patch.object(time, "sleep", clock.sleep):
        attached = Calculator.launch_or_attach(engine)

    testbase.assert_true(attached is None, "nothing to launch")
    testbase.assert_equal(_FakePopen.launched, [])
    testbase.assert_equal(clock.sleeps, [])

    return


def test_launch_or_attach_launches_and_polls_until_attached():
    """
        When the application is not running its command is launched and attach is
        retried once a second until it succeeds; the model is injected on success.
    """
    app = FakeApplication("gnome-calculator")
    engine = FakeAutomationEngine([None, None, None, app])
    clock = FakeClock()
    _FakePopen.launched = []

    class Calculator(DeclarativeApplication):
        APPLICATION_NAME = "gnome-calculator"
        APPLICATION_COMMAND = "gnome-calculator --mode basic"

    with patch.object(subprocess, "Popen", _FakePopen), patch.object(time, "sleep", clock.sleep):
        attached = Calculator.launch_or_attach(engine)

    testbase.assert_true(attached is app, "attached after polling")
    testbase.assert_true(attached.declarative_model is Calculator, "model injected")
    testbase.assert_equal(_FakePopen.launched, [shlex.split("gnome-calculator --mode basic")])
    testbase.assert_equal(clock.sleeps, [1, 1, 1])
    testbase.assert_equal(len(engine.lookups), 4)

    return


def test_launch_or_attach_gives_up_after_twenty_polls():
    """
        An application that never appears is polled twenty times, one second apart,
        and then reported as ``None``.
    """
    engine = FakeAutomationEngine([None])
    clock = FakeClock()
    _FakePopen.launched = []

    class Calculator(DeclarativeApplication):
        APPLICATION_NAME = "gnome-calculator"
        APPLICATION_COMMAND = "gnome-calculator"

    with patch.object(subprocess, "Popen", _FakePopen), patch.object(time, "sleep", clock.sleep):
        attached = Calculator.launch_or_attach(engine)

    testbase.assert_true(attached is None, "never attached")
    testbase.assert_equal(len(_FakePopen.launched), 1)
    testbase.assert_equal(clock.sleeps, [1] * 20)
    testbase.assert_equal(len(engine.lookups), 21)

    return
