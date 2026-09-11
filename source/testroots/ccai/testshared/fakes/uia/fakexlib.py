"""
    .. module:: fakexlib
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: A fake python-xlib surface for exercising the X11 window-manager agent without a display.

    The X11 agent only touches a handful of Xlib entry points: the ``X`` constants,
    ``XK.string_to_keysym``, ``display.Display`` with ``keysym_to_keycode`` /
    ``keycode_to_keysym`` / ``sync``, and ``xtest.fake_input``.  The fakes here model
    a small US keyboard layout so keymap construction, shift detection and the
    ``send_keys`` grammar produce deterministic, inspectable event streams on every
    platform, whether or not python-xlib is installed.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


import contextlib
import os

from typing import Dict, List, Optional, Tuple
from unittest.mock import patch

from ccai.uia.platforms.linux.agents.x11 import x11windowmanageragent as x11module

from ccai.testshared.fakes.uia.fakeclock import FakeClock


# Named keysyms use the real X11 values so a debugger session shows familiar numbers.
NAMED_KEYSYMS: Dict[str, int] = {
    "BackSpace": 0xff08,
    "Tab": 0xff09,
    "Return": 0xff0d,
    "Escape": 0xff1b,
    "Home": 0xff50,
    "Left": 0xff51,
    "Up": 0xff52,
    "Right": 0xff53,
    "Down": 0xff54,
    "Page_Up": 0xff55,
    "Page_Down": 0xff56,
    "End": 0xff57,
    "Print": 0xff61,
    "Insert": 0xff63,
    "Delete": 0xffff,
    "F1": 0xffbe,
    "F2": 0xffbf,
    "F3": 0xffc0,
    "F4": 0xffc1,
    "F5": 0xffc2,
    "F6": 0xffc3,
    "F7": 0xffc4,
    "F8": 0xffc5,
    "F9": 0xffc6,
    "F10": 0xffc7,
    "Shift_L": 0xffe1,
    "Control_L": 0xffe3,
    "Alt_L": 0xffe9,
    "space": 0x20,
    "exclam": 0x21,
    "quotedbl": 0x22,
    "numbersign": 0x23,
    "dollar": 0x24,
    "percent": 0x25,
    "ampersand": 0x26,
    "apostrophe": 0x27,
    "parenleft": 0x28,
    "parenright": 0x29,
    "asterisk": 0x2a,
    "plus": 0x2b,
    "comma": 0x2c,
    "minus": 0x2d,
    "period": 0x2e,
    "slash": 0x2f,
    "colon": 0x3a,
    "semicolon": 0x3b,
    "less": 0x3c,
    "equal": 0x3d,
    "greater": 0x3e,
    "question": 0x3f,
    "at": 0x40,
    "bracketleft": 0x5b,
    "backslash": 0x5c,
    "bracketright": 0x5d,
    "asciicircum": 0x5e,
    "underscore": 0x5f,
    "grave": 0x60,
    "braceleft": 0x7b,
    "bar": 0x7c,
    "braceright": 0x7d,
    "asciitilde": 0x7e,
}

# keycode -> (unshifted keysym name, shifted keysym name or None).  This is the
# core of a US layout.  F11 and F12 are deliberately absent so tests can show
# that unmappable keysyms are skipped rather than mapped to keycode 0.
US_LAYOUT: Dict[int, Tuple[str, Optional[str]]] = {
    9: ("Escape", None),
    10: ("1", "exclam"),
    11: ("2", "at"),
    12: ("3", "numbersign"),
    13: ("4", "dollar"),
    14: ("5", "percent"),
    15: ("6", "asciicircum"),
    16: ("7", "ampersand"),
    17: ("8", "asterisk"),
    18: ("9", "parenleft"),
    19: ("0", "parenright"),
    20: ("minus", "underscore"),
    21: ("equal", "plus"),
    22: ("BackSpace", None),
    23: ("Tab", None),
    24: ("q", "Q"),
    25: ("w", "W"),
    26: ("e", "E"),
    27: ("r", "R"),
    28: ("t", "T"),
    29: ("y", "Y"),
    30: ("u", "U"),
    31: ("i", "I"),
    32: ("o", "O"),
    33: ("p", "P"),
    34: ("bracketleft", "braceleft"),
    35: ("bracketright", "braceright"),
    36: ("Return", None),
    37: ("Control_L", None),
    38: ("a", "A"),
    39: ("s", "S"),
    40: ("d", "D"),
    41: ("f", "F"),
    42: ("g", "G"),
    43: ("h", "H"),
    44: ("j", "J"),
    45: ("k", "K"),
    46: ("l", "L"),
    47: ("semicolon", "colon"),
    48: ("apostrophe", "quotedbl"),
    49: ("grave", "asciitilde"),
    50: ("Shift_L", None),
    51: ("backslash", "bar"),
    52: ("z", "Z"),
    53: ("x", "X"),
    54: ("c", "C"),
    55: ("v", "V"),
    56: ("b", "B"),
    57: ("n", "N"),
    58: ("m", "M"),
    59: ("comma", "less"),
    60: ("period", "greater"),
    61: ("slash", "question"),
    64: ("Alt_L", None),
    65: ("space", None),
    67: ("F1", None),
    68: ("F2", None),
    69: ("F3", None),
    70: ("F4", None),
    71: ("F5", None),
    72: ("F6", None),
    73: ("F7", None),
    74: ("F8", None),
    75: ("F9", None),
    76: ("F10", None),
    107: ("Print", None),
    110: ("Home", None),
    111: ("Up", None),
    112: ("Page_Up", None),
    113: ("Left", None),
    114: ("Right", None),
    115: ("End", None),
    116: ("Down", None),
    117: ("Page_Down", None),
    118: ("Insert", None),
    119: ("Delete", None),
}


class FakeX:
    """
        The subset of ``Xlib.X`` constants the agent reads.
    """
    KeyPress = 2
    KeyRelease = 3
    ButtonPress = 4
    ButtonRelease = 5
    MotionNotify = 6
    ShiftMask = 1
    IsViewable = 2
    RevertToParent = 2
    CurrentTime = 0
    Above = 0
    AnyPropertyType = 0


class FakeXK:
    """
        A stand-in for ``Xlib.XK`` backed by the tables above.
    """

    @staticmethod
    def string_to_keysym(name: str) -> int:
        """
            Resolves a keysym name the way Xlib does: single characters map to their
            code point, known names to their keysym, and anything else to 0.

            :param name: The keysym name.

            :returns: The keysym, or 0 when the name is unknown.
        """
        rtnval = 0
        if len(name) == 1:
            rtnval = ord(name)
        elif name in NAMED_KEYSYMS:
            rtnval = NAMED_KEYSYMS[name]
        return rtnval


class FakeDisplay:
    """
        A stand-in for an ``Xlib.display.Display`` connection with a US keyboard.
    """

    def __init__(self, display_name: str):
        self.display_name = display_name
        self.sync_count = 0
        self.flush_count = 0
        self.keysym_to_keycode_calls = 0
        self._layout: Dict[int, Tuple[int, int]] = {}
        for keycode, (unshifted_name, shifted_name) in US_LAYOUT.items():
            unshifted = FakeXK.string_to_keysym(unshifted_name)
            shifted = 0
            if shifted_name is not None:
                shifted = FakeXK.string_to_keysym(shifted_name)
            self._layout[keycode] = (unshifted, shifted)
        return

    def keysym_to_keycode(self, keysym: int) -> int:
        """
            Finds the keycode that produces ``keysym``, unshifted matches first.

            :param keysym: The keysym to look up.

            :returns: The keycode, or 0 when no key produces the keysym.
        """
        self.keysym_to_keycode_calls = self.keysym_to_keycode_calls + 1

        rtnval = 0
        if keysym != 0:
            for keycode, (unshifted, _shifted) in self._layout.items():
                if unshifted == keysym:
                    rtnval = keycode
                    break
            if rtnval == 0:
                for keycode, (_unshifted, shifted) in self._layout.items():
                    if shifted == keysym:
                        rtnval = keycode
                        break
        return rtnval

    def keycode_to_keysym(self, keycode: int, index: int) -> int:
        """
            Returns the keysym in column ``index`` (0 unshifted, 1 shifted) for a keycode.

            :param keycode: The keycode.
            :param index: The modifier column.

            :returns: The keysym, or 0 when the column is empty.
        """
        rtnval = 0
        if keycode in self._layout:
            unshifted, shifted = self._layout[keycode]
            if index == 0:
                rtnval = unshifted
            elif index == 1:
                rtnval = shifted
        return rtnval

    def sync(self) -> None:
        """
            Counts the round-trips the agent asks for.
        """
        self.sync_count = self.sync_count + 1
        return

    def flush(self) -> None:
        """
            Counts the flushes the agent asks for.
        """
        self.flush_count = self.flush_count + 1
        return


class FakeDisplayModule:
    """
        A stand-in for the ``Xlib.display`` module.  ``Display`` records the
        connection string the agent chose and hands back a :class:`FakeDisplay`.
    """

    def __init__(self):
        self.requested: List[str] = []
        self.displays: List[FakeDisplay] = []
        return

    def Display(self, display_name: str) -> FakeDisplay:  # noqa: N802 - mirrors Xlib.display.Display
        """
            Opens a fake connection.

            :param display_name: The X display string the agent selected.

            :returns: The fake display.
        """
        self.requested.append(display_name)
        fake_display = FakeDisplay(display_name)
        self.displays.append(fake_display)
        return fake_display


class FakeXTest:
    """
        A stand-in for ``Xlib.ext.xtest`` that records every synthesized input event.

        Events are recorded as ``(kind, detail)`` tuples where ``kind`` is one of
        ``"KeyPress"``, ``"KeyRelease"``, ``"ButtonPress"``, ``"ButtonRelease"`` or
        ``"MotionNotify"`` and ``detail`` is the keycode, button, or ``(x, y)``.
    """

    EVENT_NAMES = {
        FakeX.KeyPress: "KeyPress",
        FakeX.KeyRelease: "KeyRelease",
        FakeX.ButtonPress: "ButtonPress",
        FakeX.ButtonRelease: "ButtonRelease",
        FakeX.MotionNotify: "MotionNotify",
    }

    def __init__(self):
        self.events: List[Tuple[str, object]] = []
        return

    def fake_input(self, display: FakeDisplay, event_type: int, detail: int = 0, x: Optional[int] = None,
                   y: Optional[int] = None) -> None:
        """
            Records a synthesized event instead of sending it to a server.

            :param display: The display the event is aimed at.
            :param event_type: The X event type constant.
            :param detail: The keycode or button number.
            :param x: The pointer x coordinate for motion events.
            :param y: The pointer y coordinate for motion events.
        """
        kind = self.EVENT_NAMES.get(event_type, str(event_type))
        if event_type == FakeX.MotionNotify:
            self.events.append((kind, (x, y)))
        else:
            self.events.append((kind, detail))
        return

    def key_events(self) -> List[Tuple[str, int]]:
        """
            Returns only the keyboard events, in order.
        """
        rtnval = []
        for kind, detail in self.events:
            if kind in ("KeyPress", "KeyRelease"):
                rtnval.append((kind, detail))
        return rtnval


class FakeXlibEnvironment:
    """
        Patches the X11 agent module's Xlib bindings with the fakes for the duration
        of a ``with`` block, so an :class:`X11WindowManagerAgent` can be constructed
        and driven without a display.

        The patches are applied with :func:`unittest.mock.patch.object` and
        ``create=True`` because on hosts without python-xlib the agent module's
        guarded import leaves the names undefined.
    """

    def __init__(self, environ: Optional[Dict[str, str]] = None):
        self.environ = environ
        self.x = FakeX
        self.xk = FakeXK
        self.display_module = FakeDisplayModule()
        self.xtest = FakeXTest()
        self.clock = FakeClock()
        self._stack: Optional[contextlib.ExitStack] = None
        return

    def __enter__(self) -> "FakeXlibEnvironment":
        stack = contextlib.ExitStack()
        stack.enter_context(patch.object(x11module, "X", self.x, create=True))
        stack.enter_context(patch.object(x11module, "XK", self.xk, create=True))
        stack.enter_context(patch.object(x11module, "display", self.display_module, create=True))
        stack.enter_context(patch.object(x11module, "xtest", self.xtest, create=True))
        stack.enter_context(patch.object(x11module, "time", self.clock))
        if self.environ is not None:
            stack.enter_context(patch.dict(os.environ, self.environ, clear=True))
        self._stack = stack
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        self._stack.close()
        self._stack = None
        return False

    def create_agent(self) -> x11module.X11WindowManagerAgent:
        """
            Constructs the real agent against the fake display.

            :returns: A connected :class:`X11WindowManagerAgent`.
        """
        rtnval = x11module.X11WindowManagerAgent()
        return rtnval

    def keycode_of(self, keysym_name: str) -> int:
        """
            Looks up the keycode for a keysym name in the fake layout.

            :param keysym_name: The keysym name, for example ``"Return"`` or ``"a"``.

            :returns: The keycode.
        """
        keysym = FakeXK.string_to_keysym(keysym_name)
        rtnval = FakeDisplay("lookup").keysym_to_keycode(keysym)
        return rtnval
