from ccai import testbase

from ccai.testshared.factories.uia.uia_controller import create_uia_controller

testbase.originate.parameter(create_uia_controller, identifier="uia_controller")
