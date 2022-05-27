import logging
from threading import Event, Thread

import kamzik3
from kamzik3 import DeviceError, units, MacroException
from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.macro.common import Common


# TODO: Implement ramping of value step


class Step(Common):
    def __init__(
        self,
        common_id,
        repeat_count=0,
        wait_after=units.Quantity(0, "s"),
        retry_count=0,
        trigger_log=True,
        on_warning=ABORT,
        timeout=units.Quantity(0, "s"),
        scanner=None,
        scanner_attributes=None,
    ):
        self.steps_count = 1
        if not hasattr(self, "logger"):
            self.logger = logging.getLogger("Macro.Step.{}".format(common_id))
        super().__init__(
            common_id,
            repeat_count,
            wait_after,
            retry_count,
            trigger_log,
            on_warning,
            timeout,
            scanner=scanner,
            scanner_attributes=scanner_attributes,
        )

    def start(self):
        super().start()
        self.body()

        # Raise exception when step is in error state
        if self.get_state() == WARNING:
            if self.on_warning == ABORT or self.retry_count > 0:
                raise MacroException(self.warning_message)
            else:
                # Skipping here
                self.done()
                return

        # Raise exception when step is in error state
        if self.get_state() == ERROR:
            raise MacroException(self.error_message)
        if self.get_state() == STOPPED:
            return
        self.start_timer()
        if self.get_state() == STOPPED:
            return
        self.done()

    def repeat(self):
        super().repeat()
        self.body()
        # Raise exception when step is in error state
        if self.get_state() == WARNING:
            if self.on_warning == ABORT or self.retry_count > 0:
                raise MacroException(self.warning_message)
            else:
                return
        # Raise exception when step is in error state
        if self.get_state() == ERROR:
            raise MacroException(self.error_message)
        if self.get_state() == STOPPED:
            return
        self.start_timer()
        if self.get_state() == STOPPED:
            return
        self.done()

    def body(self):
        raise NotImplementedError()

    def get_total_steps_count(self):
        return self.steps_count

    def get_total_points_count(self):
        return self.points_count

    def get_output_header(self):
        # ~ is a pint format specification
        lines = [
            "Wait: {:~}".format(self.wait_after),  # type: ignore
            "Repeat count: {}".format(self.repeat_count),
            "Retry: {}".format(self.retry_count),
            "Trigger log: {}".format(self.trigger_log),
        ]
        return lines


class StepSetpoint(Step):
    def __init__(
        self,
        common_id,
        setpoint,
        repeat_count=0,
        wait_after=units.Quantity(0, "s"),
        retry_count=0,
        trigger_log=True,
        on_warning=ABORT,
        timeout=units.Quantity(0, "s"),
        scanner=None,
        scanner_attributes=None,
    ):
        self.setpoint = setpoint
        if not hasattr(self, "logger"):
            self.logger = logging.getLogger("Macro.Step.{}".format(common_id))
        super().__init__(
            common_id,
            repeat_count,
            wait_after,
            retry_count,
            trigger_log,
            on_warning,
            timeout,
            scanner=scanner,
            scanner_attributes=scanner_attributes,
        )

    def body(self):
        raise NotImplementedError()

    def check_value_on_setpoint(self, value):
        if value is None:
            return False
        return self.setpoint == value

    def get_output_header(self):
        lines = [
            "Setpoint: {}".format(self.setpoint),
        ]
        return lines + Step.get_output_header(self)


