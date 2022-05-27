""" Example of yaml configuration
Lexium0: &Lexium0 !Device:kamzik3.devices.deviceLexium.DeviceLexium
    device_id: Lexium0
    host: 192.168.83.60
Lexium0_axis_0: &Lexium0_axis_0 !Device:kamzik3.devices.deviceLexium.DeviceLexiumChannel
    device: *Lexium0
    channel: 0
    device_id: MotorAxis0
    config:
        attributes:
            !!python/tuple [Encoder enabled, Value]: 1
            !!python/tuple [Rotation direction, Value]: 0
            !!python/tuple [Use mark index, Value]: 0
            !!python/tuple [Position, Factor]: 2.0833e-6
            !!python/tuple [Position, Unit]: deg
            !!python/tuple [Position +limit, Factor]: 2.0833e-6
            !!python/tuple [Position +limit, Unit]: deg
            !!python/tuple [Position -limit, Factor]: 2.0833e-6
            !!python/tuple [Position -limit, Unit]: deg
            !!python/tuple [Backlash distance, Unit]: deg
            !!python/tuple [Backlash distance, Value]: 1 deg
            !!python/tuple [Maximum velocity, Value]: 80000
            !!python/tuple [Microstep resolution, Value]: 256
            !!python/tuple [Run current, Value]: 50%
            !!python/tuple [Stall factor, Value]: 30
            !!python/tuple [Position, Tolerance]: [0.1 deg, 0.1 deg]
"""
import re
import time
from threading import Thread, Event

import numpy as np
from pint.errors import UndefinedUnitError

import kamzik3
from kamzik3 import DeviceError, DeviceUnitError, units
from kamzik3.constants import *
from kamzik3.devices.deviceChannel import DeviceChannel
from kamzik3.devices.deviceSocket import DeviceSocket
from kamzik3.snippets.snippetsDecorators import expose_method
from kamzik3.snippets.snippetsUnits import device_units


