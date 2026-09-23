"""
    Display-free tests for :meth:`MonitorCommand._walk_element` on Linux elements.
    ``pyatspi`` is replaced in ``sys.modules`` by a stand-in whose
    ``listInterfaces`` answers from the fake node, and the tree is read through
    :class:`FakeAccessibilityAgent`.
"""

import sys
import types

from typing import List
from unittest.mock import patch

from ccai import testbase

from ccai.uia.cli.cmdtree.mapping.monitor import MonitorCommand
from ccai.uia.platforms.linux.wrappers.uiaelement import LinuxElement

from ccai.testshared.fakes.uia.fakeelements import FakeAccessibilityAgent, FakeNativeNode


INTERFACES_BY_NAME = {
    "Calculator": ["Accessible", "Component"],
    "OK": ["Accessible", "Action", "Component"],
}


def _list_interfaces(native: FakeNativeNode) -> List[str]:
    """
        Stands in for ``pyatspi.listInterfaces``.

        :param native: The fake accessible.

        :returns: The interface names configured for the node's name.
    """
    rtnval = list(INTERFACES_BY_NAME[native.name])
    return rtnval


def test_walk_element_records_pyatspi_interfaces():
    """
        The interface names reported by pyatspi are stored in the mapping of the
        element and of its children.
    """
    access = FakeAccessibilityAgent()
    window = FakeNativeNode("Calculator", "frame")
    window.add_child("OK", "push button")
    element = LinuxElement(window, access, None)
    fake_pyatspi = types.SimpleNamespace(listInterfaces=_list_interfaces)

    command = MonitorCommand()
    with patch.dict(sys.modules, {"pyatspi": fake_pyatspi}):
        data = command._walk_element(element)

    testbase.assert_equal(data["interfaces"], ["Accessible", "Component"])
    testbase.assert_equal(len(data["children"]), 1)
    child_data = data["children"][0]
    testbase.assert_equal(child_data["interfaces"], ["Accessible", "Action", "Component"])

    return
