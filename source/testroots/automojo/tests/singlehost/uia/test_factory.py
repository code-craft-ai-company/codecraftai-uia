import platform

from automojo import testbase


def test_get_automation_engine():
    """
        Verifies the automation factory returns the MacOS engine on Darwin.
    """
    system = platform.system()
    if system != "Darwin":
        return

    from automojo.uia.factory import AutomationFactory
    from automojo.uia.platforms.macos.automation import MacOSAutomation

    engine = AutomationFactory.get_automation_engine()
    testbase.assert_equal(isinstance(engine, MacOSAutomation), True)

    return