class DeviceLexium(DeviceSocket):
    terminator = b">"
    response_timeout = 3000
    join_token = ',"~",'
    push_commands_max = 1
    error_description = {
        0: "No Error",
        1: "Over-current condition on output 1",
        2: "Over-current condition on output 2",
        6: "An I/O is already set to this type. Applies to non-General Purpose I/O",
        8: "Tried to SET IO to an incorrect I/O type",
        9: "Tried to write to I/O set as Input or is 'TYPED'",
        10: "Illegal I/O number",
        11: "Incorrect CLOCK type",
        12: "Input 1 not defined as a capture input",
        20: "Tried to set unknown variable or flag. Trying to set an undefined variable of flag. Also could be a typo.",
        21: "Tried to set an incorrect value. Many variables have a range such as the Run Current (RC) which is 1 to 100%. As an example, you cannot set the RC to 110%.",
        22: "VI is set greater than or equal to VM. The Initial Velocity is set equal to, or higher than the Maximum Velocity. VI must be less than VM.",
        23: "VM is set less than or equal to VI. The Maximum Velocity is set equal to, or lower than the Initial Velocity. VM must be greater than VI.",
        24: "Illegal data entered. Data has been entered that the devices does not understand.",
        25: "Variable or flag is read only. Read only flags and variables cannot be set.",
        26: "Variable or flag is not allowed to be incremented or decremented. IC and DC cannot be used on variables or flags such as Baud and Version.",
        27: "Trip not defined. Trying to enable a trip that has not yet been defined.",
        28: "WARNING! Trying to redefine a program label or variable.",
        29: "Trying to redefine a built in command, variable or flag.",
        30: "Unknown label or user variable. Trying to Call or Branch to a Label or Variable that has not yet been defined.",
        31: "Program label or user variable table is full. The table has a maximum capacity of 22 labels and/or user variables.",
        32: "Trying to set a label (LB).",
        33: "Trying to SET an Instruction.",
        34: "Trying to Execute a Variable or Flag",
        35: "Trying to Print Illegal Variable or Flag",
        36: "Illegal Motor Count to Encoder Count Ratio",
        37: "Command, Variable or Flag Not Available in Drive",
        38: "Missing parameter separator",
        39: "Trip on Position and Trip on Relative Distance not allowed together",
        40: "Program not running. If HOLD (H) is entered in Immediate Mode and a program is not running.",
        41: "Stack overflow",
        42: "Illegal program card_address. Tried to Clear, List, Execute, etc. an incorrect Program card_address.",
        43: "Tried to overflow program stack. Calling a Sub-Routine or Trip Routine with no Return.",
        44: "Program locked. User Programs can be Locked with the <LK> command. Once Locked, the program cannot be listed or edited in any way.",
        45: "Trying to Overflow Program Space.",
        46: "Not in Program Mode.",
        47: "Tried to Write to Illegal Flash Address",
        48: "Program Execution stopped by I/O set as Stop.",
        60: "Tried to enter an unknown command",
        61: "Trying to set illegal BAUD rate. The only Baud Rates accepted are those listed on the Properties Page of IMS Terminal.",
        62: "IV already pending or IF Flag already TRUE.",
        63: "Character over-run. Character was received. Processor did not have time to process it and it was over-written by the next character.",
        70: "FLASH Check Sum Fault",
        71: "Internal Temperature Warning",
        72: "Internal Over Temperature disabling drive",
        73: "Tried to SAVE while moving",
        74: "Tried to Initialize Parameters (IP) or Clear Program (CP) while Moving",
        76: "Microstep resolution set to low, must be greater than min sys. speed.",
        77: "VM, VI, or SL too great for selected microstep resolution",
        78: "Aux Power out of range",
        79: "V+ out of range",
        80: "HOME switch not defined. Attempting to do a HOME (H) sequence but the Home Switch has not yet been defined.",
        81: "HOME type not defined. The HOME (HM or HI) Command has been programmed butwith no type or an illegal type. (Types = 1, 2, 3, or 4)",
        82: "Went to both LIMITS and did not find home. The motion encroached both limits but did not trip the Home switch. Indicates a possible bad switch or a bad circuit.",
        83: "Reached plus LIMIT switch. The LIMIT switch in the plus direction was tripped.",
        84: "Reached minus LIMIT switch. The LIMIT switch in the minus direction was tripped.",
        85: "MA or MR isn't allowed during a HOME and a HOME isn't allowed while the devices is in motion.",
        86: "Stall detected. The Stall Flag (ST) has been set to 1.",
        87: "Not allowed to change AS mode while moving",
        88: "Moves not allowed while calibration is in progress.",
        89: "Calibration not allowed while motion is in progress.",
        90: "Motion Variables are too low switching to EE=1",
        91: "Motion stopped by I/O set as Stop.",
        92: "Position Error in Closed loop. motor will attempt to position the shaft within the dead band, After failing 3 attempts Error 92 will be generated. Axis will continue to function normally.",
        93: "MR or MA not allowed while correcting position at end of previous MR or MA.",
        94: "Motion commanded while drive disabled (DE=0)",
        95: "Rotation of direction (RD) attempted while axis is in motion",
        100: "Configuration test done, encoder resolution mismatch",
        101: "Configuration test done, encoder direction incorrect",
        102: "Configuration test done, encoder resolution and direction incorrect",
        103: "Configuration not done, drive not enabled",
        104: "Locked rotor",
        105: "Maximum position count reached",
        106: "Lead limit reached",
        107: "Lag limit reached",
        108: "Lead/lag not zero at the end of a move",
        109: "Calibration failed because drive not enabled.",
        110: "Make up disabled.",
        111: "Factory calibration failed",
    }

    def __init__(self, host, port=503, device_id=None, config=None):
        super().__init__(host, port, device_id, config)

    def _init_attributes(self):
        super()._init_attributes()
        self.create_attribute(ATTR_SERIAL_NUMBER, readonly=True)
        self.create_attribute(
            ATTR_TEMPERATURE,
            readonly=True,
            default_type=np.float16,
            decimals=2,
            unit="degC",
        )
        self.create_attribute(ATTR_CHANNELS, default_value=1, readonly=True)

    def handle_configuration(self):

        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()
            self.start_polling()
            self.set_status(STATUS_CONFIGURED)
            self.logger.info(
                "Device configuration took {} sec.".format(time.time() - start_at)
            )

        self.get_error_flag()
        self.get_serial_number(callback=_finish_configuration)

    def handle_readout(self, readout_buffer):
        command, output, callback, token = super().handle_readout(readout_buffer)
        self.handle_command(command, output)

        if callback is not None:
            self.handle_readout_callback(callback, command, readout_buffer)
        if token:
            kamzik3.session.publisher.push_message(
                self.device_id, [command, readout_buffer], token
            )
            for observer in self._observers[:]:
                if isinstance(observer, DeviceLexiumChannel):
                    kamzik3.session.publisher.push_message(
                        observer.device_id, [command, readout_buffer], token
                    )
                    break

    def handle_command(self, command, output):

        command = command.strip()
        data = output.replace(command, "").strip()
        if command == "PR SN":
            self.set_raw_value(ATTR_SERIAL_NUMBER, data)
        elif command == "PR IT":
            self.set_raw_value(ATTR_TEMPERATURE, float(data.replace(", ", ".")))
        elif command == "PR EF":
            if int(data) == 1:
                self.handle_command_error(command, output)
        elif command == "PR ER":
            error_message = self.error_description.get(int(data), "Undefined error")
            self.logger.error(error_message)
            self.set_value(ATTR_LAST_ERROR, error_message)
            self.notify((0, ATTR_LAST_ERROR), error_message)
            self.notify((0, ATTR_ERROR_CODE), int(data))
        elif command == "PR P":
            self.notify((0, ATTR_POSITION), int(data))
        elif command == "PR ST":
            self.notify((0, ATTR_STALL_FLAG), bool(int(data)))
        elif command == "PR MV":
            self.notify((0, ATTR_MOVING), bool(int(data)))
        elif command == "PR V":
            self.notify((0, ATTR_VELOCITY), int(data))
        elif command == "PR I3":
            self.notify((0, ATTR_POSITIVE_LIMIT_SWITCH), bool(int(data)))
        elif command == "PR I4":
            self.notify((0, ATTR_NEGATIVE_LIMIT_SWITCH), bool(int(data)))
        elif command == "PR I6":
            self.notify((0, ATTR_INDEX_MARK), bool(int(data)))
        elif command == "PR HC":
            self.notify((0, ATTR_HOLDING_CURRENT), int(data))
        elif command == "PR VM":
            self.notify((0, ATTR_MAXIMUM_VELOCITY), int(data))
        elif command == "PR VI":
            self.notify((0, ATTR_INITIAL_VELOCITY), int(data))
        elif command == "PR RC":
            self.notify((0, ATTR_RUN_CURRENT), int(data))
        elif command == "PR RD":
            self.notify((0, ATTR_ROTATION_DIRECTION), int(data))
        elif command == "PR TS":
            self.notify((0, ATTR_TORQUE_SPEED), int(data))
        elif command == "PR EE":
            self.notify((0, ATTR_ENCODER_ENABLED), int(data))
        elif command == "PR MS":
            self.notify((0, ATTR_MICROSTEP_RESOLUTION), int(data))
        elif command == "PR SF":
            self.notify((0, ATTR_STALL_FACTOR), int(data))
        elif command == "PR IS":
            for line in data.split("\r\n"):
                out = re.search("IS = ([0-9]), ([0-9]), ([0-9])", line)
                if out:
                    if out.group(1) == "3":
                        if int(out.group(2)) == 0:
                            self.notify((0, ATTR_USE_POSITIVE_LIMIT_SWITCH), False)
                        else:
                            self.notify(
                                (0, ATTR_USE_POSITIVE_LIMIT_SWITCH),
                                bool(int(out.group(3))),
                            )
                    elif out.group(1) == "4":
                        if int(out.group(2)) == 0:
                            self.notify((0, ATTR_USE_POSITIVE_LIMIT_SWITCH), False)
                        else:
                            self.notify(
                                (0, ATTR_USE_NEGATIVE_LIMIT_SWITCH),
                                bool(int(out.group(3))),
                            )
                        break

    def start_polling(self):
        DeviceSocket.start_polling(self)
        self.poll_command("PR IT\r", 1000)

    def get_serial_number(self, callback=None):
        return self.command("PR SN\r", with_token=True, callback=callback)

    def get_device_temperature(self, callback=None):
        return self.command("PR IT\r", with_token=True, callback=callback)

    def get_error_flag(self, callback=None):
        return self.command("PR EF\r", with_token=True, callback=callback)

    def get_error_code(self, callback=None):
        return self.command("PR ER\r", with_token=True, callback=callback)

    def collect_incoming_data(self, data: bytes) -> None:
        if data.find(b"?") != -1:
            (
                command,
                token,
                callback,
                returning,
            ), _timestamp = self.commands_buffer.popleft()
            self.handle_command_error(command, "".join(self.buffer))
            self.device_poller.prepend_command(
                self, ("PR ER\r", token, callback, returning)
            )
            self.buffer = []
        else:
            super().collect_incoming_data(data)