class StepDeviceAttribute(StepSetpoint):
    check_max_timeout = 2000
    check_timeout = 0
    device = None
    device_attribute = None

    def __init__(
        self,
        common_id,
        device_id,
        attribute,
        setpoint,
        repeat_count=0,
        wait_after=units.Quantity(0, "s"),
        retry_count=0,
        trigger_log=True,
        on_warning=ABORT,
        timeout=units.Quantity(0, "s"),
        scanner=None,
        scanner_attributes=None,
    ):
        self.device_id = device_id
        self.attribute = Attribute.list_attribute(attribute)
        self.device_status_idle_flag = False
        self.device_setpoint_reached_flag = False
        self.check_event = Event()
        # self.timeout_lock = Lock()  # Prevents race on setting check_timeout
        if not hasattr(self, "logger"):
            self.logger = logging.getLogger(
                "Macro.Step.{}.{}.{}".format(common_id, device_id, attribute)
            )
        super().__init__(
            common_id,
            setpoint,
            repeat_count,
            wait_after,
            retry_count,
            trigger_log,
            on_warning,
            timeout,
            scanner=scanner,
            scanner_attributes=scanner_attributes,
        )

    def body(self):
        self.check_timeout = 0
        try:
            self.logger.debug("Setting setpoint to {}".format(self.setpoint))
            self.device = kamzik3.session.get_device(self.device_id)
            self.device_attribute = self.device.get_attribute(self.attribute)

            if not self.device.in_statuses(READY_DEVICE_STATUSES):
                raise DeviceError("Device {} is not ready".format(self.device_id))
            # Attach callback for attribute and status changes
            self.device.attach_attribute_callback(
                self.attribute, self.check_attribute_set, key_filter=VALUE
            )
            self.device.attach_attribute_callback(
                ATTR_STATUS, self.check_device_status, key_filter=VALUE
            )
            # Set device's attribute to desired setpoint
            self.device.set_attribute(
                self.attribute + [VALUE], self.setpoint, callback=self.on_value_set
            )
            # Check if reached setpoint or timed out
            self.device_status_idle_flag = self.device.in_statuses(IDLE_DEVICE_STATUSES)
            self.device_setpoint_reached_flag = False

            while (
                self.get_state() == BUSY
                and self.check_timeout <= self.check_max_timeout
            ):
                self.check_event.wait(0.01)
                # To successfully finish step device has to be IDLE and attributes value within setpoints tolerance
                if self.device_status_idle_flag and self.device_setpoint_reached_flag:
                    # Set check event and break while loop
                    self.check_event.set()
                    break
                else:
                    self.check_timeout += 10
        except (DeviceError, AttributeError) as e:
            self.error(e)
        # Detach attribute and status callback
        self.device.detach_attribute_callback(self.attribute, self.check_attribute_set)
        self.device.detach_attribute_callback(ATTR_STATUS, self.check_device_status)

        # Raise exception if setpoint was not reached
        if self.get_state() != STOPPED and not self.check_event.isSet():
            description = "{}'s attribute setpoint {}: {} could not be reached.".format(
                self.device.device_id, self.attribute, self.setpoint
            )
            self.warning(description)

        # Remove device and attributes
        self.device = None
        self.device_attribute = None

    def get_output(self):
        return self.device.get_attribute(self.attribute).value()

    def check_attribute_set(self, value):
        # Check if value is within setpoint tolerants
        if self.check_value_on_setpoint(self.device_attribute.value()):
            self.device_setpoint_reached_flag = True
        else:
            self.device_setpoint_reached_flag = False
        # Reset check_timeout
        if not self.device_status_idle_flag:
            self.check_timeout = 0

    def check_device_status(self, value):
        # Check if device is idle
        if value in IDLE_DEVICE_STATUSES:
            self.device_status_idle_flag = True
        else:
            self.device_status_idle_flag = False
        # Reset check_timeout
        self.check_timeout = 0

    def on_value_set(self, key, value):
        # Check for error when setting setpoint
        if key == RESPONSE_ERROR:
            self.error(value)

    def reset(self):
        self.device_status_idle_flag = False
        self.device_setpoint_reached_flag = False
        self.check_event.clear()
        self.retry_count = self.max_retry_count
        super().reset()

    def get_output_header(self):
        lines = [
            "Device: {}".format(self.device_id),
            "Attribute: {}".format(self.attribute),
        ]

        return lines + StepSetpoint.get_output_header(self)

    def stop(self):
        if self.device is not None and self.get_state() == BUSY:
            self.device.stop()
        StepSetpoint.stop(self)

    def warning(self, warning_message):
        if self.device is not None and self.get_state() == BUSY:
            self.device.stop()
        StepSetpoint.warning(self)


