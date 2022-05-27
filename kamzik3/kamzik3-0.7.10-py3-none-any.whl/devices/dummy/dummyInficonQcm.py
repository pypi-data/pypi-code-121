import random
import time
from threading import Thread
from time import sleep

import numpy
import pandas

from kamzik3.constants import *
from kamzik3.devices.deviceChannel import DeviceChannel
from kamzik3.devices.deviceSocket import DeviceSocket
from kamzik3.devices.dummy.deviceDummy import DeviceDummy
from kamzik3.snippets.snippetsDecorators import expose_method


class DummyInficonQcm(DeviceDummy):
    def __init__(self, device_id=None, config=None):
        self._materials = pandas.read_csv(
            "./resources/inficon_qcm_materials.txt", sep="\t", names=["Formula", "Name"]
        )
        self.materials = (
            self._materials["Formula"] + " - " + self._materials["Name"]
        ).to_list()
        DeviceDummy.__init__(self, device_id, config)

    def _init_attributes(self):
        DeviceSocket._init_attributes(self)
        self.create_attribute(ATTR_PRODUCT_TYPE, readonly=True)
        self.create_attribute(ATTR_SOFTWARE_VERSION, readonly=True)
        self.create_attribute(ATTR_FIRMWARE, readonly=True)
        self.create_attribute(ATTR_SENSORS_COUNT, default_value=8, readonly=True)
        self.create_attribute(
            ATTR_ACTIVE_PROCESS, default_value=1, default_type=int, readonly=True
        )

        for i in range(1, self.get_value(ATTR_SENSORS_COUNT) + 1):
            self.create_attribute(
                f"{ATTR_MATERIAL}_{i}",
                default_value=None,
                default_type=self.materials,
                group=GROUP_MATERIALS,
            )
            self.create_attribute(
                f"{ATTR_OUTPUT}_{i}", default_value=None, group=GROUP_OUTPUTS
            )
            self.create_attribute(
                f"{ATTR_PROCESS}_{i}", default_value=None, group=GROUP_PROCESSES
            )
            self.create_attribute(
                f"{ATTR_USER_MESSAGE}_{i}",
                default_value=None,
                group=GROUP_USER_MESSAGES,
            )

    @expose_method()
    def init_measurement(self):
        active_channel = self.get_value(ATTR_ACTIVE_PROCESS) - 1
        self.notify((active_channel, ATTR_LAYER_THICKNESS), 0)
        self.notify((active_channel, ATTR_SENSOR_THICKNESS), 0)

    @expose_method()
    def stop_measurement(self):
        pass

    def set_active_process(self, process):
        self.set_value(ATTR_ACTIVE_PROCESS, process)

    def notify_channels(self, attribute, value):
        for channel in range(self.get_value(ATTR_SENSORS_COUNT)):
            self.notify((channel, attribute), value)