class DeviceLexiumChannel(DeviceChannel):
    available_resolutions = [
        1,
        2,
        4,
        5,
        8,
        10,
        16,
        25,
        32,
        50,
        64,
        100,
        108,
        125,
        127,
        128,
        180,
        200,
        250,
        256,
    ]
    join_token = ',"~",'

    def __init__(self, device, channel, device_id=None, config=None):
        self.referencing_stop = Event()
        self.referencing_stop.set()
        self.backlash_cleared_flag = True
        super().__init__(device, channel, device_id, config)

    def _init_attributes(self):
        super()._init_attributes()
        self.create_attribute(
            ATTR_POSITION,
            default_type=np.float64,
            readonly=False,
            decimals=3,
            set_function=self._move_absolute,
            set_value_when_set_function=False,
        )
        self.create_attribute(
            ATTR_POSITION_LOWER_LIMIT,
            default_type=np.float64,
            decimals=3,
            set_function=self.set_lower_position_limit,
        )
        self.create_attribute(
            ATTR_POSITION_UPPER_LIMIT,
            default_type=np.float64,
            decimals=3,
            set_function=self.set_upper_position_limit,
        )
        self.create_attribute(
            ATTR_BACKLASH_DISTANCE,
            default_value=0,
            default_type=np.float64,
            readonly=False,
            decimals=3,
        )
        self.create_attribute(ATTR_STALL_FLAG, default_type=bool, readonly=True)
        self.create_attribute(ATTR_MOVING, default_type=bool, readonly=True)
        self.create_attribute(ATTR_VELOCITY, default_type=np.uint64, readonly=True)
        self.create_attribute(
            ATTR_HOLDING_CURRENT,
            default_type=np.uint8,
            min_value=0,
            max_value=100,
            unit="%",
            set_function=self.set_holding_current,
        )
        self.create_attribute(
            ATTR_INITIAL_VELOCITY,
            default_type=np.uint64,
            unit="steps/s",
            set_function=self.set_initial_velocity,
        )
        self.create_attribute(
            ATTR_MAXIMUM_VELOCITY,
            default_type=np.uint64,
            unit="steps/s",
            set_function=self.set_maximum_velocity,
        )
        self.create_attribute(
            ATTR_RUN_CURRENT,
            default_type=np.uint8,
            max_value=100,
            unit="%",
            set_function=self.set_run_current,
        )
        self.create_attribute(
            ATTR_ROTATION_DIRECTION,
            default_type=np.uint8,
            max_value=1,
            set_function=self.set_rotation_direction,
        )
        self.create_attribute(
            ATTR_TORQUE_SPEED,
            default_type=np.uint64,
            set_function=self.set_torque_speed,
        )
        self.create_attribute(
            ATTR_ENCODER_ENABLED,
            default_type=np.uint8,
            min_value=0,
            max_value=1,
            set_function=self.set_encoder_enabled,
        )
        self.create_attribute(
            ATTR_MICROSTEP_RESOLUTION,
            default_value="None",
            default_type=self.available_resolutions,
            set_function=self.set_microstep_resolution,
            unit="ustep/step",
        )
        self.create_attribute(
            ATTR_ENCODER_RESOLUTION,
            default_value=4000,
            default_type=np.uint64,
            unit="count/rev",
        )
        self.create_attribute(
            ATTR_STEPS_PER_REVOLUTION,
            default_value=200,
            default_type=np.uint64,
            unit="steps",
        )
        self.create_attribute(
            ATTR_STALL_FACTOR,
            default_type=np.uint64,
            min_value=0,
            max_value=65000,
            unit="counts",
            set_function=self.set_stall_factor,
        )
        self.create_attribute(
            ATTR_POSITIVE_LIMIT_SWITCH, default_type=bool, readonly=True
        )
        self.create_attribute(
            ATTR_NEGATIVE_LIMIT_SWITCH, default_type=bool, readonly=True
        )
        self.create_attribute(ATTR_INDEX_MARK, default_type=bool, readonly=True)
        self.create_attribute(
            ATTR_USE_POSITIVE_LIMIT_SWITCH,
            default_type=bool,
            set_function=lambda value: self.set_digital_input(3, 2, value),
        )
        self.create_attribute(
            ATTR_USE_NEGATIVE_LIMIT_SWITCH,
            default_type=bool,
            set_function=lambda value: self.set_digital_input(4, 3, value),
        )
        self.create_attribute(ATTR_REFERENCING, default_type=bool, readonly=True)
        self.create_attribute(
            ATTR_USE_MARK_INDEX, default_value=True, default_type=bool, readonly=False
        )

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

        self.get_encoder_enabled()
        self.get_holding_current()
        self.get_initial_velocity()
        self.get_maximum_velocity()
        self.get_run_current()
        self.get_rotation_direction()
        self.get_torque_speed()
        self.get_microsteps_resolution()
        self.get_stall_factor()
        self.get_digital_inputs(callback=_finish_configuration)

    def start_polling(self):
        super().start_polling()
        self.poll_command("PR P\r", 200)
        self.poll_command("PR MV\r", 200)
        self.poll_command("PR ST\r", 500)
        self.poll_command("PR V\r", 500)
        self.poll_command("PR I3\r", 1000)
        self.poll_command("PR I4\r", 1000)

    def stop_polling(self):
        self.remove_poll_command("PR P\r", 200)
        self.remove_poll_command("PR MV\r", 200)
        self.remove_poll_command("PR ST\r", 500)
        self.remove_poll_command("PR V\r", 500)
        self.remove_poll_command("PR I3\r", 1000)
        self.remove_poll_command("PR I4\r", 1000)

    def subject_update(self, key, value, subject):
        super().subject_update(key, value, subject)

        if isinstance(key, tuple) and key[0] == self.channel:
            if key[1] == ATTR_MOVING and self.get_value(ATTR_MOVING) != value:
                if value == 1:
                    self.set_status(STATUS_BUSY)
                else:
                    if self.backlash_cleared_flag:
                        self.set_status(STATUS_IDLE)
                    else:
                        self.move_relative(-1 * self.get_value(ATTR_BACKLASH_DISTANCE))
                        self.command("PR MV\r")
                        self.backlash_cleared_flag = True
            elif key[1] == ATTR_POSITION:
                if self.get_value(ATTR_ENCODER_ENABLED):
                    value = (
                        float(value) / self.get_value(ATTR_ENCODER_RESOLUTION)
                    ) * 360
                else:
                    value = (
                        float(value)
                        / (
                            self.get_value(ATTR_MICROSTEP_RESOLUTION)
                            * self.get_value(ATTR_STEPS_PER_REVOLUTION)
                        )
                    ) * 360
            elif key[1] == ATTR_ERROR_CODE:
                if value in (83, 84, 86):
                    self.command("SL=0\r")
                self.set_status(STATUS_ERROR)
                return
            elif key[1] == ATTR_STALL_FLAG and value is True:
                self.command("ST=0\r")

            self.set_raw_value(key[1], value)

    @expose_method()
    def stop(self, callback=None):
        self.logger.info("Stop motor channel movement")
        self.referencing_stop.set()
        self.set_value(ATTR_REFERENCING, False)
        self.backlash_cleared_flag = True
        return self.command("SL=0\r", callback, with_token=True)

    def _move_absolute(self, position, callback=None):
        self.logger.info("Move motor channel to absolute position {}".format(position))
        try:
            position = float(position)
            position_diff = self[ATTR_POSITION][SETPOINT] - self[ATTR_POSITION][VALUE]
            backlash_distance = self.get_value(ATTR_BACKLASH_DISTANCE)

            if (
                self.backlash_cleared_flag
                and backlash_distance != 0
                and np.sign(backlash_distance) == np.sign(position_diff)
            ):
                backlash_distance = self[ATTR_POSITION].remove_offset_factor(
                    backlash_distance
                )
                position += backlash_distance
                self.backlash_cleared_flag = False
            else:
                self.backlash_cleared_flag = True

            if self.get_value(ATTR_ENCODER_ENABLED):
                position = int(
                    round((position / 360.0) * self.get_value(ATTR_ENCODER_RESOLUTION))
                )
            else:
                position = int(
                    round(
                        (position / 360.0)
                        * (
                            self.get_value(ATTR_MICROSTEP_RESOLUTION)
                            * self.get_value(ATTR_STEPS_PER_REVOLUTION)
                        )
                    )
                )
            token = self.command("MA {}\r".format(position), callback, with_token=True)
            self.get_moving_state()
            return token
        except ValueError as e:
            self.logger.exception(e)
            raise DeviceError(e)

    def _move_relative(self, position, callback=None):
        self.logger.info("Move motor channel by relative position {}".format(position))
        try:
            position = float(position)
            backlash_distance = self.get_value(ATTR_BACKLASH_DISTANCE)

            if (
                self.backlash_cleared_flag
                and backlash_distance != 0
                and np.sign(backlash_distance) == np.sign(position)
            ):
                backlash_distance = self[ATTR_POSITION].remove_offset_factor(
                    backlash_distance
                )
                position += backlash_distance
                self.backlash_cleared_flag = False
            else:
                self.backlash_cleared_flag = True

            if self.get_value(ATTR_ENCODER_ENABLED):
                position = int(
                    round((position / 360.0) * self.get_value(ATTR_ENCODER_RESOLUTION))
                )
            else:
                position = int(
                    round(
                        (position / 360.0)
                        * (
                            self.get_value(ATTR_MICROSTEP_RESOLUTION)
                            * self.get_value(ATTR_STEPS_PER_REVOLUTION)
                        )
                    )
                )
            token = self.command("MR {}\r".format(position), callback, with_token=True)
            self.get_moving_state()
            return token
        except ValueError as e:
            self.logger.exception(e)
            raise DeviceError(e)

    @expose_method({"position": ATTR_POSITION})
    def move_absolute(self, position, callback=None):
        try:
            position = device_units(self, ATTR_POSITION, position)
            self.logger.info(
                "Move motor channel to absolute position {}".format(position)
            )
            return self.set_value(ATTR_POSITION, float(position.m), callback)
        except (UndefinedUnitError, ValueError) as e:
            self.logger.exception(e)
            raise DeviceUnitError(e)

    @expose_method({"position": ATTR_POSITION})
    def move_relative(self, position, callback=None):
        try:
            position = device_units(self, ATTR_POSITION, position)
            self.logger.info(
                "Move motor channel by relative position {}".format(position)
            )
            return self.move_absolute(
                self[ATTR_POSITION][VALUE] + float(position.m), callback
            )
        except (UndefinedUnitError, ValueError) as e:
            self.logger.exception(e)
            raise DeviceUnitError(e)

    def set_lower_position_limit(self, value, callback=None):
        return self.set_attribute([ATTR_POSITION, MIN], value, callback)

    def set_upper_position_limit(self, value, callback=None):
        return self.set_attribute([ATTR_POSITION, MAX], value, callback)

    @expose_method({"position": ATTR_POSITION})
    def reset_position(self, position=0, callback=None):
        try:
            position = device_units(self, ATTR_POSITION, units.Quantity(position))
            self.logger.info("Resetting position to {}".format(position))
            position = self[ATTR_POSITION].remove_offset_factor(float(position.m))
            if self.get_value(ATTR_ENCODER_ENABLED):
                position = int(
                    round((position / 360.0) * self.get_value(ATTR_ENCODER_RESOLUTION))
                )
            else:
                position = int(
                    round(
                        (position / 360.0)
                        * (
                            self.get_value(ATTR_MICROSTEP_RESOLUTION)
                            * self.get_value(ATTR_STEPS_PER_REVOLUTION)
                        )
                    )
                )

            return self.command("P={}\r".format(position), callback, with_token=True)
        except (UndefinedUnitError, ValueError) as e:
            self.logger.exception(e)
            raise DeviceUnitError(e)

    @expose_method({"velocity": "steps / second"})
    def slew(self, velocity, callback=None):
        self.logger.info("Slew motor channel by velocity {}".format(velocity))
        try:
            return self.command(
                "SL={}\r".format(int(velocity)), callback, with_token=True
            )
        except ValueError as e:
            self.logger.exception(e)
            raise DeviceError(e)

    @expose_method()
    def find_reference_in_positive_direction(self):
        self.stop_polling()
        self.poll_command("PR MV\r", 400)

        if self.get_value(ATTR_REFERENCING):
            return False
        Thread(target=self.find_reference, args=(1,)).start()
        return True

    @expose_method()
    def find_reference_in_negative_direction(self):
        self.stop_polling()
        self.poll_command("PR MV\r", 400)

        if self.get_value(ATTR_REFERENCING):
            return False
        Thread(target=self.find_reference, args=(-1,)).start()
        return True

    def find_reference(self, direction):
        self.referencing_stop.clear()
        self.set_value(ATTR_REFERENCING, True)

        stage = 0
        maximum_velocity = self.get_value(ATTR_MAXIMUM_VELOCITY)
        limit_switch = (
            ATTR_POSITIVE_LIMIT_SWITCH if direction == 1 else ATTR_NEGATIVE_LIMIT_SWITCH
        )
        if direction == 1:
            self.poll_command("PR I3\r", 200)
        else:
            self.poll_command("PR I4\r", 200)

        while not self.referencing_stop.wait(0.1):
            if stage == 0:  # Drive with maximum veloctiy to the HW limit
                self.slew(maximum_velocity * direction)
                stage = 1
            elif stage == 1 and self.get_value(
                limit_switch
            ):  # Check if we are at the limit
                time.sleep(0.3)
                self.slew(maximum_velocity * 0.3 * -direction)
                stage = 2
            elif stage == 2 and not self.get_value(limit_switch):
                time.sleep(0.3)
                self.slew(maximum_velocity * 0.3 * direction)
                stage = 3
            elif stage == 3 and self.get_value(limit_switch):
                if self.get_value(ATTR_USE_MARK_INDEX):
                    self.poll_command("PR I6\r", 200)
                    time.sleep(0.3)
                    self.find_index_mark(-direction)
                else:
                    self.slew(maximum_velocity * 0.05 * -direction)
                stage = 4
            elif (
                stage == 4
                and self.get_value(ATTR_USE_MARK_INDEX)
                and self.get_value(ATTR_INDEX_MARK)
            ):
                self.remove_poll_command("PR I6\r", 200)
                self.stop()
                time.sleep(0.3)
                position = units.Quantity(self.config.get("reference_position", 0))
                self.reset_position(str(position))
            elif (
                stage == 4
                and not self.get_value(ATTR_USE_MARK_INDEX)
                and not self.get_value(limit_switch)
            ):
                self.stop()
                time.sleep(0.3)
                position = units.Quantity(self.config.get("reference_position", 0))
                self.reset_position(str(position))

        self.set_value(ATTR_REFERENCING, False)
        self.remove_poll_command("PR MV\r", 400)
        self.remove_poll_command("PR I3\r", 200)
        self.remove_poll_command("PR I4\r", 200)
        self.remove_poll_command("PR I6\r", 200)
        self.start_polling()

    def find_index_mark(self, direction):
        if direction == 1:
            direction = 2
        else:
            direction = 4
        self.command("HI={}\r".format(direction))

    def set_holding_current(self, value, callback=None):
        self.logger.info("Set motor channel holding current to {}%".format(value))
        try:
            token = self.command("HC {}\r".format(int(value)), callback, True)
            return token
        except ValueError as e:
            self.logger.exception(e)
            raise DeviceError(e)

    def set_initial_velocity(self, value, callback=None):
        self.logger.info("Set motor channel initial velocity to {}".format(value))
        try:
            token = self.command("VI {}\r".format(int(value)), callback, True)
            return token
        except ValueError as e:
            self.logger.exception(e)
            raise DeviceError(e)

    def set_maximum_velocity(self, value, callback=None):
        self.logger.info("Set motor channel maximum velocity to {}".format(value))
        try:
            token = self.command("VM {}\r".format(int(value)), callback, True)
            return token
        except ValueError as e:
            self.logger.exception(e)
            raise DeviceError(e)

    def set_run_current(self, value, callback=None):
        self.logger.info("Set motor channel run current to {}%".format(value))
        try:
            token = self.command("RC {}\r".format(int(value)), callback, True)
            return token
        except ValueError as e:
            self.logger.exception(e)
            raise DeviceError(e)

    def set_rotation_direction(self, value, callback=None):
        self.logger.info("Set motor channel rotation direction to {}".format(value))
        try:
            token = self.command("RD {}\r".format(int(value)), callback, True)
            return token
        except ValueError as e:
            self.logger.exception(e)
            raise DeviceError(e)

    def set_torque_speed(self, value, callback=None):
        self.logger.info("Set motor channel torque speed to {}".format(value))
        try:
            token = self.command("TS {}\r".format(int(value)), callback, True)
            return token
        except ValueError as e:
            self.logger.exception(e)
            raise DeviceError(e)

    def set_stall_factor(self, value, callback=None):
        self.logger.info("Set motor channel stall factor to {}".format(value))
        try:
            token = self.command("SF {}\r".format(int(value)), callback, True)
            return token
        except ValueError as e:
            self.logger.exception(e)
            raise DeviceError(e)

    def set_encoder_enabled(self, value, callback=None):
        self.logger.info("Set motor channel encoder enabled to {}".format(value))
        try:
            token = self.command("EE {}\r".format(int(value)), callback, True)
            self.get_encoder_enabled()
            return token
        except ValueError as e:
            self.logger.exception(e)
            raise DeviceError(e)

    def set_microstep_resolution(self, value, callback=None):
        self.logger.info(
            "Set motor channel microstep resolution to {} microsteps / step".format(
                value
            )
        )
        try:
            token = self.command("MS {}\r".format(int(value)), callback, True)
            self.get_maximum_velocity()
            return token
        except ValueError as e:
            self.logger.exception(e)
            raise DeviceError(e)

    def set_digital_input(self, input, type, value):
        self.logger.info(
            "Set motor channel digital input {} to {}".format(input, value)
        )
        try:
            self.command("IS={},{},{}\r".format(int(input), int(type), int(value)))
            self.get_digital_inputs()
            self.get_on_positive_switch()
            self.get_on_negative_switch()
        except ValueError as e:
            self.logger.exception(e)
            raise DeviceError(e)

    def get_moving_state(self, callback=None):
        return self.command("PR MV\r", with_token=True, callback=callback)

    def get_holding_current(self, callback=None):
        return self.command("PR HC\r", with_token=True, callback=callback)

    def get_initial_velocity(self, callback=None):
        return self.command("PR VI\r", with_token=True, callback=callback)

    def get_maximum_velocity(self, callback=None):
        return self.command("PR VM\r", with_token=True, callback=callback)

    def get_run_current(self, callback=None):
        return self.command("PR RC\r", with_token=True, callback=callback)

    def get_rotation_direction(self, callback=None):
        return self.command("PR RD\r", with_token=True, callback=callback)

    def get_torque_speed(self, callback=None):
        return self.command("PR TS\r", with_token=True, callback=callback)

    def get_encoder_enabled(self, callback=None):
        return self.command("PR EE\r", with_token=True, callback=callback)

    def get_microsteps_resolution(self, callback=None):
        return self.command("PR MS\r", with_token=True, callback=callback)

    def get_stall_factor(self, callback=None):
        return self.command("PR SF\r", with_token=True, callback=callback)

    def get_on_index_mark(self, callback=None):
        return self.command("PR I6\r", with_token=True, callback=callback)

    def get_on_positive_switch(self, callback=None):
        return self.command("PR I3\r", with_token=True, callback=callback)

    def get_on_negative_switch(self, callback=None):
        return self.command("PR I4\r", with_token=True, callback=callback)

    def get_digital_inputs(self, callback=None):
        return self.command("PR IS\r", with_token=True, callback=callback)

    def get_position(self, callback=None):
        return self.command("PR P\r", with_token=True, callback=callback)

    def get_velocity(self, callback=None):
        return self.command("PR V\r", with_token=True, callback=callback)