class StepSetpointNumerical(Step):
    def __init__(
        self,
        common_id,
        setpoint,
        negative_tolerance=None,
        positive_tolerance=None,
        repeat_count=0,
        wait_after=units.Quantity(0, "s"),
        retry_count=0,
        trigger_log=True,
        on_warning=ABORT,
        timeout=units.Quantity(0, "s"),
        scanner=None,
        scanner_attributes=None,
    ):
        assert isinstance(setpoint, units.Quantity)

        self.setpoint = setpoint
        self.negative_tolerance = negative_tolerance
        if self.negative_tolerance is None:
            self.negative_tolerance = units.Quantity(0, self.setpoint.u)
        self.positive_tolerance = positive_tolerance
        if self.positive_tolerance is None:
            self.positive_tolerance = units.Quantity(0, self.setpoint.u)
        if not hasattr(self, "logger"):
            self.logger = logging.getLogger("Macro.Step.{}".format(common_id))
        super().__init__(
            common_id,
            repeat_count,
            wait_after,
            retry_count,
            trigger_log,
            on_warning,
            timeout,
            scanner=scanner,
            scanner_attributes=scanner_attributes,
        )

    def body(self):
        raise NotImplementedError()

    def get_output(self):
        return self.device.get_attribute(self.attribute).value()

    def check_value_on_setpoint(self, value):
        # Check value is within +/- setpoints tolerance
        assert isinstance(value, units.Quantity)

        if value is None:
            return False
        return (
            (self.setpoint - self.negative_tolerance)
            <= value
            <= (self.setpoint + self.positive_tolerance)
        )

    def get_output_header(self):
        # ~ is a pint format specification
        lines = [
            "Setpoint: {:~}".format(self.setpoint),  # type: ignore
            "Negative tolerance: {:~}".format(self.negative_tolerance),  # type: ignore
            "Positive tolerance: {:~}".format(self.positive_tolerance),  # type: ignore
        ]
        return lines + Step.get_output_header(self)


class StepDeviceAttributeNumerical(StepSetpointNumerical):
    check_max_timeout = 2000
    check_timeout = 0
    device = None
    device_attribute = None

    def __init__(
        self,
        common_id,
        device_id,
        attribute,
        setpoint,
        negative_tolerance=None,
        positive_tolerance=None,
        repeat_count=0,
        wait_after=units.Quantity(0, "s"),
        retry_count=0,
        trigger_log=True,
        on_warning=ABORT,
        timeout=units.Quantity(0, "s"),
        scanner=None,
        scanner_attributes=None,
    ):
        self.device_id = device_id
        self.attribute = Attribute.list_attribute(attribute)
        self.device_status_idle_flag = False
        self.device_setpoint_reached_flag = False
        self.check_event = Event()
        # self.timeout_lock = Lock()  # Prevents race on setting check_timeout
        if not hasattr(self, "logger"):
            self.logger = logging.getLogger(
                "Macro.Step.{}.{}.{}".format(common_id, device_id, attribute)
            )
        super().__init__(
            common_id,
            setpoint,
            negative_tolerance,
            positive_tolerance,
            repeat_count,
            wait_after,
            retry_count,
            trigger_log,
            on_warning,
            timeout,
            scanner=scanner,
            scanner_attributes=scanner_attributes,
        )

    def body(self):
        self.check_timeout = 0
        try:
            self.logger.debug(
                "Setting setpoint to {} -{} / +{}".format(
                    self.setpoint, self.negative_tolerance, self.positive_tolerance
                )
            )
            self.device = kamzik3.session.get_device(self.device_id)
            self.device_attribute = self.device.get_attribute(self.attribute)

            if not self.device.in_statuses(READY_DEVICE_STATUSES):
                raise DeviceError("Device {} is not ready".format(self.device_id))
            if self.check_value_on_setpoint(self.device_attribute.value()):
                return
            # Attach callback for attribute and status changes
            self.device.attach_attribute_callback(
                self.attribute, self.check_attribute_set, key_filter=VALUE
            )
            self.device.attach_attribute_callback(
                ATTR_STATUS, self.check_device_status, key_filter=VALUE
            )
            # Set device's attribute to desired setpoint
            setpoint = self.device_attribute.convert_units(self.setpoint)
            self.device.set_attribute(
                self.attribute + [VALUE], setpoint.m, callback=self.on_value_set
            )
            # Check if reached setpoint or timed out
            self.device_status_idle_flag = self.device.in_statuses(IDLE_DEVICE_STATUSES)
            self.device_setpoint_reached_flag = False

            if self.check_value_on_setpoint(self.device_attribute.value()):
                self.check_event.set()
            else:
                while (
                    self.get_state() == BUSY
                    and self.check_timeout <= self.check_max_timeout
                ):
                    self.check_event.wait(0.01)
                    # To successfully finish step device has to be IDLE and attributes value within setpoints tolerance
                    if (
                        self.device_status_idle_flag
                        and self.device_setpoint_reached_flag
                    ):
                        # Set check event and break while loop
                        self.check_event.set()
                        break
                    else:
                        # Reset check_timeout
                        self.check_timeout += 10
        except (DeviceError, AttributeError) as e:
            self.error(e)
        # Raise warning if setpoint was not reached
        if self.get_state() != STOPPED and not self.check_event.isSet():
            description = "{}'s attribute setpoint {}: {} could not be reached.".format(
                self.device.device_id, self.attribute, self.setpoint
            )
            self.warning(description)

        # Detach attribute and status callback
        self.device.detach_attribute_callback(self.attribute, self.check_attribute_set)
        self.device.detach_attribute_callback(ATTR_STATUS, self.check_device_status)
        # Remove device and attributes
        self.device = None
        self.device_attribute = None

    def get_output(self):
        device = kamzik3.session.get_device(self.device_id)
        return "{}".format(device.get_attribute(self.attribute).value())

    def check_attribute_set(self, value):
        # Check if value is within setpoint tolerants
        if self.check_value_on_setpoint(self.device_attribute.value()):
            self.device_setpoint_reached_flag = True
        else:
            self.device_setpoint_reached_flag = False
        # Reset check_timeout when device is busy
        if not self.device_status_idle_flag:
            self.check_timeout = 0

    def check_device_status(self, value):
        # Check if device is idle
        if value in IDLE_DEVICE_STATUSES:
            self.device_status_idle_flag = True
        else:
            self.device_status_idle_flag = False

    def on_value_set(self, key, value):
        # Check for error when setting setpoint
        if key == RESPONSE_ERROR:
            self.error(value)

    def reset(self):
        self.device_status_idle_flag = False
        self.device_setpoint_reached_flag = False
        self.check_event.clear()
        super().reset()

    def get_output_header(self):
        lines = [
            "Type: {}".format("Attribute"),
            "Device: {}".format(self.device_id),
            "Attribute: {}".format(self.attribute),
        ]

        return lines + StepSetpointNumerical.get_output_header(self)

    def stop(self):
        device = kamzik3.session.get_device(self.device_id)
        device.stop()
        device.wait_for_status(STATUS_IDLE)
        StepSetpointNumerical.stop(self)

    def warning(self, warning_message):
        device = kamzik3.session.get_device(self.device_id)
        device.stop()
        device.wait_for_status(STATUS_IDLE)
        StepSetpointNumerical.warning(self, warning_message)


