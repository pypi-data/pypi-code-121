""" Example of yaml configuration
Smaract0: &Smaract0 !Device:kamzik3.devices.deviceSmaractMcs1.DeviceSmaractMcs2
    device_id: Smaract0
    host: 192.168.83.91
Smaract0_axis_0: &Smaract0_axis_0 !Device:kamzik3.devices.deviceSmaractMcs1.DeviceSmaractMcs1Channe2
    device: *Smaract0
    channel: 0
    device_id: MotorAxis0
    config:
      attributes:
        !!python/tuple [Sensor type, Value]: 1
        !!python/tuple [Position +limit, Value]: 15mm
        !!python/tuple [Position -limit, Value]: -15mm
        !!python/tuple [Position, Tolerance]: [10nm, 10nm]


Positioner codes:
SL...S1SS 300 Linear positioner, single piezo element
SL...D1SS 301 Linear positioner, double piezo element
SL...S1SC1 303 Linear positioner, single piezo element
SL...D1SC1 304 Linear positioner, double piezo element
SL...D1SC2 307 Linear positioner, double piezo element
SR...S1S5S 309 Small rotary positioner S single mark
SR...S1S6S 312 Rotary positioner S single mark
SR...D1S6S 313 Rotary positioner, double piezo element
SR...D1S7S 316 Rotary positioner, double piezo element
SR...T1S8S 320 Large rotary positioner S single mark
SG...D1S1S 325 Goniometer, 60.5mm radius, double
SG...D1S2S 328 Goniometer, 77.5mm radius, double
SL...S1LE 342 Linear positioner, single piezo element
SL...D1LE 343 Linear positioner, double piezo element
SL...S1LS 345 Linear positioner, single piezo element
SL...D1LS 346 Linear positioner, double piezo element
SL...S1LC1 348 Linear positioner, single piezo element
SL...D1LC1 349 Linear positioner, double piezo element
SR...S1L2S 354 Rotary positioner L single mark
SR...D1L2S 355 Rotary positioner, double piezo element
SL...S1ME 357 Linear positioner, single piezo element
SL...D1ME 358 Linear positioner, double piezo element
SL...S1P1E 360 Linear positioner, double piezo element
SL...D1P1E 361 Linear positioner, double piezo element
SG...S1M1E 363 Goniometer, 60.5mm radius, single
SG...S1M2E 366 Goniometer, 77.5mm radius, single
SG...D1L1S 381 Goniometer, 60.5mm radius, double
SG...D1L2S 383 Goniometer, 77.5mm radius, double
SG...D1L1E 387 Goniometer, 60.5mm radius, double
SG...D1L2E 389 Goniometer, 77.5mm radius, double
SH...A1SS 395 High load table, single piezo element S single mark
"""
import re
import time

import numpy as np
from bidict import frozenbidict
from numbers import Real
from pint.errors import UndefinedUnitError
from typing import List, Callable, Optional

import kamzik3
from kamzik3 import DeviceError, CommandFormatException, DeviceUnitError, units
from kamzik3.constants import *
from kamzik3.devices.deviceChannel import DeviceChannel
from kamzik3.devices.deviceSocket import DeviceSocket
from kamzik3.snippets.snippetsDecorators import expose_method
from kamzik3.snippets.snippetsUnits import device_units


