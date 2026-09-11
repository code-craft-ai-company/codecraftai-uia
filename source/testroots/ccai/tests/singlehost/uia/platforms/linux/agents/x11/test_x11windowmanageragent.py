"""
    Display-free tests for :class:`X11WindowManagerAgent`: keymap construction,
    shift detection and the ``send_keys`` modifier grammar, all driven against
    the fake Xlib surface in :mod:`ccai.testshared.fakes.uia.fakexlib`.

    These run on Linux, macOS and Windows; python-xlib does not need to be
    installed because every Xlib name the agent uses is patched onto its module.
"""

import string

from ccai import testbase
from ccai.testbase.properties import run_property, st

from ccai.testshared.fakes.uia.fakexlib import FakeDisplayModule, FakeXlibEnvironment


X11_SESSION = {"DISPLAY": ":99", "XDG_SESSION_TYPE": "x11"}


def _press_release(keycode: int) -> list:
    """
        The event pair for an unshifted key.
    """
    rtnval = [("KeyPress", keycode), ("KeyRelease", keycode)]
    return rtnval


def _shifted_press_release(keycode: int, shift_keycode: int) -> list:
    """
        The event sequence for a key the agent must shift: shift is held only
        around the press, and the key is released afterwards.
    """
    rtnval = [
        ("KeyPress", shift_keycode),
        ("KeyPress", keycode),
        ("KeyRelease", shift_keycode),
        ("KeyRelease", keycode),
    ]
    return rtnval


def test_setup_keymap_maps_control_keys():
    """
        The keymap resolves named control keys and their escape-sequence aliases to
        the keycode of the matching keysym.
    """
    with FakeXlibEnvironment(environ=X11_SESSION) as env:
        agent = env.create_agent()
        agent._setup_keymap()

        return_keycode = env.keycode_of("Return")
        testbase.assert_equal(agent._keymap["enter"], return_keycode)
        testbase.assert_equal(agent._keymap["return"], return_keycode)
        testbase.assert_equal(agent._keymap["\n"], return_keycode)
        testbase.assert_equal(agent._keymap["\r"], return_keycode)
        testbase.assert_equal(agent._keymap["tab"], env.keycode_of("Tab"))
        testbase.assert_equal(agent._keymap["\t"], env.keycode_of("Tab"))
        testbase.assert_equal(agent._keymap["esc"], env.keycode_of("Escape"))
        testbase.assert_equal(agent._keymap[" "], env.keycode_of("space"))
        testbase.assert_equal(agent._keymap["pageup"], env.keycode_of("Page_Up"))

    return


def test_setup_keymap_maps_symbols_to_their_keycodes():
    """
        Punctuation is mapped through the symbol table, so a shifted symbol lands
        on the keycode of the key that produces it.
    """
    with FakeXlibEnvironment(environ=X11_SESSION) as env:
        agent = env.create_agent()
        agent._setup_keymap()

        testbase.assert_equal(agent._keymap["*"], env.keycode_of("8"))
        testbase.assert_equal(agent._keymap["+"], env.keycode_of("equal"))
        testbase.assert_equal(agent._keymap["="], env.keycode_of("equal"))
        testbase.assert_equal(agent._keymap["!"], env.keycode_of("1"))
        testbase.assert_equal(agent._keymap["{"], env.keycode_of("bracketleft"))
        testbase.assert_equal(agent._keymap["~"], env.keycode_of("grave"))

    return


def test_setup_keymap_maps_alphanumerics_and_shift_key():
    """
        Letters of both cases share a keycode, digits map to their row, and the
        left shift keycode is captured for shifted input.
    """
    with FakeXlibEnvironment(environ=X11_SESSION) as env:
        agent = env.create_agent()
        agent._setup_keymap()

        testbase.assert_equal(agent._keymap["a"], env.keycode_of("a"))
        testbase.assert_equal(agent._keymap["A"], env.keycode_of("a"))
        testbase.assert_equal(agent._keymap["z"], env.keycode_of("z"))
        testbase.assert_equal(agent._keymap["8"], env.keycode_of("8"))
        testbase.assert_equal(agent._keymap["0"], env.keycode_of("0"))
        testbase.assert_equal(agent._shift_keycode, env.keycode_of("Shift_L"))

        for char in string.ascii_letters + string.digits:
            testbase.assert_true(char in agent._keymap, "keymap entry for {!r}".format(char))

    return


