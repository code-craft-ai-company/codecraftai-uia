
from typing import Any
from ccai.uia.factory import AutomationFactory

CONTROLLER_SINGLETON_INST = None

def UiaControllerSingleton() -> Any:
    
    global CONTROLLER_SINGLETON_INST
    if CONTROLLER_SINGLETON_INST is None:
        CONTROLLER_SINGLETON_INST = AutomationFactory.get_automation_engine()

    return CONTROLLER_SINGLETON_INST