class DeviceSmaractMcs2(DeviceSocket):
    response_timeout = 3000
    terminator = b"\r\n"
    error_pattern = re.compile(r'([-0-9]+),"([\w ]+)"')
    sensor_modes = frozenbidict({"Disabled": 0, "Enabled": 1, "Power safe": 2})
    move_modes = frozenbidict(
        {
            "Absolute": 0,
            "Relative": 1,
            "Scan absolute": 2,
            "Scan relative": 3,
            "Step": 4,
        }
    )
    safe_direction_modes = frozenbidict({"Forward": 0, "Backward": 1})
    emergency_stop_modes = frozenbidict(
        {"Normal": 0, "Restricted": 1, "Auto release": 2}
    )

    def __init__(self, host, port=55551, device_id=None, config=None):
        super().__init__(host, port, device_id, config)

    def _init_attributes(self):
        super()._init_attributes()
        self.create_attribute(ATTR_STATE, readonly=True, default_type=np.uint16)
        self.create_attribute(ATTR_SERIAL_NUMBER, readonly=True)
        self.create_attribute(ATTR_CHANNELS, readonly=True, default_type=np.uint16)
        self.create_attribute(ATTR_MODULES, readonly=True, default_type=np.uint16)
        self.create_attribute(ATTR_HAND_TOOL, readonly=True, default_type=bool)
        self.create_attribute(ATTR_MOVEMENT_LOCKED, readonly=True, default_type=bool)
        self.create_attribute(
            ATTR_INTERNAL_COMM_FAILURE, readonly=True, default_type=bool
        )
        self.create_attribute(ATTR_STREAMING, readonly=True, default_type=bool)
        self.create_attribute(
            ATTR_EMERGENCY_STOP,
            default_type=self.emergency_stop_modes.keys(),
            set_function=self.set_emergency_stop_mode,
        )

    def command(self, command, callback=None, with_token=False, returning=True):
        if not self.valid_command_format(command):
            raise CommandFormatException("Command '{}' form is invalid".format(command))

        returning = True
        command += ":SYST:ERR:NEXT?\r\n"
        return super().command(command, callback, with_token, returning)

    def poll_command(self, command, interval):
        if not self.valid_command_format(command):
            raise CommandFormatException("Command '{}' form is invalid".format(command))

        command += ":SYST:ERR:NEXT?\r\n"
        super().poll_command(command, interval)

    def remove_poll_command(self, command, interval):
        if not self.valid_command_format(command):
            raise CommandFormatException("Command '{}' form is invalid".format(command))

        command += ":SYST:ERR:NEXT?\r\n"
        super().remove_poll_command(command, interval)

    def handle_configuration(self):

        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()
            self.set_status(STATUS_CONFIGURED)
            self.logger.info(
                "Device configuration took {} sec.".format(time.time() - start_at)
            )

        # Check for possible errors
        self.get_errors_count()
        # Get number of channels
        self.command(":DEV:NOCH?\r\n")
        # Get serial number
        self.command(":DEV:SNUM?\r\n")
        # Get number of modules
        self.command(":DEV:NOBM?\r\n", callback=_finish_configuration)
        # Get emergency stop mode
        self.command(":DEV:EST:MODE?\r\n")
        self.start_polling()

    def handle_configuration_event(self):
        try:
            start_at = time.time()
            self.set_status(STATUS_CONFIGURING)
            self.handle_configuration()
            self.logger.info(
                "Device configuration took {} sec.".format(time.time() - start_at)
            )
        except DeviceError:
            self.logger.exception("Error during configuration")

    def valid_command_format(self, command):
        return command is not None and command[-2:] == "\r\n"

    def handle_readout(self, readout_buffer):
        is_error_message = self.error_pattern.match(readout_buffer[0])
        command, output, callback, token = super().handle_readout(readout_buffer)
        if is_error_message is not None:
            if command == ":SYST:ERR:NEXT?\r\n" and int(is_error_message.group(1)) != 0:
                self.logger.error(readout_buffer[0])
            elif int(is_error_message.group(1)) != 0:
                self.logger.error(readout_buffer[0])

            if callback is not None:
                self.handle_readout_callback(callback, command, readout_buffer)
            if token:
                kamzik3.session.publisher.push_message(
                    self.device_id, [command, readout_buffer], token
                )
                for observer in self._observers[:]:
                    if isinstance(observer, DeviceSmaractMcs2Channel):
                        kamzik3.session.publisher.push_message(
                            observer.device_id, [command, readout_buffer], token
                        )
            return
        else:
            command = command.replace(":SYST:ERR:NEXT?\r\n", "")
            self.commands_buffer.appendleft(
                ((":SYST:ERR:NEXT?\r\n", None, None, True), time.time())
            )

        command = command.strip()

        if command == ":DEV:NOCH?":
            self.set_offsetted_value(ATTR_CHANNELS, int(output))
        elif command == ":DEV:SNUM?":
            self.set_offsetted_value(ATTR_SERIAL_NUMBER, output.replace('"', ""))
        elif command == ":DEV:NOBM?":
            self.set_offsetted_value(ATTR_MODULES, int(output))
            for i in range(int(output)):
                module_name = "Module{}".format(i)
                self.create_attribute(
                    ATTR_STATE, module_name, readonly=True, default_type=np.uint16
                )
                self.create_attribute(
                    ATTR_TEMPERATURE,
                    module_name,
                    readonly=True,
                    default_type=np.float32,
                    decimals=2,
                    unit="degC",
                )
                self.create_attribute(
                    ATTR_SENSOR_PRESENT, module_name, readonly=True, default_type=bool
                )
                self.create_attribute(
                    ATTR_BOOSTER_PRESENT, module_name, readonly=True, default_type=bool
                )
                self.create_attribute(
                    ATTR_ADJUSTMENT_ACTIVE,
                    module_name,
                    readonly=True,
                    default_type=bool,
                )
                self.create_attribute(
                    ATTR_IOM_PRESENT, module_name, readonly=True, default_type=bool
                )
                self.create_attribute(
                    ATTR_INTERNAL_COMM_FAILURE,
                    module_name,
                    readonly=True,
                    default_type=bool,
                )
                self.create_attribute(
                    ATTR_HIGH_VOLTAGE_FAILURE,
                    module_name,
                    readonly=True,
                    default_type=bool,
                )
                self.create_attribute(
                    ATTR_HIGH_VOLTAGE_OVERLOAD,
                    module_name,
                    readonly=True,
                    default_type=bool,
                )
                self.create_attribute(
                    ATTR_OVER_TEMPERATURE, module_name, readonly=True, default_type=bool
                )

                self.poll_command(":MOD{}:STAT?\r\n".format(i), 2000)
                self.poll_command(":MOD{}:TEMP?\r\n".format(i), 2000)
        elif command == ":DEV:STAT?":
            output = int(output)
            self.set_offsetted_value(ATTR_STATE, output)
            self.set_offsetted_value(ATTR_HAND_TOOL, bool(output % 0x0001))
            self.set_offsetted_value(ATTR_MOVEMENT_LOCKED, bool(output % 0x0002))
            self.set_offsetted_value(ATTR_INTERNAL_COMM_FAILURE, bool(output % 0x0100))
            self.set_offsetted_value(ATTR_STREAMING, bool(output % 0x1000))
        elif command == ":DEV:EST:MODE?":
            output = int(output)
            self.set_offsetted_value(
                ATTR_EMERGENCY_STOP, self.emergency_stop_modes.inverse[output]
            )
        elif command == ":SYST:ERR:COUN?":
            if int(output) > 0:
                self.get_next_error()
        elif command == ":SYST:ERR:NEXT?":
            self.logger.error(output)
            self.get_errors_count()
        elif command[:4] == ":MOD":
            _, module, attribute = command.split(":")
            module_name = "Module{}".format(module[3:])
            if attribute == "TEMP?":
                self.set_offsetted_value((module_name, ATTR_TEMPERATURE), float(output))
            elif attribute == "STAT?":
                output = int(output)
                self.set_offsetted_value((module_name, ATTR_STATE), output)
                self.set_offsetted_value(
                    (module_name, ATTR_SENSOR_PRESENT), bool(output & 0x0001)
                )
                self.set_offsetted_value(
                    (module_name, ATTR_BOOSTER_PRESENT), bool(output & 0x0002)
                )
                self.set_offsetted_value(
                    (module_name, ATTR_ADJUSTMENT_ACTIVE), bool(output & 0x0004)
                )
                self.set_offsetted_value(
                    (module_name, ATTR_IOM_PRESENT), bool(output & 0x0008)
                )
                self.set_offsetted_value(
                    (module_name, ATTR_INTERNAL_COMM_FAILURE), bool(output & 0x0100)
                )
                self.set_offsetted_value(
                    (module_name, ATTR_HIGH_VOLTAGE_FAILURE), bool(output & 0x1000)
                )
                self.set_offsetted_value(
                    (module_name, ATTR_HIGH_VOLTAGE_OVERLOAD), bool(output & 0x2000)
                )
                self.set_offsetted_value(
                    (module_name, ATTR_OVER_TEMPERATURE), bool(output & 0x4000)
                )
        elif command[:5] == ":CHAN":
            chunks = command.split(":")
            channel, attribute = chunks[1], chunks[-1]
            channel = int(channel[4:])
            if attribute == "STAT?":
                attribute, output = ATTR_STATE, int(output)
            elif attribute == "CURR?":
                attribute, output = ATTR_POSITION, int(output)
            elif attribute == "TARG?":
                attribute, output = ATTR_TARGET_POSITION, int(output)
            elif attribute == "TEMP?":
                attribute, output = ATTR_TEMPERATURE, float(output)
            elif attribute == "UNIT?":
                attribute, output = ATTR_ENCODER_BASE_UNIT, int(output)
            elif attribute == "RES?":
                attribute, output = ATTR_ENCODER_RESOLUTION, int(output)
            elif attribute == "NAME?":
                attribute, output = ATTR_POSITIONER_TYPE, output.replace('"', "")
            elif attribute == "CODE?":
                attribute, output = ATTR_POSITIONER_CODE, int(output)
            elif attribute == "MIN?":
                attribute, output = ATTR_POSITION_LOWER_LIMIT, int(output)
            elif attribute == "MAX?":
                attribute, output = ATTR_POSITION_UPPER_LIMIT, int(output)
            elif attribute == "FREQ?":
                attribute, output = ATTR_STEP_FREQUENCY, int(output)
            elif attribute == "AMPL?":
                attribute, output = ATTR_STEP_AMPLITUDE, int(output)
            elif attribute == "VEL?":
                attribute, output = ATTR_VELOCITY, int(output)
            elif attribute == "HOLD?":
                attribute, output = ATTR_HOLDING_TIME, int(output)
            elif attribute == "ACC?":
                attribute, output = ATTR_ACCELERATION, int(output)
            elif attribute == "MODE?":
                attribute, output = (
                    ATTR_SENSOR_MODE,
                    self.sensor_modes.inverse[int(output)],
                )
            elif attribute == "MMOD?":
                attribute, output = ATTR_MOVE_MODE, self.move_modes.inverse[int(output)]
            elif attribute == "SDIR?":
                attribute, output = (
                    ATTR_SAFE_DIRECTION,
                    self.safe_direction_modes.inverse[int(output)],
                )
            elif attribute == "OPT?":
                attribute, output = (
                    ATTR_REFERENCE_DIRECTION,
                    self.safe_direction_modes.inverse[int(output)],
                )
            else:
                return
            self.notify((channel, attribute), output)

        if callback is not None:
            self.handle_readout_callback(callback, command, readout_buffer)
        if token:
            kamzik3.session.publisher.push_message(
                self.device_id, [command, readout_buffer], token
            )
            for observer in self._observers[:]:
                if isinstance(observer, DeviceSmaractMcs2Channel):
                    kamzik3.session.publisher.push_message(
                        observer.device_id, [command, readout_buffer], token
                    )

    def start_polling(self):
        super().start_polling()
        self.poll_command(":DEV:STAT?\r\n", 1000)

    def get_errors_count(self):
        self.command(":SYST:ERR:COUN?\r\n")

    def get_next_error(self):
        self.command(":SYST:ERR:NEXT?\r\n")

    def set_emergency_stop_mode(self, value, callback=None):
        self.logger.info("Set emergency stop mode to {}".format(value))
        value = self.emergency_stop_modes[value]
        # Set this mode as a default
        self.command(
            ":DEV:EST:MODE:DEF {}\r\n".format(value), callback, with_token=True
        )
        return self.command(
            ":DEV:EST:MODE {}\r\n".format(value), callback, with_token=True
        )