class DummyInficonQcmSensorChannel(DeviceChannel):
    sensor_state = [
        "Good Crystal and active",
        "Failed Crystal and active",
        "Invalid Measurement on Crystal and active",
        "Good Crystal and inactive",
        "Failed Crystal and inactive",
        "Invalid Measurement on Crystal and inactive",
    ]
    sensor_type = ["Single", "XtalTwo", "XtalSix", "Xtal12", "Generic"]

    def __init__(self, device, channel, device_id=None, config=None):
        super().__init__(device, channel, device_id, config)
        self.handle_configuration()

    def handle_configuration(self):
        if self.configured:
            return

        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()
            self.configured = True
            self.start_polling()
            self.set_status(STATUS_CONFIGURED)
            Thread(target=self._sensor_simulation).start()
            self.logger.info(
                "Device configuration took {} sec.".format(time.time() - start_at)
            )

        self.connected = True
        _finish_configuration()

    def _init_attributes(self):
        DeviceChannel._init_attributes(self)
        self.create_attribute(ATTR_STATE, readonly=True)
        self.add_attribute(
            ATTR_MATERIAL,
            self.device.get_attribute(
                [GROUP_MATERIALS, f"{ATTR_MATERIAL}_{self.channel + 1}"]
            ),
        )
        self.create_attribute(ATTR_SENSOR_TYPE, default_type=self.sensor_type)
        self.create_attribute(ATTR_AUTO_Z, default_type=bool)
        self.create_attribute(
            ATTR_Z_RATIO, default_value=0, default_type=float, readonly=True, decimals=9
        )
        self.create_attribute(
            ATTR_FUNDAMENTAL_FREQUENCY,
            unit="Hz",
            default_value=0,
            default_type=numpy.double,
            readonly=True,
            decimals=9,
            factor=0.000873114913702011,
        )
        self.create_attribute(
            ATTR_AHARMONIC_FREQUENCY,
            unit="Hz",
            default_value=0,
            default_type=numpy.double,
            readonly=True,
            decimals=9,
            factor=0.000873114913702011,
        )
        self.create_attribute(
            ATTR_SENSOR_THICKNESS,
            unit="nm",
            default_value=0,
            default_type=float,
            readonly=True,
            decimals=9,
            factor=0.1,
        )
        self.create_attribute(
            ATTR_CRYSTAL_LIFE,
            unit="%",
            default_value=100,
            default_type=int,
            readonly=True,
        )
        self.create_attribute(
            ATTR_RAW_RATE,
            unit="nm/s",
            default_value=0,
            default_type=float,
            readonly=True,
            decimals=9,
            factor=0.1,
        )
        self.create_attribute(
            ATTR_SHUTTER_STROKES,
            default_value=0,
            default_type=int,
            readonly=True,
            save_change=True,
            min_value=0,
        )
        self.create_attribute(
            ATTR_SHUTTER_OPEN, default_value=False, default_type=bool, readonly=True
        )
        self.create_attribute(
            ATTR_LAYER_THICKNESS,
            unit="nm",
            default_value=0,
            default_type=float,
            readonly=True,
            decimals=9,
            factor=0.1,
        )

    def _sensor_simulation(self):
        while self.configured:
            factor = 1000 if self.get_value(ATTR_SHUTTER_OPEN) else 1
            lt = self.get_value(ATTR_LAYER_THICKNESS)
            st = self.get_value(ATTR_SENSOR_THICKNESS)
            self.set_value(
                ATTR_AHARMONIC_FREQUENCY, random.randint(10000, 100000) * factor
            )
            self.set_value(
                ATTR_FUNDAMENTAL_FREQUENCY, random.randint(10000, 100000) * factor
            )
            raw_rate = (random.randint(1, 1000) * 1e-9) * factor
            self.set_value(ATTR_RAW_RATE, raw_rate)
            if self.device.get_value(ATTR_ACTIVE_PROCESS) == self.channel + 1:
                self.set_value(ATTR_LAYER_THICKNESS, lt + raw_rate)
            self.set_value(ATTR_SENSOR_THICKNESS, st + raw_rate)
            self.set_value(ATTR_CRYSTAL_LIFE, 100 - (lt + raw_rate))
            sleep(0.1)

    def subject_update(self, key, value, subject):
        DeviceChannel.subject_update(self, key, value, subject)

        if self.connected and isinstance(key, tuple) and key[0] == self.channel:
            attribute = key[1]

            self.set_attribute(
                (ATTR_LATENCY, VALUE), self.device.get_value(ATTR_LATENCY)
            )
            self.set_value(attribute, value)

    @expose_method()
    def open_shutter(self):
        if not self.get_value(ATTR_SHUTTER_OPEN):
            self.set_value(
                ATTR_SHUTTER_STROKES, self.get_value(ATTR_SHUTTER_STROKES) + 1
            )
            self.set_value(ATTR_SHUTTER_OPEN, True)

    @expose_method()
    def close_shutter(self):
        if self.get_value(ATTR_SHUTTER_OPEN):
            self.set_value(
                ATTR_SHUTTER_STROKES, self.get_value(ATTR_SHUTTER_STROKES) + 1
            )
            self.set_value(ATTR_SHUTTER_OPEN, False)

    @expose_method()
    def measure_layer_thickness(self):
        self.device.set_active_process(self.channel + 1)

    @expose_method()
    def clear_shutter_strokes(self):
        self.set_value(ATTR_SHUTTER_STROKES, 0)
