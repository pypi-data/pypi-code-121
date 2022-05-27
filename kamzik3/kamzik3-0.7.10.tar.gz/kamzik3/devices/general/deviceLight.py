import time

import numpy as np

from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.devices.device import Device
from kamzik3.snippets.snippetsDecorators import expose_method


class DeviceLight(Device):
    def __init__(self, device_id=None, config=None):
        super().__init__(device_id, config)
        self.connect()

    def _init_attributes(self):
        super()._init_attributes()
        self.create_attribute(
            ATTR_INTENSITY,
            readonly=False,
            default_type=np.float16,
            min_value=0,
            max_value=100,
            unit="%",
            decimals=1,
            set_function=self.set_intensity,
            set_value_when_set_function=False,
        )
        self.create_attribute(
            ATTR_SETPOINT,
            default_value=75,
            readonly=False,
            default_type=np.float16,
            min_value=0,
            max_value=100,
            unit="%",
            decimals=1,
        )

    def handle_configuration(self):
        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()
            self.set_status(STATUS_CONFIGURED)
            self.logger.info(
                "Device configuration took {} sec.".format(time.time() - start_at)
            )

        _finish_configuration()

    def set_intensity(self, value, callback=None):
        raise NotImplementedError()

    @expose_method()
    # pylint: disable=unused-argument
    def turn_on(self, callback=None):
        self.logger.info("Turn On")
        self.set_intensity(self.get_value(ATTR_SETPOINT))

    @expose_method()
    # pylint: disable=unused-argument
    def turn_off(self, callback=None):
        self.logger.info("Turn Off")
        self.set_intensity(0)

    @expose_method()
    def stop(self):
        self.logger.info("Stop device")
        self.turn_off()


class DeviceLightAttribute(DeviceLight):
    def __init__(
        self,
        device,
        attribute,
        output_switch_attribute=None,
        device_id=None,
        config=None,
    ):
        self.device = device
        self.attribute = Attribute.list_attribute(attribute)
        self.output_switch_attribute = output_switch_attribute
        if output_switch_attribute is not None:
            self.output_switch_attribute = Attribute.list_attribute(
                output_switch_attribute
            )
        super().__init__(device_id, config)

    def connect(self, *args):
        super().connect(*args)
        self.device.attach_attribute_callback(
            self.attribute, self.value_changed, key_filter=VALUE
        )
        self.device.attach_attribute_callback(
            ATTR_STATUS, self.set_status, key_filter=VALUE
        )

    def _init_attributes(self):
        DeviceLight._init_attributes(self)
        if self.output_switch_attribute is not None:
            self.add_attribute(
                ATTR_OUTPUT_SWITCH,
                self.device.get_attribute(self.output_switch_attribute),
            )

    def value_changed(self, value):
        if value is None:
            return
        value_min, value_max = (
            self.device.get_attribute(self.attribute + [MIN]),
            self.device.get_attribute(self.attribute + [MAX]),
        )
        intensity = ((value - value_min) * 100) / (value_max - value_min)
        self.set_offsetted_value(ATTR_INTENSITY, intensity)

    def set_intensity(self, value, callback=None):
        self.logger.info("Set light intensity to {} %".format(value))
        if value > 0:
            self.set_value(ATTR_SETPOINT, value)
        value_min, value_max = (
            self.device.get_attribute(self.attribute + [MIN]),
            self.device.get_attribute(self.attribute + [MAX]),
        )
        attribute_value = (value * (value_max - value_min) / 100) + value_min
        self.device.set_attribute(self.attribute + [VALUE], attribute_value)

    @expose_method()
    def stop(self):
        self.device.stop()

    def close(self):
        self.device.detach_attribute_callback(self.attribute, self.value_changed)
        self.device.detach_attribute_callback(ATTR_STATUS, self.set_status)
        return super().close()

    @expose_method()
    def turn_on(self, callback=None):
        self.logger.info("Turn On")
        if self.output_switch_attribute is not None:
            self.device.set_value(self.output_switch_attribute, True)
        self.set_intensity(self.get_value(ATTR_SETPOINT))

    @expose_method()
    def turn_off(self, callback=None):
        self.logger.info("Turn Off")
        if self.output_switch_attribute is not None:
            self.device.set_value(self.output_switch_attribute, False)
        self.set_intensity(self.get_value(ATTR_SETPOINT))
