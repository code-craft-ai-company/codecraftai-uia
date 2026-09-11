"""
    .. module:: fakeelements
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Fake UI element trees and agents for display-free tests of the UIA object model.

    Everything here is a plain class rather than :class:`types.SimpleNamespace`
    because the product holds parents and agents through weak references, and
    ``SimpleNamespace`` instances cannot be weakly referenced.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, List, Optional, Tuple

from ccai.uia.platforms.base import AutomationEngine, UIApplication, UIElement, UIWindow
from ccai.uia.platforms.linux.agents.linuxbaseagents import AccessibilityAgent, WindowManagerAgent


class FakeElement(UIElement):
    """
        A concrete :class:`UIElement` over an in-memory tree.

        ``find_elements`` returns the direct children, which is what the
        declarative path resolver walks.  ``click`` and ``type_keys`` record what
        was asked of the element.
    """

    def __init__(self, name: str, role: str, parent: Optional[UIElement] = None, title: Optional[str] = None,
                 identifier: Optional[str] = None, exists: bool = True, visible: bool = True):
        super().__init__(parent)
        self._name = name
        self._role = role
        self._title = title
        self._identifier = identifier
        self._exists = exists
        self._visible = visible
        self._children: List["FakeElement"] = []
        self.clicks = 0
        self.typed: List[str] = []
        return

    @property
    def name(self) -> str:
        return self._name

    @property
    def role(self) -> str:
        return self._role

    @property
    def title(self) -> Optional[str]:
        return self._title

    @property
    def identifier(self) -> Optional[str]:
        return self._identifier

    @property
    def exists(self) -> bool:
        return self._exists

    @property
    def is_visible(self) -> bool:
        return self._visible

    @property
    def is_enabled(self) -> bool:
        return True

    @property
    def bounds(self) -> Tuple[int, int, int, int]:
        return (0, 0, 10, 10)

    @property
    def position(self) -> Tuple[int, int]:
        return (0, 0)

    @property
    def size(self) -> Tuple[int, int]:
        return (10, 10)

    @property
    def children(self) -> List["FakeElement"]:
        return self._children

    def add_child(self, name: str, role: str, **kwargs) -> "FakeElement":
        """
            Creates a child of the same class under this element.

            :param name: The child's accessible name.
            :param role: The child's role string.

            :returns: The new child.
        """
        child = type(self)(name, role, parent=self, **kwargs)
        self._children.append(child)
        return child

    def descendants(self) -> List["FakeElement"]:
        """
            Returns every element below this one, depth first.
        """
        rtnval = []
        for child in self._children:
            rtnval.append(child)
            rtnval.extend(child.descendants())
        return rtnval

    def click(self) -> None:
        self.clicks = self.clicks + 1
        return

    def type_keys(self, keys: str) -> None:
        self.typed.append(keys)
        return

    def find_element(self, **kwargs) -> Optional[UIElement]:
        rtnval = None
        matches = self.find_elements(**kwargs)
        if len(matches) > 0:
            rtnval = matches[0]
        return rtnval

    def find_elements(self, **kwargs) -> List[UIElement]:
        name = kwargs.get("name")
        role = kwargs.get("role")
        rtnval = []
        for child in self._children:
            if name is not None and child.name != name:
                continue
            if role is not None and child.role != role:
                continue
            rtnval.append(child)
        return rtnval

    def __repr__(self) -> str:
        return "FakeElement<{}:{}>".format(self._role, self._name)


class FakeLinuxStyleElement(FakeElement):
    """
        A fake that exposes the Linux wrapper's ``find_descendant`` search, which
        :meth:`ElementHint.resolve` tries first.  Calls are recorded.
    """

    def __init__(self, name: str, role: str, parent: Optional[UIElement] = None, **kwargs):
        super().__init__(name, role, parent=parent, **kwargs)
        self.descendant_queries: List[Tuple[Optional[str], Optional[str]]] = []
        return

    def find_descendant(self, name: Optional[str] = None, role: Optional[str] = None,
                        max_depth: int = 10) -> Optional["FakeElement"]:
        self.descendant_queries.append((name, role))
        rtnval = None
        for candidate in self.descendants():
            if name is not None and candidate.name != name:
                continue
            if role is not None and candidate.role != role:
                continue
            rtnval = candidate
            break
        return rtnval


class FakeMacStyleElement(FakeElement):
    """
        A fake that exposes the MacOS wrapper's ``find_by_title`` and
        ``find_first_by_role`` searches, the fallbacks :meth:`ElementHint.resolve`
        uses when ``find_descendant`` is absent or finds nothing.  Calls are recorded.
    """

    def __init__(self, name: str, role: str, parent: Optional[UIElement] = None, **kwargs):
        super().__init__(name, role, parent=parent, **kwargs)
        self.title_queries: List[str] = []
        self.role_queries: List[str] = []
        return

    def find_by_title(self, title: str, include_self: bool = False, expression: bool = False) -> List["FakeElement"]:
        self.title_queries.append(title)
        rtnval = []
        for candidate in self.descendants():
            if candidate.title == title or candidate.name == title:
                rtnval.append(candidate)
        return rtnval

    def find_first_by_role(self, role: str, include_self: bool = False) -> Optional["FakeElement"]:
        self.role_queries.append(role)
        rtnval = None
        for candidate in self.descendants():
            if candidate.role == role:
                rtnval = candidate
                break
        return rtnval


class FakeBothStyleElement(FakeLinuxStyleElement, FakeMacStyleElement):
    """
        A fake exposing every search entry point, for tests of the precedence
        between them.
    """

    def __init__(self, name: str, role: str, parent: Optional[UIElement] = None, **kwargs):
        super().__init__(name, role, parent=parent, **kwargs)
        return


class FakeApplication(UIApplication):
    """
        A concrete :class:`UIApplication` that only needs a name.
    """

    def __init__(self, name: str, parent: Optional[UIElement] = None):
        super().__init__(parent)
        self._name = name
        self._windows: List[UIWindow] = []
        return

    @property
    def name(self) -> str:
        return self._name

    @property
    def identifier(self) -> str:
        return "fake.{}".format(self._name)

    @property
    def bounds(self) -> Tuple[int, int, int, int]:
        return (0, 0, 0, 0)

    @property
    def position(self) -> Tuple[int, int]:
        return (0, 0)

    @property
    def size(self) -> Tuple[int, int]:
        return (0, 0)

    @property
    def is_visible(self) -> bool:
        return True

    def bring_to_front(self) -> None:
        return

    def send_to_back(self) -> None:
        return

    def click(self) -> None:
        return

    def type_keys(self, keys: str) -> None:
        return

    def launch(self) -> None:
        return

    def terminate(self) -> None:
        return

    def activate(self) -> None:
        return

    def get_windows(self) -> List[UIWindow]:
        return self._windows

    def __repr__(self) -> str:
        return "FakeApplication<{}>".format(self._name)


class FakeAutomationEngine(AutomationEngine):
    """
        An engine whose ``get_application_by_name`` answers from a scripted list.

        Each lookup pops the next answer; once the script is exhausted the last
        answer repeats.  ``None`` answers model "not running yet".
    """

    def __init__(self, answers: List[Optional[UIApplication]]):
        self._answers = list(answers)
        self.lookups: List[str] = []
        return

    def get_application_by_name(self, application_name: str) -> Optional[UIApplication]:
        self.lookups.append(application_name)
        rtnval = None
        if len(self._answers) > 1:
            rtnval = self._answers.pop(0)
        elif len(self._answers) == 1:
            rtnval = self._answers[0]
        return rtnval


class FakeNativeNode:
    """
        A stand-in for an AT-SPI accessible, read only through :class:`FakeAccessibilityAgent`.
    """

    def __init__(self, name: str, role_name: str, text: str = "", states: Optional[List[str]] = None,
                 coordinates: Optional[Tuple[int, int, int, int]] = None):
        self.name = name
        self.role_name = role_name
        self.text = text
        self.states = states if states is not None else ["visible", "enabled"]
        self.coordinates = coordinates
        self.children: List["FakeNativeNode"] = []
        return

    def add_child(self, name: str, role_name: str, **kwargs) -> "FakeNativeNode":
        """
            Adds a child node.

            :param name: The child's name.
            :param role_name: The child's role name.

            :returns: The new child.
        """
        child = FakeNativeNode(name, role_name, **kwargs)
        self.children.append(child)
        return child


class FakeAccessibilityAgent(AccessibilityAgent):
    """
        An :class:`AccessibilityAgent` over :class:`FakeNativeNode` trees.
    """

    def __init__(self, root: Optional[FakeNativeNode] = None):
        self._root = root
        self.actions: List[Tuple[FakeNativeNode, int]] = []
        self.action_result = True
        return

    def get_root(self) -> Any:
        return self._root

    def get_application_by_name(self, name: str) -> Any:
        rtnval = None
        if self._root is not None:
            for child in self._root.children:
                if child.name == name:
                    rtnval = child
                    break
        return rtnval

    def get_role(self, element: FakeNativeNode) -> Any:
        return element.role_name

    def get_role_name(self, element: FakeNativeNode) -> str:
        return element.role_name

    def get_name(self, element: FakeNativeNode) -> str:
        return element.name

    def get_text(self, element: FakeNativeNode) -> str:
        return element.text

    def get_children(self, element: FakeNativeNode) -> List[Any]:
        return list(element.children)

    def get_states(self, element: FakeNativeNode) -> List[Any]:
        return list(element.states)

    def do_action(self, element: FakeNativeNode, action_index: int) -> bool:
        self.actions.append((element, action_index))
        return self.action_result

    def get_value(self, element: FakeNativeNode) -> float:
        return 0.0

    def set_value(self, element: FakeNativeNode, value: float) -> None:
        return

    def get_coordinates(self, element: FakeNativeNode) -> Optional[Tuple[int, int, int, int]]:
        return element.coordinates


class FakeWindowManagerAgent(WindowManagerAgent):
    """
        A :class:`WindowManagerAgent` that records keyboard and mouse requests.
        ``send_keys`` raises ``failure`` when one is configured.
    """

    def __init__(self, failure: Optional[Exception] = None):
        self.sent: List[Tuple[Any, str]] = []
        self.clicks: List[Tuple[int, int]] = []
        self.focused: List[str] = []
        self.failure = failure
        return

    def get_active_window(self) -> Any:
        return None

    def get_all_windows(self) -> List[Any]:
        return []

    def get_default_display(self) -> Any:
        return None

    def focus_window(self, window_name: str) -> bool:
        self.focused.append(window_name)
        return True

    def send_keys(self, window: Any, keys: str) -> None:
        if self.failure is not None:
            raise self.failure
        self.sent.append((window, keys))
        return

    def click(self, x: int, y: int) -> None:
        self.clicks.append((x, y))
        return

    def drag_and_drop(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5) -> None:
        return

    def move_mouse(self, x: int, y: int) -> None:
        return

    def get_displays(self) -> List[dict]:
        return []

    def get_desktops(self) -> List[dict]:
        return []
