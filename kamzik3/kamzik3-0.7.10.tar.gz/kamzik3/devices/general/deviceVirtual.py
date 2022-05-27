import time
from threading import Thread

from kamzik3 import DeviceError, units
from kamzik3.constants import *
from kamzik3.devices.device import Device
from kamzik3.devices.observer import Observer
from kamzik3.macro.step import StepDeviceAttributeNumerical, StepParallel
from kamzik3.snippets.snippetsDecorators import expose_method


class DeviceVirtual(Device, Observer):

    configured = False

    def __init__(self, device_list, attribute_list, device_id=None, config=None):
        assert isinstance(device_list, list)
        assert isinstance(attribute_list, list)
        self.device_list = device_list
        self.attribute_list = attribute_list
        self.executed_step = None
        self.attached_callbacks = []
        super().__init__(device_id, config)
        for device in self.device_list:
            device.attach_attribute_callback(
                ATTR_STATUS, self.devices_status_update, key_filter=VALUE
            )

    # pylint: disable=unused-argument
    def devices_status_update(self, value):
        if self.configured:
            return
        for device in self.device_list:
            if not device.in_statuses(READY_DEVICE_STATUSES):
                return
        self.connect()

    def connect(self, *args):
        try:
            self.connecting = True
            self.connected = False
            self.device_connection_poller.add_connecting_device(self)
            for device in self.device_list:
                if not device.in_statuses(READY_DEVICE_STATUSES):
                    self.connection_error = True
                    return
            self.handle_connect_event()
        except DeviceError:
            self.logger.exception("Connection exception")
            return

    def handle_configuration(self):
        start_at = time.time()
        self.configured = True
        for device, attribute, _callback in self.attached_callbacks:
            device.detach_attribute_callback(ATTR_STATUS, self.devices_status_update)

        for device in self.device_list:
            device.attach_observer(self)

        for attribute in self.attribute_list:
            device_attribute = (
                self.device_list[0].get_attribute(attribute).attribute_copy()
            )
            device_attribute.set_value_when_set_function = True
            device_attribute.set_function = (
                lambda value, attr=attribute: self._set_attribute_value(attr, value)
            )
            self.add_attribute(attribute, device_attribute)

            def callback_fn(value, attr=attribute):
                self.attribute_changed(attr, value)

            self.device_list[0].attach_attribute_callback(
                attribute, callback_fn, key_filter=VALUE
            )
            self.attached_callbacks.append(
                (self.device_list[0], attribute, callback_fn)
            )

        self._config_commands()
        self._config_attributes()
        self.start_polling()
        self.set_status(STATUS_CONFIGURED)
        self.logger.info(
            "Device configuration took {} sec.".format(time.time() - start_at)
        )

    def _set_attribute_value(self, attribute, value, callback=None):
        try:
            self.set_absolute_value(attribute, value)
        except DeviceError as e:
            self.logger.exception(e)
            raise

    def set_absolute_value(self, attribute, value):
        value_delta = value - self.device_list[0].get_value(attribute)
        self.set_relative_value(
            attribute, units.Quantity(value_delta, self.get_attribute(attribute)[UNIT])
        )

    def set_relative_value(self, attribute, value):
        step_list = []
        for index, device in enumerate(self.device_list):
            device_attribute = device.get_attribute(attribute)
            device_absolute_value = device_attribute.value() + value
            if not device_attribute.within_limits(device_absolute_value):
                raise DeviceError(
                    "New position error. New value of {} {} is not within limits.".format(
                        device.device_id, attribute
                    )
                )
            step_list.append(
                StepDeviceAttributeNumerical(
                    index,
                    device.device_id,
                    attribute,
                    device_absolute_value,
                    positive_tolerance=device_attribute.positive_tolerance(),
                    negative_tolerance=device_attribute.negative_tolerance(),
                )
            )

        parallel_step = StepParallel("Set_Attribute_Step", step_list)
        Thread(target=self.execute_step, args=[parallel_step]).start()

    def execute_step(self, step):
        if self.executed_step is not None:
            step.error("Device is not ready")
        else:
            self.executed_step = step
            self.set_status(STATUS_BUSY)
            step.start()
            self.set_status(STATUS_IDLE)
        if step.get_state() == STATUS_ERROR:
            self.handle_command_error("Set attribute value", step.error_message)

        self.executed_step = None

    def subject_update(self, key, value, subject):
        # Don't update status when executing attribute change
        if self.executed_step is not None:
            return

        status_priorities = []
        for device in self.device_list:
            priority = STATUSES_PRIORITY.index(device[ATTR_STATUS][VALUE])
            status_priorities.append(priority)

        group_status = STATUSES_PRIORITY[min(status_priorities)]
        self.set_status(group_status)

    def attribute_changed(self, attribute, value):
        self.set_raw_value(attribute, value)

    @expose_method()
    def stop(self):
        if self.executed_step is not None:
            self.executed_step.stop()

    def disconnect(self):
        for device in self.device_list:
            device.detach_observer(self)
        for device, attribute, callback in self.attached_callbacks:
            device.detach_attribute_callback(attribute, callback)

        return super().disconnect()

    def close(self):
        self.set_status(STATUS_DISCONNECTED)
        if self.response_error or self.connection_error:
            self.connecting = False
            self.connected = False
            # self.reconnect()
