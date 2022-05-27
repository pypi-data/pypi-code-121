import numpy as np
from typing import List

from kamzik3 import MacroException
from kamzik3 import session
from kamzik3.constants import *
from kamzik3.devices.general.deviceScanner import DeviceScanner
from kamzik3.macro.macro import Macro
from kamzik3.macro.step import StepDeviceAttributeNumerical
from kamzik3.snippets.snippetsDecorators import expose_method


class GeneralFlyScanner(DeviceScanner):
    attribute_filter: List[str] = [ATTR_VELOCITY, ATTR_POSITION]

    def _init_attributes(self):
        DeviceScanner._init_attributes(self)
        self.create_attribute(
            ATTR_DWELL_TIME,
            default_value=100,
            unit="ms",
            min_value=0,
            default_type=np.int64,
        )

    @expose_method()
    def get_scanner_attributes(self):
        return [ATTR_DWELL_TIME]

    @expose_method()
    def get_scanner_macro(self, scanner_input, scanner_attributes, parent_macro=None):
        device_id = scanner_input.step_attributes["device_id"]
        device = session.get_device(device_id)
        macro = Macro(device_id="{}_{}".format(self.device_id, scanner_input.common_id))
        distance = abs(scanner_input.start_point - scanner_input.end_point)
        dwell_time = scanner_attributes[ATTR_DWELL_TIME]
        velocity = device.get_attribute(ATTR_VELOCITY)
        maximum_velocity = velocity.maximum()
        scan_line_time = dwell_time * scanner_input.steps_count
        final_velocity = distance / scan_line_time
        final_velocity = final_velocity.to(maximum_velocity.u)

        if final_velocity > maximum_velocity:
            raise MacroException(
                "Calculated velocity {} is higher than maximum velocity {}.".format(
                    final_velocity, maximum_velocity
                )
            )

        scanner_input.set_steps_count(1)
        max_velocity_step = StepDeviceAttributeNumerical(
            "SetMaxVelocityStep",
            device_id,
            ATTR_VELOCITY,
            maximum_velocity,
            trigger_log=False,
            negative_tolerance=velocity.negative_tolerance(),
            positive_tolerance=velocity.positive_tolerance(),
            on_warning=scanner_input.step_attributes["on_warning"],
            timeout=scanner_input.step_attributes["timeout"],
        )
        if not scanner_input.bidirectional:
            macro.add(max_velocity_step)
            macro.add(
                StepDeviceAttributeNumerical(
                    "SetInitPositionStep",
                    device_id,
                    ATTR_POSITION,
                    scanner_input.start_point,
                    trigger_log=False,
                    negative_tolerance=scanner_input.step_attributes[
                        "negative_tolerance"
                    ],
                    positive_tolerance=scanner_input.step_attributes[
                        "positive_tolerance"
                    ],
                    on_warning=scanner_input.step_attributes["on_warning"],
                    timeout=scanner_input.step_attributes["timeout"],
                )
            )

        macro.add(
            StepDeviceAttributeNumerical(
                "FinalVelocityStep",
                device_id,
                ATTR_VELOCITY,
                final_velocity,
                trigger_log=False,
                negative_tolerance=velocity.negative_tolerance(),
                positive_tolerance=velocity.positive_tolerance(),
                on_warning=scanner_input.step_attributes["on_warning"],
                timeout=scanner_input.step_attributes["timeout"],
            )
        )

        previous_reset_step = scanner_input.get_reset_step()

        def get_reset_step():
            return [max_velocity_step, previous_reset_step]

        scanner_input.get_reset_step = get_reset_step
        macro.add(scanner_input)
        return macro


class GeneralFlyScannerMaxVelocity(DeviceScanner):
    attribute_filter = [ATTR_MAXIMUM_VELOCITY, ATTR_POSITION]

    def _init_attributes(self):
        DeviceScanner._init_attributes(self)
        self.create_attribute(
            ATTR_DWELL_TIME,
            default_value=100,
            unit="ms",
            min_value=0,
            default_type=np.int64,
        )

    @expose_method()
    def get_scanner_attributes(self):
        return [ATTR_DWELL_TIME]

    @expose_method()
    def get_scanner_macro(self, scanner_input, scanner_attributes, parent_macro=None):
        device_id = scanner_input.step_attributes["device_id"]
        device = session.get_device(device_id)
        macro = Macro(device_id="{}_{}".format(self.device_id, scanner_input.common_id))
        distance = abs(scanner_input.start_point - scanner_input.end_point)
        dwell_time = scanner_attributes[ATTR_DWELL_TIME]
        velocity = device.get_attribute(ATTR_MAXIMUM_VELOCITY)
        maximum_velocity = velocity.maximum()
        scan_line_time = dwell_time * scanner_input.steps_count
        final_velocity = distance / scan_line_time
        final_velocity = final_velocity.to(maximum_velocity.u)

        if final_velocity > maximum_velocity:
            raise MacroException(
                "Calculated velocity {} is higher than maximum velocity {}.".format(
                    final_velocity, maximum_velocity
                )
            )

        scanner_input.set_steps_count(1)
        max_velocity_step = StepDeviceAttributeNumerical(
            "SetMaxVelocityStep",
            device_id,
            ATTR_MAXIMUM_VELOCITY,
            maximum_velocity,
            trigger_log=False,
            negative_tolerance=velocity.negative_tolerance(),
            positive_tolerance=velocity.positive_tolerance(),
            on_warning=scanner_input.step_attributes["on_warning"],
            timeout=scanner_input.step_attributes["timeout"],
        )
        if not scanner_input.bidirectional:
            macro.add(max_velocity_step)
            macro.add(
                StepDeviceAttributeNumerical(
                    "SetInitPositionStep",
                    device_id,
                    ATTR_POSITION,
                    scanner_input.start_point,
                    trigger_log=False,
                    negative_tolerance=scanner_input.step_attributes[
                        "negative_tolerance"
                    ],
                    positive_tolerance=scanner_input.step_attributes[
                        "positive_tolerance"
                    ],
                    on_warning=scanner_input.step_attributes["on_warning"],
                    timeout=scanner_input.step_attributes["timeout"],
                )
            )

        macro.add(
            StepDeviceAttributeNumerical(
                "FinalVelocityStep",
                device_id,
                ATTR_MAXIMUM_VELOCITY,
                final_velocity,
                trigger_log=False,
                negative_tolerance=velocity.negative_tolerance(),
                positive_tolerance=velocity.positive_tolerance(),
                on_warning=scanner_input.step_attributes["on_warning"],
                timeout=scanner_input.step_attributes["timeout"],
            )
        )

        previous_reset_step = scanner_input.get_reset_step()

        def get_reset_step():
            return [max_velocity_step, previous_reset_step]

        scanner_input.get_reset_step = get_reset_step
        macro.add(scanner_input)
        return macro