class StepDeviceMethod(Step):
    check_max_timeout = 2000
    check_timeout = 0
    device = None
    device_method = None
    retry_timeout = 1000

    def __init__(
        self,
        common_id,
        device_id,
        method,
        method_parameters,
        repeat_count=0,
        wait_after=units.Quantity(0, "s"),
        retry_count=0,
        busy_timeout=units.Quantity(1, "s"),
        trigger_log=True,
        on_warning=ABORT,
        timeout=units.Quantity(0, "s"),
        scanner=None,
        scanner_attributes=None,
    ):
        self.device_id = device_id
        self.method = method
        self.method_parameters = method_parameters
        self.device_status_idle_flag = False
        self.check_event = Event()
        # self.timeout_lock = Lock()  # Prevents race on setting check_timeout
        self.busy_timeout = busy_timeout
        if not hasattr(self, "logger"):
            self.logger = logging.getLogger(
                "Macro.Step.{}.{}.{}".format(common_id, device_id, method)
            )
        Step.__init__(
            self,
            common_id,
            repeat_count,
            wait_after,
            retry_count,
            trigger_log,
            on_warning,
            timeout,
            scanner=scanner,
            scanner_attributes=scanner_attributes,
        )

    def body(self):
        self.check_timeout = 0
        try:
            self.logger.debug("Executing method {}".format(self.method))
            self.device = kamzik3.session.get_device(self.device_id)
            self.device_method = getattr(self.device, self.method)
            if not self.device.in_statuses(READY_DEVICE_STATUSES):
                raise DeviceError("Device {} is not ready".format(self.device_id))
            # Attach callback for attribute and status changes
            self.device.attach_attribute_callback(
                ATTR_STATUS, self.check_device_status, key_filter=VALUE
            )
            # Set device's attribute to desired setpoint
            self.device_method(**self.method_parameters)
            # Check if reached setpoint or timed out
            self.device_status_idle_flag = self.device.in_statuses(IDLE_DEVICE_STATUSES)
            wait_for_status_busy_timeout = self.busy_timeout.to("s").m / 0.1
            while (
                self.get_state() == BUSY
                and self.device_status_idle_flag
                and wait_for_status_busy_timeout > 0
            ):
                self.check_event.wait(0.1)
                wait_for_status_busy_timeout -= 1
            while self.get_state() == BUSY and not self.device_status_idle_flag:
                self.check_event.wait(0.1)
            self.check_event.set()
        except (DeviceError, AttributeError) as e:
            self.error(e)

        # Detach attribute and status callback
        self.device.detach_attribute_callback(ATTR_STATUS, self.check_device_status)
        # Remove device and attributes
        self.device = None
        self.device_method = None

    def check_device_status(self, value):
        # Check if device is idle
        if value in IDLE_DEVICE_STATUSES:
            self.device_status_idle_flag = True
        else:
            self.device_status_idle_flag = False

    def retry(self, retry_reason):
        try:
            # Make sure we tried to stop whatever is going on before retrying step again.
            kamzik3.session.get_device(self.device_id).stop()
        except DeviceError:
            self.logger.error("Device could not be stopped")
        Step.retry(self, retry_reason)

    def on_value_set(self, key, value):
        # Check for error when setting setpoint
        if key == RESPONSE_ERROR:
            self.error(value)

    def reset(self):
        self.device_status_idle_flag = False
        self.check_event.clear()
        Step.reset(self)

    def warning(self, warning_message):
        device = kamzik3.session.get_device(self.device_id)
        device.stop()
        device.wait_for_status(STATUS_IDLE)
        Step.warning(
            self,
            "{} executing {} on {}".format(
                warning_message, self.method, self.device_id
            ),
        )

    def stop(self):
        device = kamzik3.session.get_device(self.device_id)
        device.stop()
        device.wait_for_status(STATUS_IDLE)
        Step.stop(self)

    def get_output_header(self):
        lines = [
            "Type: {}".format("Method"),
            "Device: {}".format(self.device_id),
            "Busy timeout: {}".format(self.busy_timeout),
            "Method: {}".format(self.method),
        ]
        for attribute, value in self.method_parameters.items():
            lines.append("{}: {}".format(attribute, value))

        return lines + Step.get_output_header(self)


