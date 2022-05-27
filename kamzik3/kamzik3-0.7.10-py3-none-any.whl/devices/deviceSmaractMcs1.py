""" Example of yaml configuration
Smaract0: &Smaract0 !Device:kamzik3.devices.deviceSmaractMcs1.DeviceSmaractMcs1
    device_id: Smaract0
    host: 192.168.83.91
Smaract0_axis_0: &Smaract0_axis_0 !Device:kamzik3.devices.deviceSmaractMcs1.DeviceSmaractMcs1Channel
    device: *Smaract0
    channel: 0
    device_id: MotorAxis0
    config:
      attributes:
        !!python/tuple [Sensor type, Value]: 1
        !!python/tuple [Position +limit, Value]: 15mm
        !!python/tuple [Position -limit, Value]: -15mm
        !!python/tuple [Position, Tolerance]: [10nm, 10nm]
"""
import re
import time

import numpy as np
import serial
from bidict import frozenbidict
from pint.errors import UndefinedUnitError

import kamzik3
from kamzik3 import DeviceUnitError
from kamzik3.constants import *
from kamzik3.devices.deviceChannel import DeviceChannel
from kamzik3.devices.devicePort import DevicePort
from kamzik3.devices.deviceSocket import DeviceSocket
from kamzik3.snippets.snippetsDecorators import expose_method
from kamzik3.snippets.snippetsUnits import device_units

from kamzik3.constants import PREVIOUS


