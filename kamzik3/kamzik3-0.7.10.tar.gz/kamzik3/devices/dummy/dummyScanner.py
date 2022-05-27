import numpy as np

import kamzik3
from kamzik3 import MacroException
from kamzik3 import session
from kamzik3.constants import *
from kamzik3.devices.general.deviceScanner import DeviceScanner
from kamzik3.macro.macro import Macro
from kamzik3.macro.step import StepDeviceAttributeNumerical
from kamzik3.snippets.snippetsDecorators import expose_method


class DummyScanner(DeviceScanner):
    def _init_attributes(self):
        DeviceScanner._init_attributes(self)
        self.create_attribute(
            ATTR_DWELL_TIME,
            default_value=100,
            unit="ms",
            min_value=0,
            default_type=np.int64,
        )

    def _init_new_scan(self, _scanner_input, _scanner_attributes):
        self.logger.info(
            "Initiating new scan number {}".format(
                kamzik3.session.get_value(ATTR_SCAN_COUNT)
            )
        )

    @expose_method()
    def get_scanner_attributes(self):
        return [ATTR_DWELL_TIME]

    @expose_method()
    def get_scanner_macro(self, scanner_input, scanner_attributes, parent_macro=None):
        macro = Macro(device_id="{}_{}".format(self.device_id, scanner_input.common_id))
        distance = abs(scanner_input.start_point - scanner_input.end_point)
        dwell_time = scanner_attributes[ATTR_DWELL_TIME]
        device_id = scanner_input.step_attributes["device_id"]
        # current_velocity = session.get_device(device_id).get_attribute(ATTR_MAXIMUM_VELOCITY).value()
        maximum_velocity = (
            session.get_device(device_id).get_attribute(ATTR_MAXIMUM_VELOCITY).maximum()
        )
        mv = session.get_device(device_id).get_attribute(ATTR_MAXIMUM_VELOCITY)
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
        if not scanner_input.bidirectional:
            velocity_step_0 = StepDeviceAttributeNumerical(
                "SetMaxVelocityStep",
                device_id,
                ATTR_MAXIMUM_VELOCITY,
                maximum_velocity,
                trigger_log=False,
                negative_tolerance=mv.negative_tolerance(),
                positive_tolerance=mv.positive_tolerance(),
                on_warning=scanner_input.step_attributes["on_warning"],
                timeout=scanner_input.step_attributes["timeout"],
            )
            position_step_0 = StepDeviceAttributeNumerical(
                "SetInitPositionStep",
                device_id,
                ATTR_POSITION,
                scanner_input.start_point,
                trigger_log=False,
                negative_tolerance=scanner_input.step_attributes["negative_tolerance"],
                positive_tolerance=scanner_input.step_attributes["positive_tolerance"],
                on_warning=scanner_input.step_attributes["on_warning"],
                timeout=scanner_input.step_attributes["timeout"],
            )
            macro.add(velocity_step_0)
            macro.add(position_step_0)
        velocity_step_1 = StepDeviceAttributeNumerical(
            "FinalVelocityStep",
            device_id,
            ATTR_MAXIMUM_VELOCITY,
            final_velocity,
            trigger_log=False,
            negative_tolerance=mv.negative_tolerance(),
            positive_tolerance=mv.positive_tolerance(),
            on_warning=scanner_input.step_attributes["on_warning"],
            timeout=scanner_input.step_attributes["timeout"],
        )
        macro.add(velocity_step_1)
        macro.add(scanner_input)
        # velocity_step_2 = StepDeviceAttributeNumerical("PreviousVelocityStep", device_id, ATTR_MAXIMUM_VELOCITY,
        #                                              current_velocity,
        #                                              trigger_log=False, negative_tolerance=mv.negative_tolerance(),
        #                                              positive_tolerance=mv.positive_tolerance())
        # macro.add(velocity_step_2)
        return macro
