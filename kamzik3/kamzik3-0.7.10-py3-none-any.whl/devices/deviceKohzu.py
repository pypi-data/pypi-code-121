import re
import time
from math import ceil

import numpy as np
from bidict import frozenbidict
from pint.errors import UndefinedUnitError

import kamzik3
from kamzik3 import DeviceUnitError
from kamzik3.constants import *
from kamzik3.devices.deviceChannel import DeviceChannel
from kamzik3.devices.deviceSocket import DeviceSocket
from kamzik3.snippets.snippetsDecorators import expose_method
from kamzik3.snippets.snippetsUnits import device_units

ATTR_READ_ENCODER = "Read encoder"

helptext = """
Example of yaml configuration

Kohzu0: &Kohzu0 !Device:kamzik3.devices.deviceKohzu.DeviceKohzu
   device_id: Kohzu0
   host: 192.168.83.94
Kohzu0_axis_0: &Kohzu0_axis_0 !Device:kamzik3.devices.deviceKohzu.DeviceKohzuChannel
    device: *Kohzu0
    channel: 0
    device_id: Motor
    config:
     attributes:
       !!python/tuple [Encoder resolution, Value]: 50 nm
       !!python/tuple [Step resolution, Value]: 500 nm
       !!python/tuple [Encoder calc den, Value]: 1
       !!python/tuple [Encoder calc num, Value]: 10
       !!python/tuple [Position, Tolerance]: [0.5um, 0.5um]
       !!python/tuple [Referencing method, Value]: 4
       !!python/tuple [Position +limit, Value]: 10 mm
       !!python/tuple [Position -limit, Value]: -10 mm
       !!python/tuple [Maximum velocity, Value]: 10000
"""