class DeviceSmaractMcs1(DeviceSocket):
    # push_buffer_size = 50
    response_timeout = 3000
    push_commands_max = 1
    terminator = b"\n"
    handtool_modes = frozenbidict({"Disabled": 0, "Enabled": 1, "Display only": 2})
    sensor_modes = frozenbidict({"Disabled": 0, "Enabled": 1, "Power safe": 2})
    channel_command_pattern = re.compile(":([A-Z]+)([-0-9]+),(.*)")
    linear_sensor_type = [None, 1, 5, 6, 9, 18, 21, 24, 32, 38, 40, 41, 42, 43, 44]
    sensor_types = [
        1,
        2,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        23,
        24,
        32,
        37,
        38,
        39,
        40,
        41,
        42,
        43,
        44,
        48,
        49,
        50,
        51,
        53,
        54,
    ]
    safe_direction_modes = frozenbidict({"Forward": 0, "Backward": 1})

    def __init__(self, host, port=5000, device_id=None, config=None):
        super().__init__(host, port, device_id, config)

    def _init_attributes(self):
        super()._init_attributes()
        self.create_attribute(ATTR_STATE, readonly=True, default_type=np.uint16)
        self.create_attribute(ATTR_SERIAL_NUMBER, readonly=True)
        self.create_attribute(ATTR_CHANNELS, readonly=True, default_type=np.uint16)
        self.create_attribute(
            ATTR_HAND_TOOL_MODE, readonly=True, default_type=np.uint16
        )
        self.create_attribute(
            ATTR_HAND_TOOL_MODE,
            default_value="Display only",
            default_type=self.handtool_modes.keys(),
            set_function=self.set_hand_tool_mode,
        )
        self.create_attribute(
            ATTR_SENSOR_MODE,
            default_type=self.sensor_modes.keys(),
            set_function=self.set_sensor_mode,
        )
        self.create_attribute(
            ATTR_SENSOR_PRESENT, default_value=True, readonly=True, default_type=np.bool
        )

    def valid_command_format(self, command):
        return command is not None and command[-1] == "\n"

    def handle_configuration(self):
        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()
            self.set_status(STATUS_CONFIGURED)
            self.logger.info(
                "Device configuration took {} sec.".format(time.time() - start_at)
            )

        # Set communication to synchronous
        self.command(":SCM0\n")
        # Set hand-tool mode to just display positions
        self.set_hand_tool_mode("Display only")
        # Get Interface version
        self.command(":GSI\n")
        # Get number of channels
        self.command(":GNC\n")
        # Get Interface version
        self.command(":GSE\n", callback=_finish_configuration)

    def handle_readout(self, readout_buffer):
        command, output, callback, token = super().handle_readout(readout_buffer)

        if output[:2] == ":E":
            channel, error_number = [int(v) for v in output[2:].split(",")]
            if error_number > 0:
                if error_number == 129:
                    self.notify((channel, ATTR_SENSOR_MODE), "Disabled")
                    self.notify((channel, ATTR_SENSOR_PRESENT), False)
                # elif error_number == 140:
                #     self.set_offsetted_value(ATTR_SENSOR_MODE, "Disabled")
                #     for channel in range(self[ATTR_CHANNELS][VALUE]):
                #         self.notify((channel, ATTR_SENSOR_MODE), "Disabled")
                self.handle_command_error(command, output)
        elif command == ":GSI\n":
            self.set_offsetted_value(ATTR_SERIAL_NUMBER, output.strip(":IN"))
        elif command == ":GNC\n":
            channels = int(output.strip(":N"))
            self.set_offsetted_value(ATTR_CHANNELS, channels)
        elif command == ":GSE\n":
            mode = self.sensor_modes.inv[int(output.strip(":SE"))]
            self.set_offsetted_value(ATTR_SENSOR_MODE, mode)
            for channel in range(self[ATTR_CHANNELS][VALUE]):
                self.notify((channel, ATTR_SENSOR_MODE), mode)
        elif output[:3] == ":BR":
            pass
        else:
            find = self.channel_command_pattern.search(output)
            if find is not None and find != -1:
                attribute = None
                cmd, channel, value = find.group(1), int(find.group(2)), find.group(3)
                if cmd == "S":
                    attribute, value = ATTR_STATE, int(value)
                elif cmd == "P":
                    attribute, value = ATTR_POSITION, int(value)
                elif cmd == "A":
                    position, revolutions = value.split(",")
                    self.notify((channel, ATTR_REVOLUTIONS), int(revolutions))
                    attribute, value = ATTR_POSITION, int(position)
                elif cmd == "ST":
                    attribute, value = ATTR_SENSOR_TYPE, int(value)
                elif cmd == "PPK":
                    attribute, value = ATTR_REFERENCED, bool(int(value))
                elif cmd == "SD":
                    safe_direction = self.safe_direction_modes.inv[int(value)]
                    attribute, value = ATTR_SAFE_DIRECTION, safe_direction
                elif cmd == "CLA":
                    attribute, value = ATTR_ACCELERATION, int(value)
                elif cmd == "CLS":
                    attribute, value = ATTR_VELOCITY, int(value)
                elif cmd == "AL":
                    min_position, min_revolution, max_position, max_revolution = [
                        int(i) for i in value.split(",")
                    ]
                    attribute, value = ATTR_POSITION_LOWER_LIMIT, (
                        min_position,
                        min_revolution,
                    )
                    self.notify(
                        (channel, ATTR_POSITION_UPPER_LIMIT),
                        (max_position, max_revolution),
                    )
                elif cmd == "PL":
                    min_position, max_position = value.split(",")
                    min_position, max_position = int(min_position), int(max_position)
                    attribute, value = ATTR_POSITION_LOWER_LIMIT, int(min_position)
                    self.notify((channel, ATTR_POSITION_UPPER_LIMIT), int(max_position))
                if attribute:
                    self.notify((channel, attribute), value)

        if callback is not None:
            self.handle_readout_callback(callback, command, readout_buffer)
        if token:
            kamzik3.session.publisher.push_message(
                self.device_id, [command, readout_buffer], token
            )
            for observer in self._observers[:]:
                if isinstance(observer, DeviceSmaractMcs1Channel):
                    kamzik3.session.publisher.push_message(
                        observer.device_id, [command, readout_buffer], token
                    )

    def set_hand_tool_mode(self, value):
        self.logger.info("Set hand tool mode to {}".format(value))
        int_mode = self.handtool_modes[value]
        self.command(":SHE{}\n".format(int_mode))

    def set_sensor_mode(self, value):
        self.logger.info("Set sensor mode to {}".format(value))
        for channel in range(self[ATTR_CHANNELS][VALUE]):
            self.notify((channel, ATTR_SENSOR_MODE), value)

        value = self.sensor_modes[value]
        self.command(":SSE{}\n".format(value))


