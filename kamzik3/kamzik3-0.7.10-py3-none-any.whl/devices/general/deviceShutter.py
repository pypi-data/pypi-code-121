import time

import numpy as np

from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.devices.device import Device
from kamzik3.snippets.snippetsDecorators import expose_method
from kamzik3.snippets.snippetsTimer import CallbackTimer
from kamzik3.snippets.snippetsUnits import device_units


class DeviceShutter(Device):
    """
    General Shutter Device.
    To make use of it use this class as a parent class for any actual shutter.
    """

    def __init__(self, device_id=None, config=None):
        super().__init__(device_id, config)
        self.open_delay_timer = None
        self.close_delay_timer = None
        self.connect()

    def _init_attributes(self):
        """
        Attributes;
            ATTR_OPENED: Boolean flag showing open state of the Shutter
            ATTR_AUTO_MODE: Boolean switch, which enables Auto mode.
                            Auto mode is used by Macroserver to automatically operate the shutter.
            ATTR_OPEN_DELAY: Open delay in milliseconds
            ATTR_CLOSE_DELAY: Close delay in milliseconds
            ATTR_OPENED_AT: Showing to what percent shutter is Open
        """
        super()._init_attributes()
        self.create_attribute(
            ATTR_OPENED, default_value=False, readonly=True, default_type=np.bool
        )
        self.create_attribute(ATTR_AUTO_MODE, default_value=False, default_type=np.bool)
        self.create_attribute(
            ATTR_OPEN_DELAY,
            default_value=0,
            min_value=0,
            unit="ms",
            default_type=np.int32,
        )
        self.create_attribute(
            ATTR_CLOSE_DELAY,
            default_value=0,
            min_value=0,
            unit="ms",
            default_type=np.int32,
        )
        self.create_attribute(
            ATTR_OPENED_AT,
            default_value=0,
            readonly=True,
            default_type=np.float16,
            min_value=0,
            max_value=100,
            decimals=2,
            unit="%",
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

    def _open_shutter(self):
        """
        Privater method, which must be overloaded.
        Put code, which close the shutter based on Device specification here.
        """
        raise NotImplementedError()

    @expose_method()
    def open_shutter(self, clear_auto_mode=True):
        """
        This is general method which open the shutter.
        It's calling _open_shutter method either directly or as a callback when OPEN_DELAY is set.
        :param bool clear_auto_mode: Clear auto mode flag
        """
        self.clear_open_delay()
        self.set_value(ATTR_AUTO_MODE, not clear_auto_mode)

        open_delay = self.get_value(ATTR_OPEN_DELAY)
        if open_delay:
            self.set_status(STATUS_BUSY)
            self.open_delay_timer = CallbackTimer(open_delay, self._open_shutter)
            self.open_delay_timer.start()
        else:
            self._open_shutter()

    def _close_shutter(self):
        """
        Privater method, which must be overloaded.
        Put code, which open the shutter based on Device specification here.
        """
        raise NotImplementedError()

    @expose_method()
    def close_shutter(self, clear_auto_mode=True):
        """
        This is general method which close the shutter.
        It's calling _close_shutter method either directly or as a callback when CLOSE_DELAY is set.
        :param bool clear_auto_mode: Clear auto mode flag
        """
        self.clear_close_delay()
        self.set_value(ATTR_AUTO_MODE, not clear_auto_mode)

        close_delay = self.get_value(ATTR_CLOSE_DELAY)
        if close_delay:
            self.set_status(STATUS_BUSY)
            self.close_delay_timer = CallbackTimer(close_delay, self._close_shutter)
            self.close_delay_timer.start()
        else:
            self._close_shutter()

    def is_opened(self) -> bool:
        """
        Return True if Shutter is open, False otherwise.
        :return bool: Open state
        """
        raise NotImplementedError()

    def clear_open_delay(self):
        """
        Stop / clear open delay timer
        """
        if self.open_delay_timer is not None:
            self.open_delay_timer.stop()

    def clear_close_delay(self):
        """
        Stop / clear close delay timer
        """
        if self.close_delay_timer is not None:
            self.close_delay_timer.stop()

    @expose_method()
    def stop(self):
        self.clear_open_delay()
        self.clear_close_delay()
        self.set_status(STATUS_IDLE)

    def close(self) -> bool:
        self.clear_open_delay()
        self.clear_close_delay()
        return Device.close(self)


class DeviceShutterAttribute(DeviceShutter):
    """
    This is Shutter implemented by using Device and its Attribute.
    To use it, one must specify Device, Attribute and value for open and close state.
    Example of config file:

    Shutter_NI: &Shutter_NI !Device:kamzik3.devices.general.deviceShutter.DeviceShutterAttribute
        device: *NiCard
        device_id: Shutter
        attribute: [Digital outputs, port0/line0]
        opened_value: 1
        closed_value: 0
    """

    def __init__(
        self, device, attribute, opened_value, closed_value, device_id=None, config=None
    ):
        """
        :param Device device: Input device
        :param Union[list, tuple, str] attribute: Attribute to check
        :param mixed opened_value: value indicating open shutter
        :param mixed closed_value: value indicating close shutter
        :param str device_id: Device ID
        :param Union(dict, None) config: Device configuration
        """
        self.device = device
        self.attribute = Attribute.list_attribute(attribute)
        self.opened_value = opened_value
        self.closed_value = closed_value
        self.configured = False
        super().__init__(device_id, config)

    def _init_attributes(self):
        """
        Attributes;
            ATTR_OPENED_VALUE: Value indicating, that Shutter is Open
            ATTR_CLOSED_VALUE: Value indicating, that Shutter is Close
        """
        super()._init_attributes()
        self.create_attribute(
            ATTR_OPENED_VALUE, default_value=self.opened_value, default_type=np.float64
        )
        self.create_attribute(
            ATTR_CLOSED_VALUE, default_value=self.closed_value, default_type=np.float64
        )

    def connect(self, *args):
        self.device.attach_attribute_callback(
            ATTR_STATUS, self.set_status, key_filter=VALUE
        )

    def set_status(self, status):
        super().set_status(status)
        if status in READY_DEVICE_STATUSES and not self.configured:
            self.handle_configuration()

    def handle_configuration(self):
        """
        When configuring, set UNIT of the opened and closed value to unit of the Attribute.
        :return:
        """
        self.configured = True
        opened_value = device_units(self.device, self.attribute, self.opened_value)
        closed_value = device_units(self.device, self.attribute, self.closed_value)
        # noinspection PyStringFormat
        self.set_attribute([ATTR_OPENED_VALUE, UNIT], "{:~}".format(opened_value.u))  # type: ignore
        # noinspection PyStringFormat
        self.set_attribute([ATTR_CLOSED_VALUE, UNIT], "{:~}".format(closed_value.u))  # type: ignore
        self.device.attach_attribute_callback(
            self.attribute, self.shutter_value_changed, key_filter=VALUE
        )

    def shutter_value_changed(self, value):
        """
        Attribute callback, connected to the input Device Attribute.
        Callback is called when Value of the Attribute changed.
        :param mixed value: new value
        """
        self.set_value(ATTR_OPENED, self.is_opened(value))

    def _open_shutter(self):
        """
        Open shutter logic.
        By setting Status to IDLE, we are clearing delay BUSY status.
        """
        self.clear_open_delay()
        self.set_status(STATUS_IDLE)
        self.device.set_value(self.attribute, self.get_value(ATTR_OPENED_VALUE))

    def _close_shutter(self):
        """
        Close shutter logic.
        By setting Status to IDLE, we are clearing delay BUSY status.
        """
        self.clear_close_delay()
        self.set_status(STATUS_IDLE)
        self.device.set_value(self.attribute, self.get_value(ATTR_CLOSED_VALUE))

    # Note: I don't know if disabling arguments-differ is correct here. Might be a legitimate warning...
    # pylint: disable=arguments-differ
    def is_opened(self, current_value=None) -> bool:
        """
        Check if Shutter is open or close.
        :param mixed current_value: Current value of Device Attribute
        :return bool: Open state
        """
        opened_value = self.get_value(ATTR_OPENED_VALUE)
        if current_value is None:
            return False

        if self.device.get_attribute(self.attribute)[TYPE] == "bool":
            # Attribute is bool type
            opened = self.device.get_value(self.attribute) and opened_value
            self.set_value(ATTR_OPENED_AT, int(opened) * 100)
            return bool(self.device.get_value(self.attribute) and opened_value)

        current_value = self.device.get_value(self.attribute)
        tolerance = self.device.get_attribute(self.attribute + [TOLERANCE])

        try:
            self.set_value(
                ATTR_OPENED_AT, (float(current_value) / float(opened_value)) * 100
            )
        except ZeroDivisionError:
            self.set_value(ATTR_OPENED_AT, 100)
        return bool(
            (opened_value - tolerance[0])
            <= current_value
            <= (opened_value + tolerance[1])
        )

    @expose_method()
    def stop(self):
        DeviceShutter.stop(self)
        self.device.stop()

    def close(self) -> bool:
        """
        Close Device connection.
        """
        self.device.detach_attribute_callback(
            self.attribute, self.shutter_value_changed
        )
        return super().close()