class DeviceSmaractMcs2Channel(DeviceChannel):
    sensor_modes = DeviceSmaractMcs2.sensor_modes
    move_modes = DeviceSmaractMcs2.move_modes
    safe_direction_modes = DeviceSmaractMcs2.safe_direction_modes

    def _init_attributes(self):
        super()._init_attributes()
        self.create_attribute(ATTR_STATE, readonly=True, default_type=np.uint16)
        self.create_attribute(
            ATTR_TEMPERATURE,
            readonly=True,
            default_type=np.float16,
            decimals=2,
            unit="degC",
        )
        self.create_attribute(ATTR_MOVING, readonly=True, default_type=bool)
        self.create_attribute(
            ATTR_POSITION,
            readonly=False,
            default_type=np.int64,
            set_function=self._move_absolute,
            set_value_when_set_function=False,
        )
        self.create_attribute(
            ATTR_TARGET_POSITION,
            default_type=np.int64,
            set_function=self._move_absolute,
            set_value_when_set_function=False,
        )
        self.create_attribute(ATTR_CLOSED_LOOP_ACTIVE, readonly=True, default_type=bool)
        self.create_attribute(ATTR_CALIBRATING, readonly=True, default_type=bool)
        self.create_attribute(ATTR_REFERENCING, readonly=True, default_type=bool)
        self.create_attribute(ATTR_HOLDING, readonly=True, default_type=bool)
        self.create_attribute(ATTR_MOVE_DELAYED, readonly=True, default_type=bool)
        self.create_attribute(ATTR_SENSOR_PRESENT, readonly=True, default_type=bool)
        self.create_attribute(ATTR_CALIBRATED, readonly=True, default_type=bool)
        self.create_attribute(ATTR_REFERENCED, readonly=True, default_type=bool)
        self.create_attribute(ATTR_END_STOP_REACHED, readonly=True, default_type=bool)
        self.create_attribute(
            ATTR_RANGE_LIMIT_REACHED, readonly=True, default_type=bool
        )
        self.create_attribute(
            ATTR_FOLLOWING_LIMIT_REACHED, readonly=True, default_type=bool
        )
        self.create_attribute(ATTR_MOVEMENT_FAILED, readonly=True, default_type=bool)
        self.create_attribute(ATTR_STREAMING, readonly=True, default_type=bool)
        self.create_attribute(ATTR_OVER_TEMPERATURE, readonly=True, default_type=bool)
        self.create_attribute(ATTR_INDEX_MARK, readonly=True, default_type=bool)
        self.create_attribute(ATTR_ENCODER_BASE_UNIT, readonly=True)
        self.create_attribute(
            ATTR_ENCODER_RESOLUTION, readonly=True, default_type=np.int8
        )
        self.create_attribute(
            ATTR_POSITIONER_CODE,
            readonly=False,
            default_type=np.int8,
            min_value=0,
            max_value=500,
            set_function=self.set_positioner_code,
        )
        self.create_attribute(ATTR_POSITIONER_TYPE, readonly=True)
        self.create_attribute(
            ATTR_POSITION_LOWER_LIMIT,
            default_type=np.int64,
            set_function=self.set_lower_position_limit,
        )
        self.create_attribute(
            ATTR_POSITION_UPPER_LIMIT,
            default_type=np.int64,
            set_function=self.set_upper_position_limit,
        )
        self.create_attribute(
            ATTR_CONFIGURED_LIMITS,
            default_type=TYPE_LIST,
            default_value=[None, None],
            set_function=self._check_limits,
        )
        self.create_attribute(
            ATTR_STEP_FREQUENCY,
            default_type=np.uint32,
            min_value=1,
            max_value=20e3,
            unit="Hz",
            set_function=self.set_step_frequency,
        )
        self.create_attribute(
            ATTR_STEP_AMPLITUDE,
            default_type=np.uint32,
            min_value=1,
            max_value=65535,
            set_function=self.set_step_amplitude,
        )
        self.create_attribute(
            ATTR_ACCELERATION,
            default_type=np.int64,
            min_value=0,
            max_value=100e9,
            set_function=self.set_acceleration,
        )
        self.create_attribute(
            ATTR_VELOCITY,
            default_type=np.int64,
            min_value=0,
            max_value=10e12,
            set_function=self.set_velocity,
        )
        self.create_attribute(
            ATTR_SENSOR_MODE,
            default_type=self.sensor_modes.keys(),
            set_function=self.set_sensor_mode,
        )
        self.create_attribute(
            ATTR_MOVE_MODE,
            default_type=self.move_modes.keys(),
            set_function=self.set_move_mode,
        )
        self.create_attribute(
            ATTR_SAFE_DIRECTION,
            default_type=self.safe_direction_modes.keys(),
            set_function=self.set_safe_direction,
        )
        self.create_attribute(
            ATTR_REFERENCE_DIRECTION,
            default_type=self.safe_direction_modes.keys(),
            set_function=self.set_reference_direction,
        )
        self.create_attribute(
            ATTR_HOLDING_TIME,
            default_type=np.int32,
            min_value=-1,
            unit="ms",
            set_function=self.set_holding_time,
        )
        self.create_attribute(ATTR_CLOSE_LOOP_UNIT, display=False)
        self.create_attribute(
            ATTR_OPEN_LOOP_FACTOR,
            default_value=[1, 1],
            default_type=TYPE_LIST,
            display=False,
        )
        self.create_attribute(
            ATTR_MOVE_METHOD,
            default_value=CLOSE_LOOP,
            default_type=[OPEN_LOOP, CLOSE_LOOP],
            set_function=self.set_move_method,
        )

    def _check_limits(self, limits: List[Real]) -> None:
        """
        Check if the limits are correctly configured.

        :param limits: list of two real numbers [lower_limit, upper_limit], None for a
         is limit is allowed.
        """
        if limits[0] == limits[1] or (  # limits could be a number or None
            all(val is not None for val in limits) and limits[1] < limits[0]
        ):
            self.logger.info("Invalid configuration for limits, defaulting to -/+inf")
            self.set_attribute((ATTR_POSITION, MIN), -np.inf)
            self.set_attribute((ATTR_POSITION, MAX), np.inf)
            self.set_value(ATTR_POSITION_LOWER_LIMIT, -np.inf)
            self.set_value(ATTR_POSITION_UPPER_LIMIT, np.inf)

    def _update_configured_limits(self, _):
        """
        Callback which updates ATTR_CONFIGURED_LIMITS.

        Another callback is attached to ATTR_CONFIGURED_LIMITS, which allows to check
        if limits are compatible with each other.
        """
        lower_limit = self.get_value(ATTR_POSITION_LOWER_LIMIT, VALUE)
        upper_limit = self.get_value(ATTR_POSITION_UPPER_LIMIT, VALUE)
        self.set_value(ATTR_CONFIGURED_LIMITS, [lower_limit, upper_limit])

    def _check_move_mode(self, value):
        """
        Check the compatibility of the configured move mode with mode method.

        It is important to check the value of ATTR_MOVE_MODE here, because if the user
        uses the controller to move the stage, the device switches to 'Relative' move
        mode without Kamzik knowing it.
        """
        if self.get_value(ATTR_MOVE_METHOD) == OPEN_LOOP and value != "Step":
            self.set_value(ATTR_MOVE_MODE, "Step")
        if self.get_value(ATTR_MOVE_METHOD) == CLOSE_LOOP and value != "Absolute":
            self.set_value(ATTR_MOVE_MODE, "Absolute")

    def config_attributes(self):
        """
        Check the attributes configuration.

        The base resolution is by default not writable with the MCS2 controller.
        Therefore the measured position will always be in the default unit (pm or ndeg).
        One must prevent the user to define a wrong resolution in the config, since this
        would not apply to the device.
        """
        if ("Position", "Unit") in self.config["attributes"]:
            self.logger.info(
                "Ignoring '[ Position, Unit ]: "
                f"{self.config['attributes'][('Position', 'Unit')]}' from config file"
            )
            del self.config["attributes"][("Position", "Unit")]

        self._config_attributes()

    def handle_configuration(self):
        if self.configured:
            return
        self.attach_attribute_callback(
            ATTR_POSITION_LOWER_LIMIT,
            callback=self._update_configured_limits,
            key_filter=VALUE,
        )
        self.attach_attribute_callback(
            ATTR_POSITION_UPPER_LIMIT,
            callback=self._update_configured_limits,
            key_filter=VALUE,
        )
        self.attach_attribute_callback(
            ATTR_MOVE_MODE,
            callback=self._check_move_mode,
            key_filter=VALUE,
        )

        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self.config_attributes()
            self.configured = True
            self.start_polling()
            self.set_status(STATUS_CONFIGURED)
            self.logger.info(
                "Device configuration took {} sec.".format(time.time() - start_at)
            )

        self.connected = True
        self.get_sensor_mode()
        self.get_encoder_unit()
        self.get_position_limit_range()
        self.get_positioner_configuration()
        self.get_step_frequency()
        self.get_step_amplitude()
        self.get_acceleration()
        self.get_velocity()
        self.get_move_mode()
        self.get_holding_time()
        self.get_reference_direction()
        self.command(
            ":CHAN{}:SDIR?\r\n".format(self.channel), callback=_finish_configuration
        )

    def start_polling(self):
        super().start_polling()
        self.poll_command(":CHAN{}:STAT?\r\n".format(self.channel), 250)
        self.poll_command(":CHAN{}:MMOD?\r\n".format(self.channel), 1000)
        self.poll_command(":CHAN{}:POS:CURR?\r\n".format(self.channel), 250)
        self.poll_command(":CHAN{}:POS:TARG?\r\n".format(self.channel), 250)
        self.poll_command(":CHAN{}:TEMP?\r\n".format(self.channel), 10000)

    def stop_polling(self):
        self.remove_poll_command(":CHAN{}:STAT?\r\n".format(self.channel), 250)
        self.remove_poll_command(":CHAN{}:MMOD?\r\n".format(self.channel), 1000)
        self.remove_poll_command(":CHAN{}:POS:CURR?\r\n".format(self.channel), 250)
        self.remove_poll_command(":CHAN{}:POS:TARG?\r\n".format(self.channel), 250)
        self.remove_poll_command(":CHAN{}:TEMP?\r\n".format(self.channel), 10000)

    def subject_update(self, key, value, subject):
        super().subject_update(key, value, subject)

        if self.connected and isinstance(key, tuple) and key[0] == self.channel:
            attribute = key[1]

            if attribute == ATTR_STATE and self.get_value(ATTR_STATE) != value:
                if self.get_value(ATTR_SENSOR_PRESENT) != bool(value & 0x0020):
                    if bool(value & 0x0020):
                        self.poll_command(
                            ":CHAN{}:POS:CURR?\r\n".format(self.channel), 250
                        )
                        self.poll_command(
                            ":CHAN{}:POS:TARG?\r\n".format(self.channel), 250
                        )
                    else:
                        self.remove_poll_command(
                            ":CHAN{}:POS:CURR?\r\n".format(self.channel), 250
                        )
                        self.remove_poll_command(
                            ":CHAN{}:POS:TARG?\r\n".format(self.channel), 250
                        )

                self.set_offsetted_value(ATTR_MOVING, bool(value & 0x0001))
                self.set_offsetted_value(ATTR_CLOSED_LOOP_ACTIVE, bool(value & 0x0002))
                self.set_offsetted_value(ATTR_CALIBRATING, bool(value & 0x0004))
                self.set_offsetted_value(ATTR_REFERENCING, bool(value & 0x0008))
                self.set_offsetted_value(ATTR_MOVE_DELAYED, bool(value & 0x0100))
                self.set_offsetted_value(ATTR_SENSOR_PRESENT, bool(value & 0x0020))
                self.set_offsetted_value(ATTR_CALIBRATED, bool(value & 0x0040))
                self.set_offsetted_value(ATTR_REFERENCED, bool(value & 0x0080))
                self.set_offsetted_value(ATTR_END_STOP_REACHED, bool(value & 0x0100))
                self.set_offsetted_value(ATTR_RANGE_LIMIT_REACHED, bool(value & 0x0200))
                self.set_offsetted_value(
                    ATTR_FOLLOWING_LIMIT_REACHED, bool(value & 0x0400)
                )
                self.set_offsetted_value(ATTR_MOVEMENT_FAILED, bool(value & 0x0800))
                self.set_offsetted_value(ATTR_STREAMING, bool(value & 0x1000))
                self.set_offsetted_value(ATTR_OVER_TEMPERATURE, bool(value & 0x4000))
                self.set_offsetted_value(ATTR_INDEX_MARK, bool(value & 0x8000))

                holding = (
                    bool(value & 0x0004)
                    and bool(value & 0x0008)
                    and bool(value & 0x0008)
                    and bool(value & 0x0002)
                    and not bool(value & 0x0001)
                )
                self.set_offsetted_value(ATTR_HOLDING, holding)

                if bool(value & 0x0001):
                    self.set_status(STATUS_BUSY)
                else:
                    self.set_status(STATUS_IDLE)
            elif attribute == ATTR_SENSOR_MODE:
                if value == "Disabled":
                    self.remove_poll_command(
                        ":CHAN{}:POS:CURR?\r\n".format(self.channel), 250
                    )
                    self.remove_poll_command(
                        ":CHAN{}:POS:TARG?\r\n".format(self.channel), 250
                    )
                else:
                    self.poll_command(":CHAN{}:POS:CURR?\r\n".format(self.channel), 250)
                    self.poll_command(":CHAN{}:POS:TARG?\r\n".format(self.channel), 250)
            elif attribute == ATTR_ENCODER_BASE_UNIT:
                if value == 2:
                    value = "m"
                else:
                    value = "deg"
            elif attribute == ATTR_ENCODER_RESOLUTION:
                unit = self.get_value(ATTR_ENCODER_BASE_UNIT)
                prefix = {-12: "p", -9: "n", -6: "u", -3: "m"}
                base_position_unit = prefix.get(value, "") + unit

                self.set_attribute((ATTR_TARGET_POSITION, UNIT), base_position_unit)
                self.set_attribute(
                    (ATTR_POSITION_UPPER_LIMIT, UNIT), base_position_unit
                )
                self.set_attribute(
                    (ATTR_POSITION_LOWER_LIMIT, UNIT), base_position_unit
                )
                self.set_attribute(
                    (ATTR_ACCELERATION, UNIT), "{}/s".format(base_position_unit)
                )
                self.set_attribute(
                    (ATTR_VELOCITY, UNIT), "{}/s".format(base_position_unit)
                )
                self.set_attribute((ATTR_POSITION, UNIT), base_position_unit)
            elif attribute == ATTR_POSITION_LOWER_LIMIT:
                self.set_attribute((ATTR_POSITION, MIN), value)
            elif attribute == ATTR_POSITION_UPPER_LIMIT:
                self.set_attribute((ATTR_POSITION, MAX), value)
            self.set_value(ATTR_LATENCY, self.device.get_value(ATTR_LATENCY))
            self.set_offsetted_value(attribute, value)

    def enable_close_loop(self):
        if self.position_attribute_copy is not None:
            self.set_attribute(
                (ATTR_POSITION, UNIT), self.position_attribute_copy[UNIT]
            )
            self.set_attribute(
                (ATTR_POSITION, OFFSET), self.position_attribute_copy[OFFSET]
            )
            self.set_attribute(
                (ATTR_POSITION, FACTOR), self.position_attribute_copy[FACTOR]
            )
            self.set_value(ATTR_MOVE_MODE, "Absolute")
            self[ATTR_POSITION].set_function = self._move_absolute
            self.position_attribute_copy = None

            # self.poll_command(":CHAN{}:POS:CURR?\r\n".format(self.channel), 250)
            # self.poll_command(":CHAN{}:POS:TARG?\r\n".format(self.channel), 250)

    def enable_open_loop(self):
        self.position_attribute_copy = self[ATTR_POSITION].attribute_copy()
        default_unit = self.get_value(ATTR_CLOSE_LOOP_UNIT)

        self.set_attribute(
            (ATTR_POSITION, UNIT),
            default_unit
            if default_unit is not None
            else self.position_attribute_copy[UNIT],
        )
        self.set_attribute((ATTR_POSITION, OFFSET), 0)
        self.set_attribute((ATTR_POSITION, FACTOR), 1)

        if self.get_value(ATTR_POSITION) is None:
            self.set_offsetted_value(ATTR_POSITION, 0)
        self[ATTR_POSITION].set_function = self._move_steps
        self.set_value(ATTR_MOVE_MODE, "Step")

        # self.remove_poll_command(":CHAN{}:POS:CURR?\r\n".format(self.channel), 250)
        # self.remove_poll_command(":CHAN{}:POS:TARG?\r\n".format(self.channel), 250)

    def set_move_method(self, value):
        if value == OPEN_LOOP:
            self.enable_open_loop()
        elif value == CLOSE_LOOP:
            self.enable_close_loop()

    @expose_method()
    def stop(self, callback=None):
        self.logger.info("Stop movement")
        return self.command(
            ":STOP{}\r\n".format(self.channel), callback, with_token=True
        )

    @expose_method()
    def calibrate(self, callback=None):
        self.logger.info("Calibrate")
        return self.command(
            ":CAL{}\r\n".format(self.channel), callback, with_token=True
        )

    @expose_method()
    def find_reference(self, callback=None):
        self.logger.info("Reference")
        return self.command(
            ":REF{}\r\n".format(self.channel), callback, with_token=True
        )

    @expose_method({"step": ATTR_POSITION})
    def move_relative(self, step):
        """Move the stage relatively to the current position."""
        try:
            step = device_units(self, ATTR_POSITION, step).m
            self.logger.info("Move by relative position {}".format(step))
            if self.get_value(ATTR_MOVE_MODE) == "Absolute":
                # add the step to the non-offsetted current position
                step = self.get_raw_value(ATTR_POSITION) + step
            return self.set_value(ATTR_TARGET_POSITION, step)
        except (UndefinedUnitError, ValueError) as e:
            self.logger.exception(e)
            raise DeviceUnitError(e)

    @expose_method({"position": ATTR_POSITION})
    def move_absolute(self, position):
        """
        Move the stage to the defined absolute position.

        The position from the GUI includes the offset, which needs to be subtracted
        before calling _move_absolute (which sends the command to the device).
        """
        try:
            position = device_units(self, ATTR_POSITION, position).m
            unit = self.get_value(ATTR_POSITION, key=UNIT)
            self.logger.info(
                "Move to position including offset {} {}".format(position, unit)
            )
            position = position - self.get_value(ATTR_POSITION, key=OFFSET)
            return self.set_value(ATTR_TARGET_POSITION, position)
        except (UndefinedUnitError, ValueError) as e:
            self.logger.exception(e)
            raise DeviceUnitError(e)

    def _move_absolute(self, value, callback=None):
        """
        Move in absolute position of the device.

        :param value: physical position = GUI_position/factor - offset
        """
        if self.get_value(ATTR_POSITION) is not None:
            self.logger.info("Move to absolute position {}".format(value))
            token = self.command(
                ":MOVE{} {}\r\n".format(self.channel, value), callback, with_token=True
            )
            return token
        return None

    def _move_steps(self, steps: float, callback: Optional[Callable] = None) -> int:
        """
        Callback method for open loop control.

        The amplitude of the movement is unitless, in steps. The n_factor and p_factor
        are user-friendly conversion factors corresponding to the estimated number of
        steps per degree or per millimeter (in the positive and negative directions).

        :param steps: number of steps to move, expressed in the unit of ATTR_POSITION
        :param callback: optional callback
        :return: the token
        """
        if self.get_value(ATTR_MOVE_MODE) != "Step":
            self.set_value(ATTR_MOVE_MODE, "Step")

        # convert steps to the user-friendly unit deg or mm
        unit = self.get_value(ATTR_POSITION, UNIT)
        if unit in {"mdeg", "udeg", "ndeg", "pdeg"}:
            steps = units.Quantity(steps, unit).to("deg").m
        if unit in {"m", "um", "nm", "pm"}:
            steps = units.Quantity(steps, unit).to("mm").m

        n_factor, p_factor = self.get_value(ATTR_OPEN_LOOP_FACTOR)
        factor = n_factor if steps < 0 else p_factor
        steps = int(np.rint(steps * factor))
        if steps == 0:
            self.logger.info(
                f"Move by {steps} steps: minimum angular step = {1/factor:.3f} deg"
            )
        else:
            self.logger.info(f"Move by {steps} steps")
        token = self.command(
            ":MOVE{} {}\r\n".format(self.channel, steps), callback, with_token=True
        )
        return int(token)

    @expose_method({"position": "New position"})
    def set_position(self, position=0):
        self.logger.info(f"Reset position to {position}")
        position = int(position)
        self.command(f":CHAN{self.channel}:POS {position}\r\n")

    def get_encoder_unit(self):
        self.command(":CHAN{}:TUN:BASE:UNIT?\r\n".format(self.channel))
        self.command(":CHAN{}:TUN:BASE:RES?\r\n".format(self.channel))

    def get_position_limit_range(self):
        self.command(":CHAN{}:RLIM:MAX?\r\n".format(self.channel))
        self.command(":CHAN{}:RLIM:MIN?\r\n".format(self.channel))

    def get_positioner_configuration(self):
        self.command(":CHAN{}:PTYP:NAME?\r\n".format(self.channel))
        self.command(":CHAN{}:PTYP:CODE?\r\n".format(self.channel))

    def get_step_frequency(self):
        self.command(":CHAN{}:STEP:FREQ?\r\n".format(self.channel))

    def get_step_amplitude(self):
        self.command(":CHAN{}:STEP:AMPL?\r\n".format(self.channel))

    def get_velocity(self):
        self.command(":CHAN{}:VEL?\r\n".format(self.channel))

    def get_acceleration(self):
        self.command(":CHAN{}:ACC?\r\n".format(self.channel))

    def get_sensor_mode(self):
        self.command(":CHAN{}:SENS:MODE?\r\n".format(self.channel))

    def get_move_mode(self):
        return self.command(":CHAN{}:MMOD?\r\n".format(self.channel))

    def get_safe_direction(self):
        self.command(":CHAN{}:SDIR?\r\n".format(self.channel))

    def get_reference_direction(self):
        self.command(":CHAN{}:REF:OPT?\r\n".format(self.channel))

    def get_holding_time(self):
        self.command(":CHAN{}:HOLD?\r\n".format(self.channel))

    def set_holding_time(self, value, callback=None):
        self.logger.info("Set holding time to {}".format(value))
        return self.command(
            ":CHAN{}:HOLD {}\r\n".format(self.channel, int(value)),
            callback,
            with_token=True,
        )

    # callback is unused, but I'm not sure if I can just disable it
    # or if it's still used dynamically
    # pylint: disable=unused-argument
    def set_upper_position_limit(self, value, callback=None):
        unit = self.get_value(ATTR_POSITION_UPPER_LIMIT, key=UNIT)
        try:
            set_value = device_units(self, ATTR_POSITION, units.Quantity(value, unit)).m
        except UndefinedUnitError:
            set_value = value
        self.logger.info("Set upper limit to {} {}".format(set_value, unit))
        self.set_attribute([ATTR_POSITION, MAX], set_value)

    # callback is unused, but I'm not sure if I can just disable it
    # or if it's still used dynamically
    # pylint: disable=unused-argument
    def set_lower_position_limit(self, value, callback=None):
        unit = self.get_value(ATTR_POSITION_LOWER_LIMIT, key=UNIT)
        try:
            set_value = device_units(self, ATTR_POSITION, units.Quantity(value, unit)).m
        except UndefinedUnitError:
            set_value = value
        self.logger.info("Set lower limit to {} {}".format(set_value, unit))
        self.set_attribute([ATTR_POSITION, MIN], set_value)

    def set_positioner_code(self, value, callback=None):
        self.logger.info("Set positioner  code to {}".format(value))
        token = self.command(
            ":CHAN{}:PTYP:CODE {}\r\n".format(self.channel, int(value)),
            callback,
            with_token=True,
        )
        self.get_positioner_configuration()
        self.get_encoder_unit()
        return token

    def set_step_frequency(self, value, callback=None):
        self.logger.info("Set step frequency to {} Hz".format(value))
        self.command(
            ":CHAN{}:MCLF:CURR {}\r\n".format(self.channel, int(value)),
            callback,
            with_token=True,
        )
        return self.command(
            ":CHAN{}:STEP:FREQ {}\r\n".format(self.channel, int(value)),
            callback,
            with_token=True,
        )

    def set_step_amplitude(self, value, callback=None):
        self.logger.info("Set step amplitude to {}".format(value))
        return self.command(
            ":CHAN{}:STEP:AMPL {}\r\n".format(self.channel, int(value)),
            callback,
            with_token=True,
        )

    def set_velocity(self, value, callback=None):
        self.logger.info("Set velocity to {}".format(value))
        return self.command(
            ":CHAN{}:VEL {}\r\n".format(self.channel, int(value)),
            callback,
            with_token=True,
        )

    def set_acceleration(self, value, callback=None):
        self.logger.info("Set acceleration to {}".format(value))
        return self.command(
            ":CHAN{}:ACC {}\r\n".format(self.channel, int(value)),
            callback,
            with_token=True,
        )

    def set_sensor_mode(self, value, callback=None):
        self.logger.info("Set sensor mode to {}".format(value))
        value = self.sensor_modes[value]
        out = self.command(
            ":CHAN{}:SENS:MODE {}\r\n".format(self.channel, value),
            callback,
            with_token=True,
        )
        self.get_sensor_mode()
        return out

    def set_move_mode(self, value, callback=None):
        self.logger.info("Set move mode to {}".format(value))
        if value == "Step":
            self.set_value(ATTR_MOVE_METHOD, OPEN_LOOP)
        else:
            self.set_value(ATTR_MOVE_METHOD, CLOSE_LOOP)

        value = self.move_modes[value]
        return self.command(
            ":CHAN{}:MMOD {}\r\n".format(self.channel, value), callback, with_token=True
        )

    def set_safe_direction(self, value, callback=None):
        self.logger.info("Set safe direction to {}".format(value))
        value = self.safe_direction_modes[value]
        return self.command(
            ":CHAN{}:SDIR {}\r\n".format(self.channel, value), callback, with_token=True
        )

    def set_reference_direction(self, value, callback=None):
        self.logger.info("Set reference direction to {}".format(value))
        value = self.safe_direction_modes[value]
        return self.command(
            ":CHAN{}:REF:OPT {}\r\n".format(self.channel, value),
            callback,
            with_token=True,
        )

    # callback is unused, but I'm not sure if I can just disable it
    # or if it's still used dynamically
    # pylint: disable=unused-argument
    @expose_method()
    def enable_holding(self, callback=None):
        """
        Here comes a short description of enable_holding.

        :param callback:
        """
        # enable holding
        self.set_value(ATTR_HOLDING_TIME, -1)
        # move by 0 to end holding
        self.set_value(ATTR_MOVE_MODE, "Relative")
        self.move_relative(device_units(self, ATTR_POSITION, 0))
        self.set_value(ATTR_MOVE_MODE, "Absolute")

    # callback is unused, but I'm not sure if I can just disable it
    # or if it's still used dynamically
    # pylint: disable=unused-argument
    @expose_method()
    def disable_holding(self, callback=None):
        """
        Here comes a short description of disable_holding.

        :param callback:
        """
        # disable holding
        self.set_value(ATTR_HOLDING_TIME, 0)
        # move by 0 to end holding
        self.set_value(ATTR_MOVE_MODE, "Relative")
        self.move_relative(device_units(self, ATTR_POSITION, 0))
        self.set_value(ATTR_MOVE_MODE, "Absolute")
