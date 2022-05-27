import random
import time
from threading import Thread
from time import sleep

import numpy as np

from kamzik3.constants import *
from kamzik3.devices.dummy.deviceDummy import DeviceDummy

ATTR_CHAMELEON = "Chameleon"
ATTR_RANDOM_VALUE = "Random value"
ATTR_CHAMELEON_UNIT = "Chameleon unit"
ATTR_GROUP_ATTRIBUTE = "Group attribute"
ATTR_SHARED_ATTRIBUTE = "Shared attribute"
ATTR_SHARED_VALUE = "Shared value"
GROUP_TEST_GROUP = "Test group"


class DummyFeatureTestDevice(DeviceDummy):
    def _init_attributes(self):
        DeviceDummy._init_attributes(self)
        a = self.create_attribute(
            ATTR_CHAMELEON, default_value=0, default_type=np.float, decimals=3, unit=""
        )
        self.create_attribute(
            ATTR_CHAMELEON_UNIT,
            GROUP_TEST_GROUP,
            default_value="",
            set_function=self.set_chameleon_unit,
            save_change=True,
        )
        r = self.create_attribute(
            ATTR_RANDOM_VALUE,
            default_value=0,
            readonly=True,
            default_type=np.float,
            decimals=3,
            unit="",
            min_value=50,
            max_value=950,
        )
        self.create_attribute(
            ATTR_GROUP_ATTRIBUTE,
            GROUP_TEST_GROUP,
            default_value=0,
            default_type=np.float,
            decimals=3,
            unit="",
        )
        self.add_attribute(ATTR_SHARED_ATTRIBUTE, r)
        self.add_attribute(ATTR_SHARED_VALUE, a)

    def handle_configuration(self):
        start_at = time.time()
        self._config_commands()
        self._config_attributes()
        Thread(target=self.random_value_generator).start()
        self.set_status(STATUS_CONFIGURED)
        self.logger.info(
            "Device configuration took {} sec.".format(time.time() - start_at)
        )

    def set_chameleon_unit(self, value):
        self.set_attribute([ATTR_CHAMELEON, UNIT], value)
        self.set_attribute([ATTR_RANDOM_VALUE, UNIT], value)
        self.set_attribute([GROUP_TEST_GROUP, ATTR_GROUP_ATTRIBUTE, UNIT], value)

    def random_value_generator(self):
        while self.connected:
            value = random.uniform(0, 1e3)
            self.set_attribute([ATTR_RANDOM_VALUE, VALUE], value)
            sleep(0.2)
