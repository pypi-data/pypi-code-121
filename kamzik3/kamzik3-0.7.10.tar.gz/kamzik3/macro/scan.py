import copy
import logging
import random
import time

from numpy import linspace

import kamzik3
from kamzik3 import units
from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.macro.common import StepGenerator
from kamzik3.macro.step import StepSetpointNumerical


class Scan(StepGenerator):
    first_step_at = 0

    def __init__(
        self,
        common_id,
        start_point,
        end_point,
        steps_count,
        step_class=StepSetpointNumerical,
        step_attributes=None,
        repeat_count=0,
        random_deviation=units.Quantity(0, "percent"),
        wait_after=units.Quantity(0, "s"),
        retry_count=0,
        trigger_log=True,
        as_step=False,
        bidirectional=False,
        scanner=None,
        scanner_attributes=None,
        return_back=True,
        on_warning=ABORT,
        timeout=units.Quantity(0, "s"),
    ):
        assert isinstance(start_point, units.Quantity)
        assert isinstance(end_point, units.Quantity)
        assert isinstance(wait_after, units.Quantity)
        assert steps_count > 0
        self.return_back = return_back
        self.step_index = 0
        self.start_point = start_point
        self.end_point = end_point
        self.random_deviation = random_deviation
        if as_step:
            self.steps_count = 1
            self.points_count = 1
        else:
            self.steps_count = steps_count
            self.points_count = steps_count + 1
        self.bidirectional = bidirectional
        self.scan_pass = 0
        self.steps = self.step_generator()
        self.scanning_range = linspace(start_point.m, end_point.m, steps_count + 1)
        self.step_class = step_class
        self.step_attributes = step_attributes
        if self.step_attributes is None:
            self.step_attributes = {}
        self.current_step = None
        self.as_step = as_step
        self.logger = logging.getLogger("Macro.Scan.{}".format(common_id))
        attribute = kamzik3.session.get_device(
            self.step_attributes["device_id"]
        ).get_attribute(self.step_attributes["attribute"])
        self.initial_value_of_attribute = attribute.value()
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

    def set_steps_count(self, steps_count):
        """
        Set number of steps for current scan.

        Create step generator within the range of start_point and end_point of size
        steps_count.

        :param steps_count: int
        """
        assert steps_count > 0
        if self.as_step:
            self.steps_count = 1
            self.points_count = 1
        else:
            self.steps_count = steps_count
            self.points_count = steps_count + 1
        self.steps = self.step_generator()
        self.scanning_range = linspace(
            self.start_point.m, self.end_point.m, steps_count + 1
        )

    def get_total_steps_count(self):
        """
        Return total number of steps for current Scan.

        This number includes all repetitions as well.

        :return: int
        """
        repeat_step = self.step_attributes.get("repeat_count", 0) + 1
        repeat_scan = self.repeat_count + 1
        return self.steps_count * repeat_step * repeat_scan

    def get_total_points_count(self):
        """
        Return total number of points for current Scan.

        This number includes all repetitions as well.

        :return: int
        """
        repeat_step = self.step_attributes.get("repeat_count", 0) + 1
        repeat_scan = self.repeat_count + 1
        return self.points_count * repeat_step * repeat_scan

    def step_generator(self):
        """
        Initiate step generator.

        :return: Step
        """
        self.first_step_at = time.time()
        scanning_range = self.scanning_range
        if self.bidirectional and self.scan_pass % 2:
            # Reverse scanning range for each odd scan_pass if bidirectional flag is set
            scanning_range = reversed(self.scanning_range)
        for (
            self.step_attributes["common_id"],
            self.step_attributes["setpoint"],
        ) in enumerate(scanning_range):
            # Get through canning range of setpoints and generate step for each one of them
            if self.get_state() == STOPPED:
                # Cancel generator when scan was stopped
                break
            random_offset = 0
            if self.random_deviation.m > 0:
                # If random deviation is set, calculate max size of randomized part of the step
                half_step_size = (
                    abs(self.scanning_range[1] - self.scanning_range[0])
                    * (self.random_deviation.m / 100)
                ) / 2
                # Generate random offset
                random_offset = random.uniform(-half_step_size, half_step_size)
            self.step_attributes["setpoint"] = units.Quantity(
                self.step_attributes["setpoint"] + random_offset, self.start_point.u
            )
            # Generate next step based on step attributes
            yield self.step_class(**self.step_attributes)
            # Increase step_index counter
            self.step_index += 1
        # Increase scan pass counter
        self.scan_pass += 1

    def get_reset_step(self):
        """
        Get Step, which initiate Device Attribute into initial Value.

        :return: Step
        """
        setpoint_attributes_copy = copy.copy(self.step_attributes)
        setpoint_attributes_copy["common_id"] = "ReturnBack"
        setpoint_attributes_copy["setpoint"] = self.initial_value_of_attribute
        setpoint_attributes_copy["wait_after"] = units.Quantity(0, "s")
        setpoint_attributes_copy["timeout"] = units.Quantity(0, "s")
        try:
            del setpoint_attributes_copy["output"]
        except KeyError:
            pass
        return self.step_class(**setpoint_attributes_copy)

    def return_back_callback(self):
        """
        Callback function for the Device attributes.

        Whenever Scan was Stopped or aborted, this callback ensures that Device
        attributes get back to initial value.
        """
        if self.return_back and self.initial_value_of_attribute is not None:
            # if return_back is set and initial value of attribute is not None
            device = kamzik3.session.get_device(self.step_attributes["device_id"])
            # wait until device is one of the Idle statuses
            if device.wait_for_status(IDLE_DEVICE_STATUSES):
                # get reset step
                step = self.get_reset_step()
                if isinstance(step, list):
                    # we have list of steps to execute
                    for sub_step in step:
                        sub_step.start()
                else:
                    # execute reset step
                    step.start()
            else:
                # device did not get into idle state after timeout of 1s
                self.logger.error(
                    "Could not return {} to {}, device was not IDLE".format(
                        self.step_attributes["attribute"],
                        self.initial_value_of_attribute,
                    )
                )

    def get_output_header(self):
        # ~ is a pint format specification
        lines = [
            "Type: {}".format("Scan"),
            "Scanner: {}".format(self.scanner),
            "Device: {}".format(self.step_attributes["device_id"]),
            "Attribute: {}".format(
                Attribute.list_attribute(self.step_attributes["attribute"])
            ),
            "Start point: {:~}".format(self.start_point),  # type: ignore
            "End point: {:~}".format(self.end_point),  # type: ignore
            "Steps count: {}".format(self.steps_count),  # type: ignore
            "Step size: {:~}".format(  # type: ignore
                (self.end_point - self.start_point) / self.steps_count
            ),
            "Points count: {}".format(self.points_count),
            "Bidirectional: {}".format(self.bidirectional),
            "Negative tolerance: {:~}".format(  # type: ignore
                self.step_attributes["negative_tolerance"]
            ),
            "Positive tolerance: {:~}".format(  # type: ignore
                self.step_attributes["positive_tolerance"]
            ),
            "Random deviation: {:~}".format(self.random_deviation),  # type: ignore
            "Wait: {:~}".format(self.step_attributes["wait_after"]),  # type: ignore
            "Repeat count: {}".format(self.repeat_count),
            "Retry: {}".format(self.retry_count),
            "Return back: {}".format(self.return_back),
            "Trigger log: {}".format(self.step_attributes["trigger_log"]),
        ]
        if self.scanner_attributes is not None:
            for key, value in self.scanner_attributes.items():
                lines.append("{}: {}".format(key, value))
        return lines

    def remove(self):
        if self.current_step is not None:
            self.current_step.remove()
        self.steps = None
        self.scanning_range = None
        self.step_class = None
        self.step_attributes = None
        self.current_step = None
        StepGenerator.remove(self)