def test_setup_keymap_skips_keysyms_without_a_keycode():
    """
        A keysym the display cannot produce is left out of the keymap rather than
        mapped to keycode 0, so later lookups fall through cleanly.
    """
    with FakeXlibEnvironment(environ=X11_SESSION) as env:
        agent = env.create_agent()
        agent._setup_keymap()

        testbase.assert_true("f10" in agent._keymap, "f10 is on the fake keyboard")
        testbase.assert_false("f11" in agent._keymap, "f11 is not on the fake keyboard")
        testbase.assert_false("f12" in agent._keymap, "f12 is not on the fake keyboard")
        testbase.assert_false(0 in agent._keymap.values(), "keycode 0 never appears")

    return


def test_setup_keymap_runs_once():
    """
        The keymap is built on first use and reused afterwards; a second call does
        not query the display again.
    """
    with FakeXlibEnvironment(environ=X11_SESSION) as env:
        agent = env.create_agent()
        fake_display = env.display_module.displays[0]

        agent._setup_keymap()
        calls_after_first = fake_display.keysym_to_keycode_calls
        testbase.assert_greater(calls_after_first, 0)

        agent._setup_keymap()
        calls_after_second = fake_display.keysym_to_keycode_calls
        testbase.assert_equal(calls_after_second, calls_after_first)

    return


def test_needs_shift_for_upper_case_letters():
    """
        Upper-case letters live in the shifted column of their keycode; lower-case
        letters do not.
    """
    with FakeXlibEnvironment(environ=X11_SESSION) as env:
        agent = env.create_agent()
        agent._setup_keymap()

        testbase.assert_true(agent._needs_shift("A"), "A needs shift")
        testbase.assert_true(agent._needs_shift("Q"), "Q needs shift")
        testbase.assert_false(agent._needs_shift("a"), "a does not need shift")
        testbase.assert_false(agent._needs_shift("q"), "q does not need shift")

    return


def test_needs_shift_for_shifted_symbols():
    """
        Symbols resolved through the symbol table are shifted when they sit in the
        shifted column, and not when they are the key's base symbol.
    """
    with FakeXlibEnvironment(environ=X11_SESSION) as env:
        agent = env.create_agent()
        agent._setup_keymap()

        testbase.assert_true(agent._needs_shift("*"), "* is shift+8")
        testbase.assert_true(agent._needs_shift("+"), "+ is shift+=")
        testbase.assert_true(agent._needs_shift("_"), "_ is shift+-")
        testbase.assert_true(agent._needs_shift("!"), "! is shift+1")
        testbase.assert_false(agent._needs_shift("8"), "8 is unshifted")
        testbase.assert_false(agent._needs_shift("="), "= is unshifted")
        testbase.assert_false(agent._needs_shift("-"), "- is unshifted")
        testbase.assert_false(agent._needs_shift(","), ", is unshifted")

    return


def test_needs_shift_is_false_for_control_and_unknown_keys():
    """
        Control keys have no character keysym and unknown characters have no
        keycode; neither asks for shift.
    """
    with FakeXlibEnvironment(environ=X11_SESSION) as env:
        agent = env.create_agent()
        agent._setup_keymap()

        testbase.assert_false(agent._needs_shift("enter"), "enter")
        testbase.assert_false(agent._needs_shift("\n"), "newline")
        testbase.assert_false(agent._needs_shift(" "), "space")
        testbase.assert_false(agent._needs_shift("é"), "unmapped character")

    return


def test_keydown_wraps_shifted_key_in_shift_press_and_release():
    """
        ``keydown`` with ``needs_shift`` presses shift, presses the key and releases
        shift; ``keyup`` releases only the key.
    """
    with FakeXlibEnvironment(environ=X11_SESSION) as env:
        agent = env.create_agent()
        agent._setup_keymap()
        keycode_a = env.keycode_of("a")
        shift = env.keycode_of("Shift_L")

        agent.keydown(keycode_a, True)
        agent.keyup(keycode_a)

        expected = _shifted_press_release(keycode_a, shift)
        testbase.assert_equal(env.xtest.key_events(), expected)

    return


def test_keypress_emits_press_then_release():
    """
        A plain character produces exactly one press and one release of its keycode.
    """
    with FakeXlibEnvironment(environ=X11_SESSION) as env:
        agent = env.create_agent()

        agent.keypress("a")

        expected = _press_release(env.keycode_of("a"))
        testbase.assert_equal(env.xtest.key_events(), expected)

    return