# todo: Revise Parallel step
class StepParallel(Step):
    def __init__(
        self,
        common_id,
        step_list,
        repeat_count=0,
        wait_after=units.Quantity(0, "s"),
        retry_count=0,
        trigger_log=True,
        on_warning=ABORT,
        timeout=units.Quantity(0, "s"),
        scanner=None,
        scanner_attributes=None,
    ):
        assert isinstance(step_list, list)
        self.step_list = step_list
        for step in self.step_list:
            if not isinstance(step, Step):
                raise TypeError("Step {} is not type of Step".format(step))
        Step.__init__(
            self,
            common_id,
            repeat_count,
            wait_after,
            retry_count,
            trigger_log,
            on_warning,
            timeout,
            scanner=scanner,
            scanner_attributes=scanner_attributes,
        )

    def body(self):
        step_threads = []
        # Start each step in separate thread
        for step in self.step_list:
            step_thread = Thread(target=step.start)
            step_threads.append(step_thread)
            step_thread.start()

        # Check if parallel step was not aborted
        while len(step_threads) != 0 and self.get_state() == BUSY:
            for step_thread in step_threads[:]:
                if step_thread.is_alive():
                    # Try to join thread with 100 ms
                    step_thread.join(timeout=0.1)
                else:
                    step_threads.remove(step_thread)

            for step in self.step_list:
                if step.get_state() == ERROR:
                    self.set_state(ERROR)
                    self.error_message = step.error_message
                    raise MacroException(self.error_message)
                elif step.get_state() == STOPPED:
                    self.set_state(STOPPED)

        if self.get_state() == STOPPED:
            for step in self.step_list:
                if step.get_state() == BUSY:
                    step.stop()