class DeviceKohzu(DeviceSocket):
    terminator = b"\r\n"
    # push_buffer_size = 30
    push_commands_max = 1
    error_description = {
        1: "No STX at the beginning of the command. No header character is required in TCPIP only when RS-232C is used.",
        3: "Characters other than specified characters or number are included.",
        4: "There is no applicable command.",
        5: "The emergency stop signal was detected. It is spontaneously sent from ARIES.",
        6: "Since cutting of Motionnet device was detected while a certain axis was driving, the emergency stop was performed. It is spontaneously sent from ARIES.",
        100: "Total number of parameters is incorrect.",
        101: "Numerical value of the 1st parameter is out of range.",
        102: "Numerical value of the 2nd parameter is out of range.",
        103: "Numerical value of the 3rd parameter is out of range.",
        104: "Numerical value of the 4th parameter is out of range.",
        105: "Numerical value of the 5th parameter is out of range.",
        106: "Numerical value of the 6th parameter is out of range.",
        107: "Numerical value of the 7th parameter is out of range.",
        108: "Numerical value of the 8th parameter is out of range.",
        109: "Numerical value of the 9th parameter is out of range.",
        120: "Number of axes specified in a parameter exceeds controllable number of axes. *Determined according to the connection number of slave controllers and the total number of controllable drive axes.",
        121: "Specified system parameter number is not used.",
        300: "Inside IC related error",
        304: "CW limit is activated during driving and the drive stopped.",
        305: "CCW limit is activated during driving and the drive stopped.",
        306: "One of axes entered limit during multi-axis driving (MPS, SPS) and the drive stopped.",
        307: "Both CW limit and CCW limit are in.",
        308: "The motor is not excited.",
        309: "Tried to operate while axes are driving.",
        310: "Even though the number of oscillation is 1, the coordinate of moving destination specifying the stop time exceeds the range of -134,217,728~134,217,727.",
        311: "Tried to rewrite the pulse counter value of driving axis.",
        312: "Tried to rewrite the encoder counter value of driving axis.",
        313: "Tried to rewrite the system parameter of driving axis.",
        314: "Because emergency stop is detected, driving axes are stopped.",
        315: "Because alarm is detected, driving axes are stopped.",
        316: "- side soft limit is more than + side soft limit.",
        317: "Due to + side soft limit, the drive is stopped.",
        318: "Due to - side soft limit, the drive is stopped.",
        319: "One of axes entered soft limit during multi-axis driving (MPS, SPS) and the drive is stopped.",
        320: "Movement amount of standalone axis is 0 between the linear interpolations.",
        321: "Tried to make it operate in the state where a servoready signal is not ON.",
        322: "Since cutting of Motionnet device was detected while the axis was driving, the axis was stopped. Feedback 401 Though the number of retry_count counts exceeded in feedback control, theencoder feedback did not complete.",
        500: "MPI command is not issued.",
        501: "Drive parameter corresponding to the 1st axis of MPS command is not set.",
        502: "Drive parameter corresponding to the 2nd axis of MPS command is not set.",
        503: "Drive parameter corresponding to the 3rd axis of MPS command is not set.",
        504: "Drive parameter corresponding to the 4th axis of MPS command is not set.",
        505: "The coordinate at the movement destination of the MPS 1st axis is out of range (-13.,'21.,'728 to 13.,'21.,'727).",
        506: "The coordinate at the movement destination of the MPS 2nd axis is out of range (-13.,'21.,'728 to 13.,'21.,'727).",
        507: "The coordinate at the movement destination of the MPS 3rd axis is out of range (-13.,'21.,'728 to 13.,'21.,'727).",
        508: "The coordinate at the movement destination of the MPS 4th axis is out of range (-13.,'21.,'728 to 13.,'21.,'727).",
        510: "3 or more axes specified for simultaneous drive are the same.",
        511: "1st and 2nd axes specified for simultaneous drive are the same.",
        512: "1st and 3rd axes specified for simultaneous drive are the same.",
        513: "1st and 4th axes specified for simultaneous drive are the same.",
        514: "2nd and 3rd axes specified for simultaneous drive are the same.",
        515: "2nd and 4th axes specified for simultaneous drive are the same.",
        516: "3rd and 4th axes specified for simultaneous drive are the same.",
        600: "Failed to create a speed table.",
        601: "Acceleration time is large.",
        602: "Acceleration time is small.",
        603: "Deceleration time is large.",
        604: "Deceleration time is small.",
        605: "Start speed exceeds 50% of the maximum speed.",
        606: "Maximum speed of slave axis between the linear interpolations exceeds the limit value (SYS No.16).",
        607: "Maximum speed exceeds the limit value (SYS No.16).",
        700: "While outputting the trigger signal, It was going to change the trigger-related system parameter(SYS.No.51 to 56).",
        701: "TRS command is issued for driving axes.",
        702: "Trigger output doesn't stop after exceeding the setting time.",
        703: "Trigger output stopped before exceeding the setting time.",
        800: "Because emergency stop is detected a command is not executed. It restores by issue of the REM command.",
        801: "Because emergency stop is detected a release cannot be executed. Please publish the REM command after removing the factor of an emergency stop.",
        802: "A command is not executed for the emergency stop state by connection interception (power supply cutting is included) of a Motionnet device. It restores by issue of the RAX command.",
        900: "RAX command is executed during driving.",
        901: "While the axis drove, the WIP command or the PIP command was published.",
        50: "Change of Motionnet device composition was detected. It is spontaneously sent from ARIE.",
        350: "Moving target position exceeds the soft limit. This warning is returned when the drive command's response method is quick while the soft limit is valid and the target position exceeds the soft limit. Driving continues to the soft limit.",
    }
    feedback_control_method = frozenbidict(
        {"No correction": 0, "Correction at positioning": 1, "Normal correction": 2}
    )
    trigger_source = frozenbidict(
        {
            "Motor pulse": 0,
            "Encoder pulse x1": 1,
            "Encoder pulse x2": 2,
            "Encoder pulse x3": 3,
        }
    )
    trigger_pulse_width = frozenbidict(
        {"1 usec": 1, "10 usec": 2, "100 usc": 3, "1000 usc": 4}
    )
    trigger_edge = frozenbidict({RISING: 0, FALLING: 1})
    trigger_logic = frozenbidict({POSITIVE: 0, NEGATIVE: 1})
    microstep_select = frozenbidict({"M1": 0, "M2": 1})
    motor_selection = frozenbidict({"Pulse": 0, "Servo": 1})
    stop_type = frozenbidict({"Deceleration and stop": 0, "Emergency stop": 1})
    motor_excitation = frozenbidict({"Off": 0, "On": 1})
    accelerating_pattern = frozenbidict(
        {"Rectangular drive": 1, "Trapezoidal drive": 2, "S-shaped drive": 3}
    )
    encoder_adding = frozenbidict({"Normal": 0, "Reverse": 1})
    system_setting = frozenbidict(
        {
            ATTR_REFERENCING_METHOD: 2,
            ATTR_ROTATION_CHANGE: 7,
            ATTR_SWAP_LIMITS: 8,
            ATTR_POSITION_UPPER_LIMIT: 14,
            ATTR_POSITION_LOWER_LIMIT: 15,
            ATTR_MAXIMUM_VELOCITY: 16,
            ATTR_ENCODER_CALC_NUM: 33,
            ATTR_ENCODER_CALC_DEN: 34,
            ATTR_ENCODER_ADDING: 35,
            ATTR_FEEDBACK_CONTROL_TYPE: 41,
            ATTR_RETRY_COUNT: 43,
            ATTR_FEEDBACK_TIMEOUT: 44,
            ATTR_TRIGGER_SOURCE: 51,
            ATTR_TRIGGER_EDGE: 52,
            ATTR_TRIGGER_PM_PITCH: 53,
            ATTR_TRIGGER_ENC_PITCH: 54,
            ATTR_TRIGGER_PULSE_WIDTH: 55,
            ATTR_TRIGGER_LOGIC: 56,
            ATTR_MOTOR_EXCITATION: 61,
            ATTR_MOTOR_SELECTION: 62,
            ATTR_MICROSTEP_SELECT: 65,
            ATTR_STOP_TYPE: 99,
        }
    )

    def __init__(self, host, port=12321, device_id=None, config=None):
        super().__init__(host, port, device_id, config)

    def _init_attributes(self):
        super()._init_attributes()

        self.create_attribute(ATTR_SERIAL_NUMBER, readonly=True)
        self.create_attribute(ATTR_CHANNELS, readonly=True, default_type=np.uint16)
        self.create_attribute(ATTR_MODULES, readonly=True, default_type=np.uint16)

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

        # Get ARIES serial number
        self.command("IDN\r\n")
        # Get ARIES configuration
        self.command("RAX\r\n", callback=_finish_configuration)

    def handle_readout(self, readout_buffer):
        command, output, callback, token = super().handle_readout(readout_buffer)
        output_parts = output.split("\t")
        response_flag = output_parts.pop(0)

        if response_flag == "E":
            command, error_code = output_parts
            readout_buffer = self.error_description.get(
                int(error_code), "Undefined error"
            )
            self.handle_command_error(command, readout_buffer)
            s = re.search("[A-Z]+([0-9]+)", command)
            command = RESPONSE_ERROR
            if s is not None and s != -1:
                channel = int(s.group(1)) - 1
                self.notify((channel, ATTR_LAST_ERROR), readout_buffer)
        elif command == "IDN\r\n":
            self.set_value(
                ATTR_SERIAL_NUMBER,
                "{} {}".format(" ".join(output_parts[:2]), ".".join(output_parts[2:])),
            )
        elif command == "RAX\r\n":
            self.set_value(ATTR_MODULES, int(output_parts[1]))
            self.set_value(ATTR_CHANNELS, int(output_parts[2]))
        elif output_parts[0][:3] == "RSY":
            channel = int(output_parts[0][3:]) - 1
            self.notify(
                (channel, self.system_setting.inv[int(output_parts[1])]),
                int(output_parts[2]),
            )
        elif output_parts[0][:3] == "RTB":
            channel = int(output_parts[0][3:]) - 1
            self.notify((channel, ATTR_SPEED_TABLE_ROW), ", ".join(output_parts))
            self.notify((channel, ATTR_START_SPEED), int(output_parts[2]))
            self.notify((channel, ATTR_TOP_SPEED), int(output_parts[3]))
            self.notify((channel, ATTR_ACCELERATION_TIME), int(output_parts[4]))
            self.notify((channel, ATTR_DECELERATION_TIME), int(output_parts[5]))
            self.notify(
                (channel, ATTR_ACCELERATION_PATTERN),
                self.accelerating_pattern.inv[int(output_parts[6])],
            )
        elif output_parts[0][:3] == "STR":
            channel = int(output_parts[0][3:]) - 1
            self.notify((channel, ATTR_STATE), output_parts[1:])
        elif output_parts[0][:3] == "RDE":
            channel = int(output_parts[0][3:]) - 1
            self.notify((channel, ATTR_ENCODER_READ), int(output_parts[1]))
        elif output_parts[0][:3] == "RDP":
            channel = int(output_parts[0][3:]) - 1
            self.notify((channel, ATTR_PULSE_READ), int(output_parts[1]))
        elif output_parts[0][:3] == "ROG":
            channel = int(output_parts[0][3:]) - 1
            self.notify((channel, ATTR_REFERENCED), int(output_parts[1]))

        if callback is not None:
            self.handle_readout_callback(callback, command, readout_buffer)
        if token:
            kamzik3.session.publisher.push_message(
                self.device_id, [command, readout_buffer], token
            )
            for observer in self._observers[:]:
                if isinstance(observer, DeviceKohzuChannel):
                    kamzik3.session.publisher.push_message(
                        observer.device_id, [command, readout_buffer], token
                    )


