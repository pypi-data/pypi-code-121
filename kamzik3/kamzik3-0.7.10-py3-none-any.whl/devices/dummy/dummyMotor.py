import time
from threading import Thread
from time import sleep

import numpy as np

from kamzik3 import DeviceError
from kamzik3.constants import *
from kamzik3.devices.device import Device
from kamzik3.devices.deviceChannel import DeviceChannel
from kamzik3.devices.dummy.deviceDummy import DeviceDummy
from kamzik3.snippets.snippetsDecorators import expose_method


class DummyMotor(DeviceDummy):
    def __init__(self, channels=3, device_id=None, config=None):
        assert channels > 0
        self.channels = channels
        DeviceDummy.__init__(self, device_id, config)

    def _init_attributes(self):
        Device._init_attributes(self)
        self.create_attribute(
            ATTR_CHANNELS,
            default_value=self.channels,
            readonly=True,
            default_type=np.uint16,
            max_value=255,
        )


class DummyMotorChannel(DeviceChannel):
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
            self.logger.info(
                "Device configuration took {} sec.".format(time.time() - start_at)
            )

        self.connected = True
        _finish_configuration()

    def _init_attributes(self):
        DeviceChannel._init_attributes(self)
        self.create_attribute(
            ATTR_REFERENCED, default_value=True, readonly=True, default_type=np.bool
        )
        self.create_attribute(
            ATTR_POSITION,
            default_value=0,
            default_type=np.float,
            set_function=self._move_absolute,
            unit="nm",
            set_value_when_set_function=False,
            min_value=-1e9,
            max_value=1e9,
        )
        self.create_attribute(
            ATTR_POSITION_LOWER_LIMIT,
            default_value=-1e9,
            default_type=np.float,
            min_value=-1e9,
            max_value=1e9,
            unit="nm",
            set_function=self._set_lower_limit,
        )
        self.create_attribute(
            ATTR_POSITION_UPPER_LIMIT,
            default_value=1e9,
            default_type=np.float,
            min_value=-1e9,
            max_value=1e9,
            unit="nm",
            set_function=self._set_upper_limit,
        )
        self.create_attribute(
            ATTR_MAXIMUM_VELOCITY,
            default_value=1e5,
            default_type=np.uint64,
            min_value=10,
            max_value=1e6,
            unit="nm/sec",
            set_function=self._set_maximum_velocity,
        )
        self.create_attribute(
            ATTR_VELOCITY,
            default_value=0,
            default_type=np.float,
            min_value=-1e4,
            max_value=1e4,
            unit="nm/sec",
        )

    def subject_update(self, key, value, subject):
        DeviceChannel.subject_update(self, key, value, subject)

        if self.connected and isinstance(key, tuple) and key[0] == self.channel:
            attribute = key[1]

            self.set_attribute(
                (ATTR_LATENCY, VALUE), self.device.get_value(ATTR_LATENCY)
            )
            self.set_value(attribute, value)

    def _move_absolute(self, value, callback=None):
        if self.is_status(STATUS_BUSY):
            raise DeviceError("Motor is moving")

        def move_thread(setpoint):
            if value == self.get_value(ATTR_POSITION):
                return

            direction = 1
            if setpoint - self.get_raw_value(ATTR_POSITION) < 0:
                direction = -1

            self.set_raw_value(
                ATTR_VELOCITY, direction * self.get_raw_value(ATTR_MAXIMUM_VELOCITY)
            )
            self.set_status(STATUS_BUSY)
            counter = 0
            while (
                self.connected
                and self[ATTR_VELOCITY][VALUE] != 0
                and self.is_status(STATUS_BUSY)
            ):
                # Velocity in nm / 100ms
                counter += 1
                velocity = int(self.get_raw_value(ATTR_VELOCITY) / 10.0)
                new_position = int(self.get_raw_value(ATTR_POSITION) + velocity)
                if direction == 1:
                    if new_position < setpoint:
                        self.set_raw_value(ATTR_POSITION, new_position)
                    else:
                        self.set_raw_value(ATTR_POSITION, setpoint)
                        self.stop()
                else:
                    if new_position > setpoint:
                        self.set_raw_value(ATTR_POSITION, new_position)
                    else:
                        self.set_raw_value(ATTR_POSITION, setpoint)
                        self.stop()
                sleep(0.1)
            self.set_status(STATUS_IDLE)

        Thread(target=move_thread, args=[value]).start()
        if callback is not None:
            callback()

    def _set_upper_limit(self, value, callback=None):
        position_upper_limit = self[ATTR_POSITION].remove_offset_factor(value)
        self.set_raw_value(ATTR_POSITION, position_upper_limit, key=MAX)
        if callback is not None:
            callback()

    def _set_lower_limit(self, value, callback=None):
        position_lower_limit = self[ATTR_POSITION].remove_offset_factor(value)
        self.set_raw_value(ATTR_POSITION, position_lower_limit, key=MIN)
        if callback is not None:
            callback()

    def _set_maximum_velocity(self, velocity_upper_limit, callback=None):
        velocity_lower_limit = -velocity_upper_limit
        self.set_raw_value(ATTR_VELOCITY, velocity_lower_limit, key=MIN)
        self.set_raw_value(ATTR_VELOCITY, velocity_upper_limit, key=MAX)

        if self.get_raw_value(ATTR_VELOCITY) > velocity_upper_limit:
            self.get_raw_value(ATTR_VELOCITY, velocity_upper_limit)
        elif self.get_raw_value(ATTR_VELOCITY) < velocity_lower_limit:
            self.get_raw_value(ATTR_VELOCITY, velocity_lower_limit)
        if callback is not None:
            callback()

    @expose_method()
    def find_reference(self, callback=None):
        if self.is_status(STATUS_BUSY):
            raise DeviceError("Motor is moving")

        self.logger.info("Find reference")
        self._set((ATTR_POSITION, VALUE), 0)
        if callback is not None:
            callback()

    @expose_method()
    def stop(self, callback=None):
        self._set([ATTR_VELOCITY, VALUE], 0)
        if callback is not None:
            callback()

    def disconnect(self):
        self.stop()
        super().disconnect()
