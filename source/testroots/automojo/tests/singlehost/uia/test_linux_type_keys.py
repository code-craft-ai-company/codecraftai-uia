import platform
import sys
import time
import types

from automojo import testbase


def test_linux_type_keys_generates_events():
    """
        Verifies Linux type_keys generates key press and release events.
    """
    if platform.system() != "Linux":
        return

    from automojo.uia.platforms.linux.wrappers import uiaelement

    class FakeRegistry:
        events = []

        @classmethod
        def generateKeyboardEvent(cls, device: int, keysym: str, event_type: int) -> None:
            cls.events.append((device, keysym, event_type))

    fake_pyatspi = types.SimpleNamespace(
        Registry=FakeRegistry,
        KEY_PRESS=1,
        KEY_RELEASE=2,
        KEY_SYM=3,
        KEY_PRESSRELEASE=4,
        KEY_STRING=5,
    )

    original_pyatspi = sys.modules.get("pyatspi")
    sys.modules["pyatspi"] = fake_pyatspi

    original_sleep = time.sleep
    time.sleep = lambda _: None

    try:
        element = uiaelement.LinuxElement(native_obj=types.SimpleNamespace(name="dummy"))
        element.type_keys("a ")
    finally:
        time.sleep = original_sleep
        if original_pyatspi is None:
            del sys.modules["pyatspi"]
        else:
            sys.modules["pyatspi"] = original_pyatspi

    expected = [
        (0, "a", fake_pyatspi.KEY_STRING),
        (0, " ", fake_pyatspi.KEY_STRING),
    ]

    testbase.assert_equal(FakeRegistry.events, expected)

    return