class DeviceKohzuChannel(DeviceChannel):
    def _init_attributes(self):
        super()._init_attributes()

        self.create_attribute(
            ATTR_STATE, readonly=True, default_type=np.uint8, min_value=0, max_value=3
        )
        self.create_attribute(ATTR_EMERGENCY_STOP, readonly=True, default_type=np.bool)
        self.create_attribute(ATTR_CWL, readonly=True, default_type=np.bool)
        self.create_attribute(ATTR_CCWL, readonly=True, default_type=np.bool)
        self.create_attribute(ATTR_ORG, readonly=True, default_type=np.bool)
        self.create_attribute(ATTR_NORG, readonly=True, default_type=np.bool)
        self.create_attribute(ATTR_REFERENCED, readonly=True, default_type=np.bool)
        self.create_attribute(
            ATTR_ROTATION_CHANGE,
            default_type=np.uint8,
            min_value=0,
            max_value=1,
            set_function=lambda v: self.set_sys(ATTR_ROTATION_CHANGE, v),
        )
        self.create_attribute(
            ATTR_SWAP_LIMITS,
            default_type=np.uint8,
            min_value=0,
            max_value=1,
            set_function=lambda v: self.set_sys(ATTR_SWAP_LIMITS, v),
        )
        self.create_attribute(
            ATTR_ENCODER_READ,
            default_type=np.int64,
            set_function=self.set_encoder_value,
        )
        self.create_attribute(
            ATTR_PULSE_READ,
            default_type=np.int64,
            set_function=self.set_pulse_value,
            unit="pulse",
        )
        self.create_attribute(
            ATTR_POSITION,
            default_type=np.int64,
            set_function=self._move_absolute,
            unit="nm",
            set_value_when_set_function=False,
        )
        self.create_attribute(
            ATTR_REFERENCING_METHOD,
            default_type=np.uint8,
            min_value=1,
            max_value=15,
            set_function=lambda v: self.set_sys(ATTR_REFERENCING_METHOD, v),
        )
        self.create_attribute(
            ATTR_POSITION_LOWER_LIMIT,
            default_type=np.int64,
            min_value=-134217728,
            max_value=134217727,
            unit="nm",
            set_function=lambda v: self.set_sys(ATTR_POSITION_LOWER_LIMIT, v),
        )
        self.create_attribute(
            ATTR_STEP_RESOLUTION,
            default_value=500,
            default_type=np.int64,
            min_value=1,
            max_value=134217727,
            unit="nm",
        )
        self.create_attribute(
            ATTR_START_SPEED,
            default_value=1,
            default_type=np.int32,
            min_value=1,
            max_value=2.5e6,
            unit="pulse/s",
            set_function=lambda v: self.write_speed_table(start_speed=v),
        )
        self.create_attribute(
            ATTR_TOP_SPEED,
            default_value=1,
            default_type=np.int32,
            min_value=2,
            max_value=5e6,
            unit="pulse/s",
            set_function=lambda v: self.write_speed_table(top_speed=v),
        )
        self.create_attribute(
            ATTR_ACCELERATION_TIME,
            default_value=1,
            default_type=np.int32,
            min_value=1,
            max_value=10e3,
            unit="ms",
            set_function=lambda v: self.write_speed_table(acceleration_time=v),
        )
        self.create_attribute(
            ATTR_DECELERATION_TIME,
            default_value=1,
            default_type=np.int32,
            min_value=1,
            max_value=10e3,
            unit="ms",
            set_function=lambda v: self.write_speed_table(deceleration_time=v),
        )
        self.create_attribute(
            ATTR_ENCODER_RESOLUTION,
            default_value=50,
            default_type=np.int64,
            min_value=1,
            max_value=134217727,
            unit="nm",
        )
        self.create_attribute(
            ATTR_POSITION_UPPER_LIMIT,
            default_type=np.int64,
            min_value=-134217728,
            max_value=134217727,
            unit="nm",
            set_function=lambda v: self.set_sys(ATTR_POSITION_UPPER_LIMIT, v),
        )
        self.create_attribute(
            ATTR_MAXIMUM_VELOCITY,
            default_type=np.uint32,
            min_value=2,
            max_value=5000000,
            set_function=lambda v: self.set_sys(ATTR_MAXIMUM_VELOCITY, v),
        )
        self.create_attribute(
            ATTR_ENCODER_CALC_NUM,
            default_type=np.uint32,
            min_value=1,
            max_value=134217727,
            set_function=lambda v: self.set_sys(ATTR_ENCODER_CALC_NUM, v),
        )
        self.create_attribute(
            ATTR_ENCODER_CALC_DEN,
            default_type=np.uint32,
            min_value=1,
            max_value=134217727,
            set_function=lambda v: self.set_sys(ATTR_ENCODER_CALC_DEN, v),
        )
        self.create_attribute(
            ATTR_FEEDBACK_CONTROL_TYPE,
            default_type=DeviceKohzu.feedback_control_method.keys(),
            set_function=lambda v: self.set_sys(
                ATTR_FEEDBACK_CONTROL_TYPE, DeviceKohzu.feedback_control_method[v]
            ),
        )
        self.create_attribute(
            ATTR_RETRY_COUNT,
            default_type=np.uint16,
            min_value=1,
            max_value=10e3,
            set_function=lambda v: self.set_sys(ATTR_RETRY_COUNT, v),
        )
        self.create_attribute(
            ATTR_FEEDBACK_TIMEOUT,
            default_type=np.uint16,
            min_value=1,
            max_value=10e3,
            unit="ms",
            set_function=lambda v: self.set_sys(ATTR_FEEDBACK_TIMEOUT, v),
        )
        self.create_attribute(
            ATTR_TRIGGER_SOURCE,
            default_type=DeviceKohzu.trigger_source.keys(),
            set_function=lambda v: self.set_sys(
                ATTR_TRIGGER_SOURCE, DeviceKohzu.trigger_source[v]
            ),
        )
        self.create_attribute(
            ATTR_TRIGGER_EDGE,
            default_type=DeviceKohzu.trigger_edge.keys(),
            set_function=lambda v: self.set_sys(
                ATTR_TRIGGER_EDGE, DeviceKohzu.trigger_edge[v]
            ),
        )
        self.create_attribute(
            ATTR_TRIGGER_PM_PITCH,
            default_type=np.uint32,
            min_value=1,
            max_value=100e3,
            set_function=lambda v: self.set_sys(ATTR_TRIGGER_PM_PITCH, v),
        )
        self.create_attribute(
            ATTR_TRIGGER_ENC_PITCH,
            default_type=np.uint32,
            min_value=1,
            max_value=100e3,
            set_function=lambda v: self.set_sys(ATTR_TRIGGER_ENC_PITCH, v),
        )
        self.create_attribute(
            ATTR_TRIGGER_PULSE_WIDTH,
            default_type=DeviceKohzu.trigger_pulse_width.keys(),
            set_function=lambda v: self.set_sys(
                ATTR_TRIGGER_PULSE_WIDTH, DeviceKohzu.trigger_pulse_width[v]
            ),
        )
        self.create_attribute(
            ATTR_ENCODER_ADDING,
            default_type=DeviceKohzu.encoder_adding.keys(),
            set_function=lambda v: self.set_sys(
                ATTR_ENCODER_ADDING, DeviceKohzu.encoder_adding[v]
            ),
        )
        self.create_attribute(
            ATTR_TRIGGER_LOGIC,
            default_type=DeviceKohzu.trigger_logic.keys(),
            set_function=lambda v: self.set_sys(
                ATTR_TRIGGER_LOGIC, DeviceKohzu.trigger_logic[v]
            ),
        )
        self.create_attribute(
            ATTR_MOTOR_EXCITATION,
            default_type=DeviceKohzu.motor_excitation.keys(),
            set_function=lambda v: self.set_sys(
                ATTR_MOTOR_EXCITATION, DeviceKohzu.motor_excitation[v]
            ),
        )
        self.create_attribute(
            ATTR_MOTOR_SELECTION,
            default_type=DeviceKohzu.motor_selection.keys(),
            set_function=lambda v: self.set_sys(
                ATTR_MOTOR_SELECTION, DeviceKohzu.motor_selection[v]
            ),
        )
        self.create_attribute(
            ATTR_MICROSTEP_SELECT,
            default_type=DeviceKohzu.microstep_select.keys(),
            set_function=lambda v: self.set_sys(
                ATTR_MICROSTEP_SELECT, DeviceKohzu.microstep_select[v]
            ),
        )
        self.create_attribute(
            ATTR_STOP_TYPE,
            default_type=DeviceKohzu.stop_type.keys(),
            set_function=lambda v: self.set_sys(
                ATTR_STOP_TYPE, DeviceKohzu.stop_type[v]
            ),
        )
        self.create_attribute(
            ATTR_ACCELERATION_PATTERN,
            default_type=DeviceKohzu.accelerating_pattern.keys(),
            set_function=lambda v: self.write_speed_table(acceleration_pattern=v),
        )
        self.create_attribute(
            ATTR_READ_ENCODER, default_value=True, readonly=False, default_type=np.bool
        )
        self.create_attribute(
            ATTR_VELOCITY,
            default_value=0,
            default_type=np.int64,
            min_value=0,
            max_value=3e6,
            unit="nm/s",
            set_function=self.set_velocity,
            set_value_when_set_function=False,
        )
        self.create_attribute(ATTR_SPEED_TABLE_ROW, readonly=True)

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

        self.connected = True
        self.get_system_setting(ATTR_POSITION_LOWER_LIMIT)
        self.get_system_setting(ATTR_POSITION_UPPER_LIMIT)
        self.get_system_setting(ATTR_ROTATION_CHANGE)
        self.get_system_setting(ATTR_SWAP_LIMITS)
        self.get_system_setting(ATTR_MAXIMUM_VELOCITY)
        self.get_system_setting(ATTR_ENCODER_CALC_NUM)
        self.get_system_setting(ATTR_ENCODER_CALC_DEN)
        self.get_system_setting(ATTR_FEEDBACK_CONTROL_TYPE)
        self.get_system_setting(ATTR_RETRY_COUNT)
        self.get_system_setting(ATTR_TRIGGER_SOURCE)
        self.get_system_setting(ATTR_TRIGGER_EDGE)
        self.get_system_setting(ATTR_TRIGGER_PM_PITCH)
        self.get_system_setting(ATTR_TRIGGER_ENC_PITCH)
        self.get_system_setting(ATTR_TRIGGER_PULSE_WIDTH)
        self.get_system_setting(ATTR_TRIGGER_LOGIC)
        self.get_system_setting(ATTR_MOTOR_EXCITATION)
        self.get_system_setting(ATTR_MOTOR_SELECTION)
        self.get_system_setting(ATTR_MICROSTEP_SELECT)
        self.get_system_setting(ATTR_STOP_TYPE)
        self.get_system_setting(ATTR_REFERENCING_METHOD)
        self.get_system_setting(ATTR_ENCODER_ADDING)
        self.get_referenced()
        self.command(
            "RTB{}/0\r\n".format(self.channel + 1), callback=_finish_configuration
        )

    def set_velocity(self, value):
        self.set_raw_value(ATTR_VELOCITY, value)
        value = int(ceil(value / self[ATTR_STEP_RESOLUTION][VALUE]))
        if value == 0:
            value = 1
        start_speed = 500
        acceleration = int(((value - 1000) * 4) / 1000 + 16)
        if value < 1000:
            start_speed = int(value / 2)
            acceleration = 1
        deceleration = acceleration
        self.write_speed_table(
            start_speed,
            value,
            acceleration,
            deceleration,
            acceleration_pattern="Trapezoidal drive",
        )

    def subject_update(self, key, value, subject):
        super().subject_update(key, value, subject)

        if self.connected and isinstance(key, tuple) and key[0] == self.channel:
            attribute = key[1]
            if attribute == ATTR_FEEDBACK_CONTROL_TYPE:
                value = DeviceKohzu.feedback_control_method.inv[value]
            elif attribute == ATTR_TRIGGER_EDGE:
                value = DeviceKohzu.trigger_edge.inv[value]
            elif attribute == ATTR_TRIGGER_SOURCE:
                value = DeviceKohzu.trigger_source.inv[value]
            elif attribute == ATTR_TRIGGER_LOGIC:
                value = DeviceKohzu.trigger_logic.inv[value]
            elif attribute == ATTR_TRIGGER_PULSE_WIDTH:
                value = DeviceKohzu.trigger_pulse_width.inv[value]
            elif attribute == ATTR_ENCODER_ADDING:
                value = DeviceKohzu.encoder_adding.inv[value]
            elif attribute == ATTR_MOTOR_EXCITATION:
                value = DeviceKohzu.motor_excitation.inv[value]
            elif attribute == ATTR_MOTOR_SELECTION:
                value = DeviceKohzu.motor_selection.inv[value]
            elif attribute == ATTR_MICROSTEP_SELECT:
                value = DeviceKohzu.microstep_select.inv[value]
            elif attribute == ATTR_STOP_TYPE:
                value = DeviceKohzu.stop_type.inv[value]
            elif attribute == ATTR_ENCODER_READ and self.get_value(ATTR_READ_ENCODER):
                self.set_raw_value(
                    ATTR_POSITION, value * self[ATTR_ENCODER_RESOLUTION][VALUE]
                )
            elif attribute == ATTR_PULSE_READ and not self.get_value(ATTR_READ_ENCODER):
                self.set_raw_value(
                    ATTR_POSITION, value * self[ATTR_STEP_RESOLUTION][VALUE]
                )
            elif attribute == ATTR_POSITION_LOWER_LIMIT:
                self.set_attribute([ATTR_POSITION, MIN], value)
            elif attribute == ATTR_POSITION_UPPER_LIMIT:
                self.set_attribute([ATTR_POSITION, MAX], value)
            elif attribute == ATTR_STATE:
                if int(value[0]) == 0:
                    self.set_status(STATUS_IDLE)
                else:
                    self.set_status(STATUS_BUSY)
                self.set_value(ATTR_EMERGENCY_STOP, bool(int(value[1])))

                org_value = int(value[2])
                if org_value == 0:
                    self.set_value(ATTR_ORG, False)
                    self.set_value(ATTR_NORG, False)
                elif org_value == 1:
                    self.set_value(ATTR_ORG, False)
                    self.set_value(ATTR_NORG, True)
                elif org_value == 2:
                    self.set_value(ATTR_ORG, True)
                    self.set_value(ATTR_NORG, False)
                elif org_value == 3:
                    self.set_value(ATTR_ORG, True)
                    self.set_value(ATTR_NORG, True)

                limit_value = int(value[3])
                if limit_value == 0:
                    self.set_value(ATTR_CWL, False)
                    self.set_value(ATTR_CCWL, False)
                elif limit_value == 1:
                    self.set_value(ATTR_CWL, False)
                    self.set_value(ATTR_CCWL, True)
                elif limit_value == 2:
                    self.set_value(ATTR_CWL, True)
                    self.set_value(ATTR_CCWL, False)
                elif limit_value == 3:
                    self.set_value(ATTR_CWL, True)
                    self.set_value(ATTR_CCWL, True)

                value = int(value[0])

            self.set_raw_value(ATTR_LATENCY, self.device.get_value(ATTR_LATENCY))
            self.set_raw_value(attribute, value)

    def start_polling(self):
        super().start_polling()
        self.poll_command("STR{}\r\n".format(self.channel + 1), 300)
        self.poll_command("RDE{}\r\n".format(self.channel + 1), 300)
        self.poll_command("RDP{}\r\n".format(self.channel + 1), 300)
        self.poll_command("ROG{}\r\n".format(self.channel + 1), 500)

    def stop_polling(self):
        self.remove_poll_command("STR{}\r\n".format(self.channel + 1), 300)
        self.remove_poll_command("RDE{}\r\n".format(self.channel + 1), 300)
        self.remove_poll_command("RDP{}\r\n".format(self.channel + 1), 300)
        self.remove_poll_command("ROG{}\r\n".format(self.channel + 1), 500)

    def get_system_setting(self, setting, callback=None):
        return self.command(
            "RSY{}/{}\r\n".format(
                self.channel + 1, DeviceKohzu.system_setting[setting]
            ),
            callback,
            with_token=True,
        )

    def set_sys(self, setting, value, callback=None):
        token = self.command(
            "WSY{}/{}/{}\r\n".format(
                self.channel + 1, DeviceKohzu.system_setting[setting], int(value)
            ),
            callback,
            with_token=True,
        )
        self.get_system_setting(setting)
        if setting == ATTR_POSITION_UPPER_LIMIT:
            self.get_system_setting(ATTR_POSITION_LOWER_LIMIT)
        elif setting == ATTR_POSITION_LOWER_LIMIT:
            self.get_system_setting(ATTR_POSITION_UPPER_LIMIT)
        return token

    def write_speed_table(
        self,
        start_speed=None,
        top_speed=None,
        acceleration_time=None,
        deceleration_time=None,
        acceleration_pattern=None,
        callback=None,
    ):
        if start_speed is None:
            start_speed = self.get_value(ATTR_START_SPEED)
        if top_speed is None:
            top_speed = self.get_value(ATTR_TOP_SPEED)
        if acceleration_time is None:
            acceleration_time = self.get_value(ATTR_ACCELERATION_TIME)
        if deceleration_time is None:
            deceleration_time = self.get_value(ATTR_DECELERATION_TIME)
        if acceleration_pattern is None:
            acceleration_pattern = self.get_value(ATTR_ACCELERATION_PATTERN)

        top_speed = int(top_speed)
        start_speed = int(start_speed)
        acceleration_time = int(acceleration_time)
        deceleration_time = int(deceleration_time)
        acceleration_pattern = DeviceKohzu.accelerating_pattern[acceleration_pattern]
        self.command(
            "WTB{}/{}/{}/{}/{}/{}/{}\r\n".format(
                self.channel + 1,
                0,
                start_speed,
                top_speed,
                acceleration_time,
                deceleration_time,
                acceleration_pattern,
            ),
            callback,
        )
        return self.command(
            "RTB{}/0\r\n".format(self.channel + 1), callback, with_token=True
        )

    @expose_method()
    def stop(self, callback=None):
        self.logger.info("Stop movement")
        stop_type = DeviceKohzu.stop_type[self.get_value(ATTR_STOP_TYPE)]
        return self.command(
            "STP{}/{}\r\n".format(self.channel + 1, stop_type),
            callback,
            with_token=True,
        )

    @expose_method()
    def system_rest(self, callback=None):
        self.logger.info("System rest")
        return self.command("RST\r\n", callback, with_token=True)

    @expose_method()
    def find_reference(self, callback=None):
        self.logger.info("Reference")
        return self.command(
            "ORG{}/{}/{}\r\n".format(self.channel + 1, 0, 1), callback, with_token=True
        )

    # @expose_method()
    # def find_reference_reversed(self, callback=None):
    #     self.stop_polling()
    #     rotational_direction = not self[ATTR_ROTATION_CHANGE][VALUE]
    #     swap_limits = not self[ATTR_SWAP_LIMITS][VALUE]
    #
    #     self.set_value(ATTR_ROTATION_CHANGE, rotational_direction)
    #     self.set_value(ATTR_SWAP_LIMITS, swap_limits)
    #
    #     def _swap_rotation_back(*_, **__):
    #         self.start_polling()
    #         self.set_value(ATTR_ROTATION_CHANGE, int(not rotational_direction))
    #         self.set_value(ATTR_SWAP_LIMITS, int(not swap_limits))
    #         if callback is not None:
    #             callback()
    #
    #     self.logger.info(u"Reference")
    #     return self.command(u"ORG{}/{}/{}\r\n".format(self.channel + 1, 0, 0), _swap_rotation_back, with_token=True)

    @expose_method()
    def release_emergency_stop(self, callback=None):
        self.logger.info("Emergency stop released")
        return self.command("REM\r\n", callback, with_token=True)

    @expose_method()
    def jog_clockwise(self, callback=None):
        self.logger.info("Jog clockwise")
        return self.command(
            "FRP{}/{}/{}\r\n".format(self.channel + 1, 0, 0), callback, with_token=True
        )

    @expose_method()
    def jog_counter_clockwise(self, callback=None):
        self.logger.info("Jog clockwise")
        return self.command(
            "FRP{}/{}/{}\r\n".format(self.channel + 1, 0, 1), callback, with_token=True
        )

    @expose_method({"position": ATTR_POSITION})
    def move_absolute(self, position, callback=None):
        try:
            position = device_units(self, ATTR_POSITION, position)
            self.logger.info("Move to absolute position {}".format(position))
            return self.set_value(ATTR_POSITION, position, callback=callback)
        except (UndefinedUnitError, ValueError) as e:
            self.logger.exception(e)
            raise DeviceUnitError(e)

    @expose_method({"position": ATTR_POSITION})
    def move_relative(self, position, callback=None):
        try:
            position = device_units(self, ATTR_POSITION, position)
            self.logger.info("Move by relative position {}".format(position))
            return self.set_value(
                ATTR_POSITION, self[ATTR_POSITION].value() + position, callback=callback
            )
        except (UndefinedUnitError, ValueError) as e:
            self.logger.exception(e)
            raise DeviceUnitError(e)

    def _move_absolute(self, value, callback=None):
        self.logger.info("Move to position {}".format(value))
        # APS{channel},{speed table #},{position},{response type}
        value /= self[ATTR_STEP_RESOLUTION][VALUE]
        return self.command(
            "APS{}/{}/{}/{}\r\n".format(self.channel + 1, 0, int(value), 1),
            callback,
            with_token=True,
        )

    def _move_relative(self, value, callback=None):
        self.logger.info("Move to position {}".format(value))
        # APS{channel},{speed table #},{position},{response type}
        value /= self[ATTR_STEP_RESOLUTION][VALUE]
        return self.command(
            "RPS{}/{}/{}/{}\r\n".format(self.channel + 1, 0, int(value), 1),
            callback,
            with_token=True,
        )

    def get_referenced(self, callback=None):
        return self.command(
            "ROG{}\r\n".format(self.channel + 1), callback, with_token=True
        )

    def set_encoder_value(self, value, callback=None):
        value = int(value)
        self.logger.info("Set encoder value to {}".format(value))
        return self.command(
            "WRE{}/{}\r\n".format(self.channel + 1, value), callback, with_token=True
        )

    def set_pulse_value(self, value, callback=None):
        value = int(value)
        self.logger.info("Set pulse value to {}".format(value))
        return self.command(
            "WRP{}/{}\r\n".format(self.channel + 1, value), callback, with_token=True
        )
