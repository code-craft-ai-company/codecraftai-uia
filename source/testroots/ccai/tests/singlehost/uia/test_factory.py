import platform

from ccai import testbase
from ccai.errors.exceptions import SkipError


def test_get_automation_engine():
    """
        Verifies the automation factory returns the MacOS engine on Darwin.
    """
    system = platform.system()
    if system != "Darwin":
        raise SkipError("the MacOS tests need a Darwin host")

    from ccai.uia.factory import AutomationFactory
    from ccai.uia.platforms.macos.automation import MacOSAutomation

    engine = AutomationFactory.get_automation_engine()
    testbase.assert_equal(isinstance(engine, MacOSAutomation), True)

    return
