from automojo import testbase

from automojo.testshared.factories.uia.uia_controller import create_uia_controller

testbase.originate.parameter(create_uia_controller, identifier="uia_controller")