# abstract methods `collect_incoming_data` and `found_terminator` are defined in
# DeviceSocket (one of the base classes of DeviceSmaractMcs1). Since multiple
# inheritance is used here we better disable the pylint warning.
# pylint: disable=abstract-method
# see https://github.com/python/mypy/issues/9319 for mypy error
class DeviceSmaractMcs1Port(DevicePort, DeviceSmaractMcs1):  # type: ignore
    push_buffer_size = DeviceSmaractMcs1.push_buffer_size
    response_timeout = DeviceSmaractMcs1.response_timeout
    terminator = DeviceSmaractMcs1.terminator

    def __init__(
        self,
        port,
        baud_rate=9600,
        parity=serial.PARITY_NONE,
        stop_bits=serial.STOPBITS_ONE,
        byte_size=serial.EIGHTBITS,
        device_id=None,
        config=None,
    ):
        super().__init__(
            port, baud_rate, parity, stop_bits, byte_size, device_id, config
        )

    def _init_attributes(self):
        super()._init_attributes()
        self.create_attribute(
            ATTR_BAUDRATE,
            default_value=self.baud_rate,
            readonly=False,
            default_type=self.BAUDRATES,
            set_function=self.set_baudrate,
        )

    def handshake(self):
        self.logger.info("Handshake initiated")
        self.push(b":SCM0\n")
        time.sleep(0.05)  # Give some time for devices to reply
        if self.serial_port.in_waiting != 0:
            if self.read_all().strip() == ":E-1,0":
                return True
        return False

    def set_baudrate(self, value):
        self.logger.info("Set baud-rate to {}".format(value))
        self.command(":CB{}\n".format(int(value)))


