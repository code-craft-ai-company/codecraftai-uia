"""
    Display-free tests for the declarative path grammar against elements that search the way the real platform
    wrappers do: ``find_elements()`` covers every descendant by default and only the immediate children when
    ``recursive=False`` is passed.  ``/`` must be a direct-child step and ``//`` must reach every descendant once.
"""
from typing import List

from ccai import testbase
from ccai.uia.model.declarative import ElementHint
from ccai.uia.platforms.base import UIElement
from ccai.testshared.fakes.uia.fakeelements import FakeElement


class PlatformStyleElement(FakeElement):
    """
        A fake whose ``find_elements`` searches recursively unless ``recursive=False`` is passed, like the Linux
        and macOS wrappers.
    """

    def find_elements(self, **kwargs) -> List[UIElement]:
        name = kwargs.get("name")
        role = kwargs.get("role")
        recursive = kwargs.get("recursive", True)
        candidates = self.descendants() if recursive else list(self.children)
        rtnval = []
        for candidate in candidates:
            if name is not None and candidate.name != name:
                continue
            if role is not None and candidate.role != role:
                continue
            rtnval.append(candidate)
        return rtnval


def _build_tree() -> PlatformStyleElement:
    """
        frame "Calculator"
          panel
            push button "OK"
            panel "Keypad"
              push button "Seven"
          push button "Close"
    """
    window = PlatformStyleElement("Calculator", "frame")
    panel = window.add_child("", "panel")
    panel.add_child("OK", "push button")
    keypad = panel.add_child("Keypad", "panel")
    keypad.add_child("Seven", "push button")
    window.add_child("Close", "push button")
    return window


def test_child_step_does_not_match_a_deeper_descendant():
    """
        A '/' step only looks at the immediate children, so a button two levels down is not found.
    """
    window = _build_tree()

    deep = ElementHint(path="/{name:OK}").resolve(window)
    testbase.assert_true(deep is None, "a child step must not reach the grandchild OK, found " + repr(deep))

    direct = ElementHint(path="/{name:Close}").resolve(window)
    testbase.assert_equal(direct.name, "Close")
    return


def test_leading_slash_is_the_same_as_no_prefix():
    """
        '/a/b' and 'a/b' are both child steps from the starting element.
    """
    window = _build_tree()

    with_slash = ElementHint(path="/{role:panel}/{name:OK}").resolve(window)
    without_slash = ElementHint(path="{role:panel}/{name:OK}").resolve(window)

    testbase.assert_equal(with_slash.name, "OK")
    testbase.assert_true(with_slash is without_slash, "both forms resolve to the same element")
    return


def test_descendant_step_reaches_any_depth():
    """
        A '//' step finds an element at any depth, and a child step after it is again limited to children.
    """
    window = _build_tree()

    seven = ElementHint(path="//{name:Seven}").resolve(window)
    testbase.assert_equal(seven.name, "Seven")

    keypad_child = ElementHint(path="//{name:Keypad}/{name:Seven}").resolve(window)
    testbase.assert_true(keypad_child is seven, "'//Keypad/Seven' resolves to the keypad's child")

    not_a_child = ElementHint(path="//{role:frame}/{name:Seven}").resolve(window)
    testbase.assert_true(not_a_child is None, "Seven is not a direct child of any frame")
    return


def test_descendant_walk_visits_each_element_once():
    """
        The '//' walk returns each matching descendant exactly once.
    """
    window = _build_tree()
    hint = ElementHint()

    buttons = hint._find_descendants_generic(window, {"role": "push button"})

    names = [button.name for button in buttons]
    testbase.assert_equal(sorted(names), ["Close", "OK", "Seven"])
    return
