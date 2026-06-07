import platform
from typing import Generator

from ccai import testbase


@testbase.register.resource_factory()
def create_uia_controller(constraints=None) -> Generator[object, None, None]:
    """
        Creates a UI automation controller for MacOS.

        :param constraints: Optional dictionary of constraints used while constructing the controller.

        :returns: A generator yielding the UI automation controller.
    """
    constraints = constraints or {}

    if platform.system() != "Darwin":
        yield None
        return

    from ccai.uia.factory import AutomationFactory

    controller = AutomationFactory.get_automation_engine()
    yield controller