class DeviceSmaractMcs1Channel(DeviceChannel):
    sensor_types = DeviceSmaractMcs1.sensor_types
    linear_sensor_type = DeviceSmaractMcs1.linear_sensor_type
    sensor_modes = DeviceSmaractMcs1.sensor_modes
    safe_direction_modes = DeviceSmaractMcs1.safe_direction_modes

    def _init_attributes(self):
        super()._init_attributes()
        self.create_attribute(ATTR_STATE, readonly=True, default_type=np.uint16)
        self.create_attribute(ATTR_MOVING, readonly=True, default_type=np.bool)
        self.create_attribute(
            ATTR_POSITION,
            default_type=np.int64,
            set_function=self._move_absolute,
            set_value_when_set_function=False,
        )
        self.create_attribute(ATTR_REVOLUTIONS, readonly=True, default_type=np.int64)
        self.create_attribute(ATTR_CALIBRATING, readonly=True, default_type=np.bool)
        self.create_attribute(ATTR_REFERENCING, readonly=True, default_type=np.bool)
        self.create_attribute(ATTR_CALIBRATED, readonly=True, default_type=np.bool)
        self.create_attribute(ATTR_REFERENCED, readonly=True, default_type=np.bool)
        self.create_attribute(ATTR_MOVEMENT_LOCKED, readonly=True, default_type=np.bool)
        self.create_attribute(
            ATTR_SENSOR_MODE,
            default_value=self.device.get_value(ATTR_SENSOR_MODE),
            readonly=True,
            default_type=self.sensor_modes.keys(),
        )
        self.create_attribute(
            ATTR_SENSOR_TYPE,
            default_type=self.sensor_types,
            set_function=self.set_sensor_type,
        )
        self.create_attribute(ATTR_SENSOR_PRESENT, readonly=True, default_type=np.bool)
        self.create_attribute(ATTR_ENCODER_BASE_UNIT, readonly=True)
        self.create_attribute(
            ATTR_ENCODER_RESOLUTION, readonly=True, default_type=np.int8
        )
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
            ATTR_STEP_FREQUENCY,
            default_value=1000,
            default_type=np.uint32,
            min_value=1,
            max_value=18.5e3,
            unit="Hz",
            set_function=self.set_step_frequency,
        )
        self.create_attribute(
            ATTR_STEP_AMPLITUDE,
            default_value=1000,
            default_type=np.uint32,
            min_value=1,
            max_value=4095,
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
            max_value=1e8,
            set_function=self.set_velocity,
        )
        self.create_attribute(
            ATTR_SAFE_DIRECTION,
            default_type=self.safe_direction_modes.keys(),
            set_function=self.set_safe_direction,
        )
        self.create_attribute(
            ATTR_HOLDING_TIME,
            default_value=0,
            default_type=np.uint16,
            min_value=0,
            max_value=60e3,
            unit="ms",
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

    def handle_configuration(self):
        if self.configured:
            return

        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()
            self.set_value(ATTR_SENSOR_MODE, self.device.get_value(ATTR_SENSOR_MODE))
            self.set_value(
                ATTR_SENSOR_PRESENT, self.device.get_value(ATTR_SENSOR_PRESENT)
            )
            self.get_position_limit_range()
            self.start_polling()
            self.configured = True
            self.set_status(STATUS_CONFIGURED)
            self.logger.info(
                "Device configuration took {} sec.".format(time.time() - start_at)
            )

        self.connected = True
        self.get_sensor_type()
        self.get_acceleration()
        self.get_safe_direction()
        self.command(":GCLS{}\n".format(self.channel), callback=_finish_configuration)

    def subject_update(self, key, value, subject):
        super().subject_update(key, value, subject)
        if self.connected and isinstance(key, tuple) and key[0] == self.channel:
            attribute = key[1]
            if attribute == ATTR_STATE and self.get_value(ATTR_STATE) != value:
                if value in (0, 3):
                    self.set_status(STATUS_IDLE)
                    self.set_value(ATTR_CALIBRATING, False)
                    self.set_value(ATTR_REFERENCING, False)
                    self.set_value(ATTR_MOVING, False)
                else:
                    self.set_status(STATUS_BUSY)
                    if value in (1, 2, 4, 6, 7):
                        self.set_value(ATTR_MOVING, True)

                        if value == 6:
                            self.set_value(ATTR_CALIBRATING, True)
                        elif value == 7:
                            self.set_value(ATTR_REFERENCING, True)
                        elif value == 9:
                            self.set_value(ATTR_MOVEMENT_LOCKED, True)
            elif attribute == ATTR_SENSOR_TYPE:
                self._set_position_unit(value)
                self._set_position_polling(value)
                self.get_referenced()
                self.get_position_limit_range(value)
            elif attribute == ATTR_SENSOR_PRESENT:
                if not value:
                    self.remove_poll_command(":GP{}\n".format(self.channel), 250)
                    self.remove_poll_command(":GA{}\n".format(self.channel), 250)
                else:
                    self._set_position_polling(self[ATTR_SENSOR_TYPE][VALUE])
            elif attribute == ATTR_SENSOR_MODE:
                if value == "Disabled":
                    self.remove_poll_command(":GP{}\n".format(self.channel), 250)
                    self.remove_poll_command(":GA{}\n".format(self.channel), 250)
                else:
                    self._set_position_polling(self[ATTR_SENSOR_TYPE][VALUE])
            elif attribute == ATTR_POSITION and self[ATTR_REVOLUTIONS][VALUE] != 0:
                revolution = 360 * 10 ** abs(self[ATTR_ENCODER_RESOLUTION][VALUE])
                value += self[ATTR_REVOLUTIONS][VALUE] * revolution
            elif (
                attribute == ATTR_POSITION_LOWER_LIMIT
                and self[ATTR_SENSOR_TYPE][VALUE] not in self.linear_sensor_type
            ):
                revolution = 360 * 10 ** abs(self[ATTR_ENCODER_RESOLUTION][VALUE])
                min_position, min_revolutions = value
                value = min_position + min_revolutions * revolution
                # self.set_attribute([ATTR_POSITION, MIN], value)
            elif (
                attribute == ATTR_POSITION_UPPER_LIMIT
                and self[ATTR_SENSOR_TYPE][VALUE] not in self.linear_sensor_type
            ):
                revolution = 360 * 10 ** abs(self[ATTR_ENCODER_RESOLUTION][VALUE])
                max_position, max_revolutions = value
                value = max_position + max_revolutions * revolution
                # self.set_attribute([ATTR_POSITION, MAX], value)
            self.set_value(ATTR_LATENCY, self.device.get_value(ATTR_LATENCY))
            self.set_offsetted_value(attribute, value)

    def _set_position_unit(self, sensor_type):
        if sensor_type is None:
            return

        prefix = {-12: "p", -9: "n", -6: "u", -3: "m"}
        if sensor_type in self.linear_sensor_type:
            resolution = -9
            unit = "m"
        else:
            resolution = -6
            unit = "deg"
        base_position_unit = prefix.get(resolution, "") + unit
        self.set_attribute((ATTR_ENCODER_RESOLUTION, VALUE), resolution)
        self.set_attribute((ATTR_ENCODER_BASE_UNIT, VALUE), unit)
        self.set_attribute((ATTR_POSITION, UNIT), base_position_unit)
        self.set_attribute((ATTR_POSITION_UPPER_LIMIT, UNIT), base_position_unit)
        self.set_attribute((ATTR_POSITION_LOWER_LIMIT, UNIT), base_position_unit)
        self.set_attribute((ATTR_ACCELERATION, UNIT), "{}/s".format(base_position_unit))
        self.set_attribute((ATTR_VELOCITY, UNIT), "{}/s".format(base_position_unit))

    def _set_position_polling(self, sensor_type):
        if sensor_type is None:
            return
        elif sensor_type in self.linear_sensor_type:
            self.poll_command(":GP{}\n".format(self.channel), 250)
            self.set_value(ATTR_REVOLUTIONS, 0)
        else:
            self.poll_command(":GA{}\n".format(self.channel), 250)

    def start_polling(self):
        super().start_polling()
        self.poll_command(":GS{}\n".format(self.channel), 250)

    def stop_polling(self):
        self.remove_poll_command(":GS{}\n".format(self.channel), 250)
        self.remove_poll_command(":GP{}\n".format(self.channel), 250)
        self.remove_poll_command(":GA{}\n".format(self.channel), 250)

    def _move_absolute(self, value, callback=None):
        self.logger.info("Move to position {}".format(value))
        holding_time = self.get_value(ATTR_HOLDING_TIME)
        if self[ATTR_SENSOR_TYPE][VALUE] in self.linear_sensor_type:
            return self.command(
                ":MPA{},{},{}\n".format(self.channel, int(value), holding_time),
                callback,
                with_token=True,
            )
        else:
            revolution = 360 * 10 ** abs(self[ATTR_ENCODER_RESOLUTION][VALUE])
            revolutions = int(value // revolution)
            angular_position = int(value - revolutions * revolution)
            return self.command(
                ":MAA{},{},{},{}\n".format(
                    self.channel, angular_position, revolutions, holding_time
                ),
                callback,
                with_token=True,
            )

    def _move_relative(self, value, callback=None):
        self.logger.info("Move by relative position {}".format(value))
        holding_time = self.get_value(ATTR_HOLDING_TIME)
        if self[ATTR_SENSOR_TYPE][VALUE] in self.linear_sensor_type:
            return self.command(
                ":MPR{},{},{}\n".format(self.channel, int(value), holding_time),
                callback,
                with_token=True,
            )
        else:
            revolution = 360 * 10 ** abs(self[ATTR_ENCODER_RESOLUTION][VALUE])
            revolutions = int(value // revolution)
            angular_position = int(value - revolutions * revolution)
            return self.command(
                ":MAR{},{},{},{}\n".format(
                    self.channel, angular_position, revolutions, holding_time
                ),
                callback,
                with_token=True,
            )

    def _move_steps(self, steps, callback=None):
        """
        Callback method for open loop control.

        The amplitude of the movement is unitless, in steps. The n_factor and p_factor are user-friendly conversion
        factors corresponding to the estimated number of steps per degree or per millimeter (in the positive and
        negative directions).

        :param steps: number of steps to move, expressed in the unit of ATTR_POSITION
        :param callback: optional callback
        """
        # convert steps to the user-friendly unit deg or mm
        unit = self.get_value(ATTR_POSITION, UNIT)
        if unit in {"mdeg", "udeg", "ndeg", "pdeg"}:
            steps = kamzik3.units.Quantity(steps, unit).to("deg").m
        if unit in {"m", "um", "nm", "pm"}:
            steps = kamzik3.units.Quantity(steps, unit).to("mm").m

        n_factor, p_factor = self.get_value(ATTR_OPEN_LOOP_FACTOR)
        factor = n_factor if steps < 0 else p_factor
        steps = int(np.rint(steps * factor))
        if steps == 0:
            self.logger.info(
                f"Move by {steps} steps: minimum angular step = {1/factor:.3f} deg"
            )
        else:
            self.logger.info(f"Move by {steps} steps")
        return self.move_step(steps, callback=callback)

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

    def set_move_method(self, value):
        if value == OPEN_LOOP:
            self.enable_open_loop()
        elif value == CLOSE_LOOP:
            self.enable_close_loop()

    @expose_method()
    def stop(self, callback=None):
        self.logger.info("Stop movement")
        return self.command(":S{}\n".format(self.channel), callback, with_token=True)

    @expose_method()
    def calibrate(self, callback=None):
        self.logger.info("Calibrate")
        return self.command(":CS{}\n".format(self.channel), callback, with_token=True)

    @expose_method()
    def find_reference(self, callback=None):
        self.logger.info("Reference")
        reference_direction = self.safe_direction_modes[
            self.get_value(ATTR_SAFE_DIRECTION)
        ]
        return self.command(
            ":FRM{},{},0,1\n".format(self.channel, reference_direction),
            callback,
            with_token=True,
        )

    @expose_method({"position": ATTR_POSITION})
    def move_absolute(self, position):
        try:
            position = device_units(self, ATTR_POSITION, position)
            self.logger.info("Move to absolute position {}".format(position))
            return self.set_value(ATTR_POSITION, position)
        except (UndefinedUnitError, ValueError) as e:
            self.logger.exception(e)
            raise DeviceUnitError(e)

    @expose_method({"position": ATTR_POSITION})
    def move_relative(self, position):
        try:
            position = device_units(self, ATTR_POSITION, position)
            self.logger.info("Move by relative position {}".format(position))
            return self.set_value(ATTR_POSITION, self[ATTR_POSITION].value() + position)
        except (UndefinedUnitError, ValueError) as e:
            self.logger.exception(e)
            raise DeviceUnitError(e)

    @expose_method(
        {
            "steps": "Number of steps",
            "amplitude": ATTR_STEP_AMPLITUDE,
            "frequency": ATTR_STEP_FREQUENCY,
        }
    )
    def move_step(self, steps, amplitude=None, frequency=None, callback=None):
        if amplitude in (None, ""):
            amplitude = self[ATTR_STEP_AMPLITUDE][VALUE]
        else:
            amplitude = device_units(self, ATTR_STEP_AMPLITUDE, amplitude).m
        if frequency in (None, ""):
            frequency = self[ATTR_STEP_FREQUENCY][VALUE]
        else:
            frequency = device_units(self, ATTR_STEP_FREQUENCY, frequency).m
        amplitude = int(self[ATTR_STEP_AMPLITUDE].remove_offset_factor(amplitude))
        frequency = int(self[ATTR_STEP_FREQUENCY].remove_offset_factor(frequency))
        self.logger.info(
            "Move by {} steps with amplitude {} and frequency of {} Hz".format(
                int(steps), int(amplitude), int(frequency)
            )
        )
        return self.command(
            ":MST{},{},{},{}\n".format(self.channel, int(steps), amplitude, frequency),
            callback,
            with_token=True,
        )

    def get_sensor_type(self):
        self.command(":GST{}\n".format(self.channel))

    def get_position_limit_range(self, sensor_type=None):
        if sensor_type in self.linear_sensor_type:
            self.command(":GPL{}\n".format(self.channel))
        else:
            self.command(":GAL{}\n".format(self.channel))

    def get_velocity(self):
        self.command(":GCLS{}\n".format(self.channel))

    def get_acceleration(self):
        self.command(":GCLA{}\n".format(self.channel))

    def get_safe_direction(self):
        self.command(":GSD{}\n".format(self.channel))

    def get_referenced(self):
        self.command(":GPPK{}\n".format(self.channel))

    def set_sensor_type(self, value, callback=None):
        self.logger.info("Set sensor type to {}".format(value))
        if value != self.get_attribute([ATTR_SENSOR_TYPE, PREVIOUS]):
            self.remove_poll_command(":GP{}\n".format(self.channel), 250)
            self.remove_poll_command(":GA{}\n".format(self.channel), 250)
            print(":SST{},{}\n".format(self.channel, int(value)))
            token = self.command(
                ":SST{},{}\n".format(self.channel, int(value)),
                callback,
                with_token=True,
            )
            self.get_sensor_type()
            return token
        return None

    def set_lower_position_limit(self, value, callback=None):
        self.logger.info("Set lower position limit to {}".format(value))
        # upper_limit = self[ATTR_POSITION_UPPER_LIMIT][VALUE]
        upper_limit = self.get_raw_value(ATTR_POSITION_UPPER_LIMIT)
        # self.set_value(ATTR_POSITION_LOWER_LIMIT, int(value))
        if upper_limit is None:
            upper_limit = value
            # self.set_value(ATTR_POSITION_UPPER_LIMIT, upper_limit)
        if int(self[ATTR_SENSOR_TYPE][VALUE]) in self.linear_sensor_type:
            if value > upper_limit:
                value, upper_limit = upper_limit, value
            out = self.command(
                ":SPL{},{},{}\n".format(self.channel, int(value), int(upper_limit)),
                with_token=True,
            )
        else:
            revolution = 360 * 10 ** abs(self[ATTR_ENCODER_RESOLUTION][VALUE])
            min_revolutions = int(value // revolution)
            min_angular_position = int(value - min_revolutions * revolution)
            max_revolutions = int(upper_limit // revolution)
            max_angular_position = int(upper_limit - max_revolutions * revolution)
            out = self.command(
                ":SAL{},{},{},{},{}\n".format(
                    self.channel,
                    int(min_angular_position),
                    int(min_revolutions),
                    int(max_angular_position),
                    int(max_revolutions),
                ),
                callback,
                with_token=True,
            )

        self.set_value(ATTR_POSITION, value, key=MIN)
        self.get_position_limit_range()
        return out

    def set_upper_position_limit(self, value, callback=None):
        self.logger.info("Set upper position limit to {}".format(value))
        lower_limit = self.get_raw_value(
            ATTR_POSITION_LOWER_LIMIT
        )  # self[ATTR_POSITION_LOWER_LIMIT][VALUE]
        # self.set_value(ATTR_POSITION_UPPER_LIMIT, int(value))
        if lower_limit is None:
            lower_limit = value
            # self.set_value(ATTR_POSITION_LOWER_LIMIT, lower_limit)
        if int(self[ATTR_SENSOR_TYPE][VALUE]) in self.linear_sensor_type:
            if value < lower_limit:
                value, lower_limit = lower_limit, value
            out = self.command(
                ":SPL{},{},{}\n".format(self.channel, int(lower_limit), int(value)),
                callback,
                with_token=True,
            )
        else:
            revolution = 360 * 10 ** abs(self[ATTR_ENCODER_RESOLUTION][VALUE])
            max_revolutions = int(value // revolution)
            max_angular_position = int(value - max_revolutions * revolution)
            min_revolutions = int(lower_limit // revolution)
            min_angular_position = int(lower_limit - min_revolutions * revolution)
            out = self.command(
                ":SAL{},{},{},{},{}\n".format(
                    self.channel,
                    int(min_angular_position),
                    int(min_revolutions),
                    int(max_angular_position),
                    int(max_revolutions),
                ),
                callback,
                with_token=True,
            )

        self.set_value(ATTR_POSITION, value, key=MAX)
        self.get_position_limit_range()
        return out

    def set_step_frequency(self, value, callback=None):
        self.logger.info("Set step frequency to {} Hz".format(value))
        return self.command(
            ":SCLF{},{}\n".format(self.channel, int(value)), callback, with_token=True
        )

    def set_step_amplitude(self, value):
        self.logger.info("Set step amplitude to {}".format(value))
        self[ATTR_STEP_AMPLITUDE][VALUE] = value

    def set_velocity(self, value, callback=None):
        self.logger.info("Set velocity to {}".format(value))
        return self.command(
            ":SCLS{},{}\n".format(self.channel, int(value)), callback, with_token=True
        )

    def set_acceleration(self, value, callback=None):
        self.logger.info("Set acceleration to {}".format(value))
        return self.command(
            ":SCLA{},{}\n".format(self.channel, int(value)), callback, with_token=True
        )

    def set_safe_direction(self, value, callback=None):
        self.logger.info("Set safe direction to {}".format(value))
        value = self.safe_direction_modes[value]
        return self.command(
            ":SSD{},{}\n".format(self.channel, value), callback, with_token=True
        )