def test_keypress_of_shifted_character_holds_shift_only_around_the_press():
    """
        A shifted character is typed with shift held for the press and released
        before the key itself is released.
    """
    with FakeXlibEnvironment(environ=X11_SESSION) as env:
        agent = env.create_agent()
        shift = env.keycode_of("Shift_L")

        agent.keypress("A")

        expected = _shifted_press_release(env.keycode_of("a"), shift)
        testbase.assert_equal(env.xtest.key_events(), expected)

    return


def test_keypress_ignores_unmappable_characters():
    """
        A character with no keycode on the display produces no events and no error.
    """
    with FakeXlibEnvironment(environ=X11_SESSION) as env:
        agent = env.create_agent()

        agent.keypress("é")

        testbase.assert_equal(env.xtest.key_events(), [])

    return


def test_send_keys_types_calculator_expression():
    """
        ``send_keys("12*3=")`` presses the digit keys unshifted and shifts only the
        asterisk: the exact stream the calculator test depends on.
    """
    with FakeXlibEnvironment(environ=X11_SESSION) as env:
        agent = env.create_agent()
        shift = env.keycode_of("Shift_L")

        agent.send_keys(None, "12*3=")

        expected = []
        expected.extend(_press_release(env.keycode_of("1")))
        expected.extend(_press_release(env.keycode_of("2")))
        expected.extend(_shifted_press_release(env.keycode_of("8"), shift))
        expected.extend(_press_release(env.keycode_of("3")))
        expected.extend(_press_release(env.keycode_of("equal")))
        testbase.assert_equal(env.xtest.key_events(), expected)

    return


def test_send_keys_alt_modifier_applies_to_next_character_only():
    """
        ``%`` holds Alt around the following character and releases it before the
        rest of the string is typed.
    """
    with FakeXlibEnvironment(environ=X11_SESSION) as env:
        agent = env.create_agent()
        alt = env.keycode_of("Alt_L")

        agent.send_keys(None, "%fa")

        expected = [("KeyPress", alt)]
        expected.extend(_press_release(env.keycode_of("f")))
        expected.append(("KeyRelease", alt))
        expected.extend(_press_release(env.keycode_of("a")))
        testbase.assert_equal(env.xtest.key_events(), expected)

    return


def test_send_keys_control_and_shift_modifiers():
    """
        ``^`` holds Control and ``+`` holds Shift around the next character.
    """
    with FakeXlibEnvironment(environ=X11_SESSION) as env:
        agent = env.create_agent()
        control = env.keycode_of("Control_L")
        shift = env.keycode_of("Shift_L")
        keycode_a = env.keycode_of("a")

        agent.send_keys(None, "^a+a")

        expected = [("KeyPress", control)]
        expected.extend(_press_release(keycode_a))
        expected.append(("KeyRelease", control))
        expected.append(("KeyPress", shift))
        expected.extend(_press_release(keycode_a))
        expected.append(("KeyRelease", shift))
        testbase.assert_equal(env.xtest.key_events(), expected)

    return


def test_send_keys_named_tokens():
    """
        ``{ENTER}``, ``{TAB}`` and ``{F1}`` type the named key.  The tokens are
        upper case in the documented grammar while the keymap registers them in
        lower case, so this is the case that used to produce no events at all.
    """
    with FakeXlibEnvironment(environ=X11_SESSION) as env:
        agent = env.create_agent()

        agent.send_keys(None, "{ENTER}{TAB}{F1}")

        expected = []
        expected.extend(_press_release(env.keycode_of("Return")))
        expected.extend(_press_release(env.keycode_of("Tab")))
        expected.extend(_press_release(env.keycode_of("F1")))
        testbase.assert_equal(env.xtest.key_events(), expected)

    return


def test_send_keys_braced_single_characters_are_literal():
    """
        ``{+}``, ``{%}`` and ``{^}`` type the modifier characters themselves and
        never press Alt or Control.
    """
    with FakeXlibEnvironment(environ=X11_SESSION) as env:
        agent = env.create_agent()
        shift = env.keycode_of("Shift_L")
        alt = env.keycode_of("Alt_L")
        control = env.keycode_of("Control_L")

        agent.send_keys(None, "{+}{%}{^}")

        expected = []
        expected.extend(_shifted_press_release(env.keycode_of("equal"), shift))
        expected.extend(_shifted_press_release(env.keycode_of("5"), shift))
        expected.extend(_shifted_press_release(env.keycode_of("6"), shift))
        testbase.assert_equal(env.xtest.key_events(), expected)

        pressed_keycodes = [detail for kind, detail in env.xtest.key_events()]
        testbase.assert_false(alt in pressed_keycodes, "Alt was never pressed")
        testbase.assert_false(control in pressed_keycodes, "Control was never pressed")

    return


