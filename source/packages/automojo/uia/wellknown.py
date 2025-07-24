
from mojo.uia.uiacontroller import UiaController

CONTROLLER_SINGLETON_INST = None

def UiaControllerSingleton() -> UiaController:
    
    if CONTROLLER_SINGLETON_INST is None:
        CONTROLLER_SINGLETON_INST =  UiaController()

    return CONTROLLER_SINGLETON_INST