def test_send_keys_unterminated_brace_is_literal():
    """
        A ``{`` with no closing brace is typed as a literal brace.
    """
    with FakeXlibEnvironment(environ=X11_SESSION) as env:
        agent = env.create_agent()
        shift = env.keycode_of("Shift_L")

        agent.send_keys(None, "{")

        expected = _shifted_press_release(env.keycode_of("bracketleft"), shift)
        testbase.assert_equal(env.xtest.key_events(), expected)

    return


def test_send_keys_trailing_modifier_is_typed_literally():
    """
        A modifier character with nothing after it has nothing to modify, so it is
        typed as the character itself.
    """
    with FakeXlibEnvironment(environ=X11_SESSION) as env:
        agent = env.create_agent()
        shift = env.keycode_of("Shift_L")
        alt = env.keycode_of("Alt_L")

        agent.send_keys(None, "%")

        expected = _shifted_press_release(env.keycode_of("5"), shift)
        testbase.assert_equal(env.xtest.key_events(), expected)

        pressed_keycodes = [detail for kind, detail in env.xtest.key_events()]
        testbase.assert_false(alt in pressed_keycodes, "Alt was never pressed")

    return


def test_send_keys_press_and_release_stay_balanced():
    """
        For any string of plain characters, every press is matched by a release,
        one press per character plus one shift press per shifted character, and no
        key is left held down.
    """
    alphabet = string.ascii_letters + string.digits + "*=-_.,!"

    def check(keys: str) -> None:
        with FakeXlibEnvironment(environ=X11_SESSION) as env:
            agent = env.create_agent()
            agent._setup_keymap()
            shift = env.keycode_of("Shift_L")

            agent.send_keys(None, keys)

            shifted_count = 0
            for char in keys:
                if agent._needs_shift(char):
                    shifted_count = shifted_count + 1

            presses = []
            releases = []
            held = []
            for kind, keycode in env.xtest.key_events():
                if kind == "KeyPress":
                    presses.append(keycode)
                    held.append(keycode)
                else:
                    releases.append(keycode)
                    testbase.assert_true(keycode in held, "release of a held key {}".format(keycode))
                    held.remove(keycode)

            testbase.assert_equal(len(held), 0, "nothing left held after {!r}".format(keys))
            testbase.assert_equal(sorted(presses), sorted(releases))
            testbase.assert_equal(presses.count(shift), shifted_count)
            testbase.assert_equal(len(presses) - shifted_count, len(keys))
        return

    run_property(check, max_examples=40, keys=st.text(alphabet=alphabet, min_size=0, max_size=12))

    return


def test_display_selection_uses_display_variable_on_x11():
    """
        On a plain X11 session the ``DISPLAY`` variable is authoritative.
    """
    with FakeXlibEnvironment(environ={"DISPLAY": ":99", "XDG_SESSION_TYPE": "x11"}) as env:
        env.create_agent()

        testbase.assert_equal(env.display_module.requested, [":99"])

    return


def test_display_selection_uses_xwayland_display_under_wayland():
    """
        Under Wayland the advertised ``DISPLAY`` is a stand-in; the agent connects
        to the XWayland display ``:0`` instead.
    """
    session = {"DISPLAY": ":1", "XDG_SESSION_TYPE": "wayland", "WAYLAND_DISPLAY": "wayland-0"}
    with FakeXlibEnvironment(environ=session) as env:
        env.create_agent()

        testbase.assert_equal(env.display_module.requested, [":0"])

    return


def test_display_selection_defaults_to_display_zero():
    """
        With no session variables at all the agent falls back to ``:0``.
    """
    with FakeXlibEnvironment(environ={}) as env:
        env.create_agent()

        testbase.assert_equal(env.display_module.requested, [":0"])

    return


def test_init_reports_connection_failure_as_import_error():
    """
        A display that cannot be opened surfaces as ``ImportError`` carrying the
        cause, which is what the automation factory keys its agent fallback on.
    """

    class RefusingDisplayModule(FakeDisplayModule):

        def Display(self, display_name: str):  # noqa: N802 - mirrors Xlib.display.Display
            raise ConnectionRefusedError("no server at {}".format(display_name))

    env = FakeXlibEnvironment(environ=X11_SESSION)
    env.display_module = RefusingDisplayModule()
    with env:
        raised = None
        try:
            env.create_agent()
        except ImportError as xcpt:
            raised = xcpt

        testbase.assert_true(raised is not None, "ImportError raised")
        testbase.assert_true("no server at :99" in str(raised), "cause is carried in the message")

    return
