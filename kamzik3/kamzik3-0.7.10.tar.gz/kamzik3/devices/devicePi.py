import re
import time
from decimal import DivisionByZero
from math import ceil

import bidict
import numpy as np
import serial
from bidict import frozenbidict, MutableBidict
from numpy import around, sign, sqrt
from pint.errors import UndefinedUnitError

import kamzik3
from kamzik3 import DeviceUnitError, DeviceError
from kamzik3.constants import *
from kamzik3.devices.deviceChannel import DeviceChannel
from kamzik3.devices.devicePort import DevicePort
from kamzik3.devices.deviceSocket import DeviceSocket
from kamzik3.snippets.snippetsDecorators import expose_method
from kamzik3.snippets.snippetsUnits import device_units

TRIG_OUTPUT_STEP = "Trigger step"
TRIG_OUTPUT_AXIS = "Trigger axis"
TRIG_OUTPUT_MODE = "Trigger mode"
TRIG_OUTPUT_MIN_THRESHOLD = "Trigger min threshold"
TRIG_OUTPUT_MAX_THRESHOLD = "Trigger max threshold"
TRIG_POLARITY = "Trigger polarity"
TRIG_START = "Trigger start"
TRIG_STOP = "Trigger stop"

trigger_output_config = frozenbidict(
    {
        TRIG_OUTPUT_STEP: 1,
        TRIG_OUTPUT_AXIS: 2,
        TRIG_OUTPUT_MODE: 3,
        TRIG_OUTPUT_MIN_THRESHOLD: 5,
        TRIG_OUTPUT_MAX_THRESHOLD: 6,
        TRIG_POLARITY: 7,
        TRIG_START: 8,
        TRIG_STOP: 9,
    }
)

TRIG_MODE_POSITION_DISTANCE = "Position distance"
TRIG_MODE_ON_TARGET = "On target"
TRIG_MODE_WITHIN_THRESHOLD = "Within thresholds"
TRIG_MODE_GENERATOR = "Generator"
trigger_output_mode = frozenbidict(
    {
        TRIG_MODE_POSITION_DISTANCE: 0,
        TRIG_MODE_ON_TARGET: 2,
        TRIG_MODE_WITHIN_THRESHOLD: 3,
        TRIG_MODE_GENERATOR: 4,
    }
)

INTERPOLATION_NONE = "No interpolation"
INTERPOLATION_LINE = "Line interpolation"
data_interpolation = frozenbidict(
    {
        INTERPOLATION_NONE: 0,
        INTERPOLATION_LINE: 1,
    }
)

WAVE_TYPE_PNT = "PNT"  # User defined curve
WAVE_TYPE_SINP = "SIN_P"  # Inverted cosine curve
WAVE_TYPE_RAMP = "RAMP"  # Ramp curve
WAVE_TYPE_LIN = "LIN"  # Inverted cosine curve
WAVE_TYPE_APPEND = "&"
WAVE_TYPE_START = "X"

SERVO_UPDATE_TIME_PARAM = "0xe000200"

REC_TARGET_POSITION = 1
REC_CURRENT_POSITION = 2
REC_ERROR = 3
REC_DDL_OUTPUT = 13
REC_OPEN_LOOP = 14
REC_CONTROL_OUTPUT = 15
REC_SLOWED_TARGET = 22


class DevicePi(DeviceSocket):
    terminator = b"\n"
    error_pattern = re.compile("^([-0-9]+)$")
    response_timeout = 3000
    PRE_SCAN_POINTS = 10
    MAX_SPEED_UMPMS = 10.0  # speed initially set in controller 10 mm/sec
    # to reduce communication time, we can pack up to 27 points of a WaveTable into a single "WAV ... PNT" command
    N_WAV_POINTS_PER_CMD = 27
    # to reduce communication time, we can pack up to 10 trigger actions into a single "TWS" command
    N_TRIG_PER_CMD = 10
    CTR_NAME = "Dev1/ctr0"
    CTR_MAX_SEC = (
        50.0  # in this case, we can count with 80MHz clock (-> highest precision)
    )
    error_description = {
        0: "PI_CNTR_NO_ERROR",
        1: "PI_CNTR_PARAM_SYNTAX",
        2: "PI_CNTR_UNKNOWN_COMMAND",
        3: "PI_CNTR_COMMAND_TOO_LONG",
        4: "PI_CNTR_SCAN_ERROR",
        5: "PI_CNTR_MOVE_WITHOUT_REF_OR_NO_SERVO",
        6: "PI_CNTR_INVALID_SGA_PARAM",
        7: "PI_CNTR_POS_OUT_OF_LIMITS",
        8: "PI_CNTR_VEL_OUT_OF_LIMITS",
        9: "PI_CNTR_SET_PIVOT_NOT_POSSIBLE",
        10: "PI_CNTR_STOP",
        11: "PI_CNTR_SST_OR_SCAN_RANGE",
        12: "PI_CNTR_INVALID_SCAN_AXES",
        13: "PI_CNTR_INVALID_NAV_PARAM",
        14: "PI_CNTR_INVALID_ANALOG_INPUT",
        15: "PI_CNTR_INVALID_AXIS_IDENTIFIER",
        16: "PI_CNTR_INVALID_STAGE_NAME",
        17: "PI_CNTR_PARAM_OUT_OF_RANGE",
        18: "PI_CNTR_INVALID_MACRO_NAME",
        19: "PI_CNTR_MACRO_RECORD",
        20: "PI_CNTR_MACRO_NOT_FOUND",
        21: "PI_CNTR_AXIS_HAS_NO_BRAKE",
        22: "PI_CNTR_DOUBLE_AXIS",
        23: "PI_CNTR_ILLEGAL_AXIS",
        24: "PI_CNTR_PARAM_NR",
        25: "PI_CNTR_INVALID_REAL_NR",
        26: "PI_CNTR_MISSING_PARAM",
        27: "PI_CNTR_SOFT_LIMIT_OUT_OF_RANGE",
        28: "PI_CNTR_NO_MANUAL_PAD",
        29: "PI_CNTR_NO_JUMP",
        30: "PI_CNTR_INVALID_JUMP",
        31: "PI_CNTR_AXIS_HAS_NO_REFERENCE",
        32: "PI_CNTR_STAGE_HAS_NO_LIM_SWITCH",
        33: "PI_CNTR_NO_RELAY_CARD",
        34: "PI_CNTR_CMD_NOT_ALLOWED_FOR_STAGE",
        35: "PI_CNTR_NO_DIGITAL_INPUT",
        36: "PI_CNTR_NO_DIGITAL_OUTPUT",
        37: "PI_CNTR_NO_MCM",
        38: "PI_CNTR_INVALID_MCM",
        39: "PI_CNTR_INVALID_CNTR_NUMBER",
        40: "PI_CNTR_NO_JOYSTICK_CONNECTED",
        41: "PI_CNTR_INVALID_EGE_AXIS",
        42: "PI_CNTR_SLAVE_POSITION_OUT_OF_RANGE",
        43: "PI_CNTR_COMMAND_EGE_SLAVE",
        44: "PI_CNTR_JOYSTICK_CALIBRATION_FAILED",
        45: "PI_CNTR_REFERENCING_FAILED",
        46: "PI_CNTR_OPM_MISSING",
        47: "PI_CNTR_OPM_NOT_INITIALIZED",
        48: "PI_CNTR_OPM_COM_ERROR",
        49: "PI_CNTR_MOVE_TO_LIMIT_SWITCH_FAILED",
        50: "PI_CNTR_REF_WITH_REF_DISABLED",
        51: "PI_CNTR_AXIS_UNDER_JOYSTICK_CONTROL",
        52: "PI_CNTR_COMMUNICATION_ERROR",
        53: "PI_CNTR_DYNAMIC_MOVE_IN_PROCESS",
        54: "PI_CNTR_UNKNOWN_PARAMETER",
        55: "PI_CNTR_NO_REP_RECORDED",
        56: "PI_CNTR_INVALID_PASSWORD",
        57: "PI_CNTR_INVALID_RECORDER_CHAN",
        58: "PI_CNTR_INVALID_RECORDER_SRC_OPT",
        59: "PI_CNTR_INVALID_RECORDER_SRC_CHAN",
        60: "PI_CNTR_PARAM_PROTECTION",
        61: "PI_CNTR_AUTOZERO_RUNNING",
        62: "PI_CNTR_NO_LINEAR_AXIS",
        63: "PI_CNTR_INIT_RUNNING",
        64: "PI_CNTR_READ_ONLY_PARAMETER",
        65: "PI_CNTR_PAM_NOT_FOUND",
        66: "PI_CNTR_VOL_OUT_OF_LIMITS",
        67: "PI_CNTR_WAVE_TOO_LARGE",
        68: "PI_CNTR_NOT_ENOUGH_DDL_MEMORY",
        69: "PI_CNTR_DDL_TIME_DELAY_TOO_LARGE",
        70: "PI_CNTR_DIFFERENT_ARRAY_LENGTH",
        71: "PI_CNTR_GEN_SINGLE_MODE_RESTART",
        72: "PI_CNTR_ANALOG_TARGET_ACTIVE",
        73: "PI_CNTR_WAVE_GENERATOR_ACTIVE",
        74: "PI_CNTR_AUTOZERO_DISABLED",
        75: "PI_CNTR_NO_WAVE_SELECTED",
        76: "PI_CNTR_IF_BUFFER_OVERRUN",
        77: "PI_CNTR_NOT_ENOUGH_RECORDED_DATA",
        78: "PI_CNTR_TABLE_DEACTIVATED",
        79: "PI_CNTR_OPENLOOP_VALUE_SET_WHEN_SERVO_ON",
        80: "PI_CNTR_RAM_ERROR",
        81: "PI_CNTR_MACRO_UNKNOWN_COMMAND",
        82: "PI_CNTR_MACRO_PC_ERROR",
        83: "PI_CNTR_JOYSTICK_ACTIVE",
        84: "PI_CNTR_MOTOR_IS_OFF",
        85: "PI_CNTR_ONLY_IN_MACRO",
        86: "PI_CNTR_JOYSTICK_UNKNOWN_AXIS",
        87: "PI_CNTR_JOYSTICK_UNKNOWN_ID",
        88: "PI_CNTR_REF_MODE_IS_ON",
        89: "PI_CNTR_NOT_ALLOWED_IN_CURRENT_MOTION_MODE",
        90: "PI_CNTR_DIO_AND_TRACING_NOT_POSSIBLE",
        91: "PI_CNTR_COLLISION",
        92: "PI_CNTR_SLAVE_NOT_FAST_ENOUGH",
        93: "PI_CNTR_CMD_NOT_ALLOWED_WHILE_AXIS_IN_MOTION This command is not allowed",
        94: "PI_CNTR_OPEN_LOOP_JOYSTICK_ENABLED",
        95: "PI_CNTR_INVALID_SERVO_STATE_FOR_PARAMETER",
        96: "PI_CNTR_UNKNOWN_STAGE_NAME",
        100: "PI_LABVIEW_ERROR",
        200: "PI_CNTR_NO_AXIS",
        201: "PI_CNTR_NO_AXIS_PARAM_FILE",
        202: "PI_CNTR_INVALID_AXIS_PARAM_FILE",
        203: "PI_CNTR_NO_AXIS_PARAM_BACKUP",
        204: "PI_CNTR_RESERVED_204",
        205: "PI_CNTR_SMO_WITH_SERVO_ON",
        206: "PI_CNTR_UUDECODE_INCOMPLETE_HEADER",
        207: "PI_CNTR_UUDECODE_NOTHING_TO_DECODE",
        208: "PI_CNTR_UUDECODE_ILLEGAL_FORMAT",
        209: "PI_CNTR_CRC32_ERROR",
        210: "PI_CNTR_ILLEGAL_FILENAME",
        211: "PI_CNTR_FILE_NOT_FOUND",
        212: "PI_CNTR_FILE_WRITE_ERROR",
        213: "PI_CNTR_DTR_HINDERS_VELOCITY_CHANGE",
        214: "PI_CNTR_POSITION_UNKNOWN",
        215: "PI_CNTR_CONN_POSSIBLY_BROKEN",
        216: "PI_CNTR_ON_LIMIT_SWITCH",
        217: "PI_CNTR_UNEXPECTED_STRUT_STOP",
        218: "PI_CNTR_POSITION_BASED_ON_ESTIMATION",
        219: "PI_CNTR_POSITION_BASED_ON_INTERPOLATION",
        230: "PI_CNTR_INVALID_HANDLE",
        231: "PI_CNTR_NO_BIOS_FOUND",
        232: "PI_CNTR_SAVE_SYS_CFG_FAILED",
        233: "PI_CNTR_LOAD_SYS_CFG_FAILED",
        301: "PI_CNTR_SEND_BUFFER_OVERFLOW",
        302: "PI_CNTR_VOLTAGE_OUT_OF_LIMITS",
        303: "PI_CNTR_OPEN_LOOP_MOTION_SET_WHEN_SERVO_ON Open-loop motion attempted",
        304: "PI_CNTR_RECEIVING_BUFFER_OVERFLOW",
        305: "PI_CNTR_EEPROM_ERROR",
        306: "PI_CNTR_I2C_ERROR",
        307: "PI_CNTR_RECEIVING_TIMEOUT",
        308: "PI_CNTR_TIMEOUT",
        309: "PI_CNTR_MACRO_OUT_OF_SPACE",
        310: "PI_CNTR_EUI_OLDVERSION_CFGDATA",
        311: "PI_CNTR_EUI_INVALID_CFGDATA",
        333: "PI_CNTR_HARDWARE_ERROR",
        400: "PI_CNTR_WAV_INDEX_ERROR",
        401: "PI_CNTR_WAV_NOT_DEFINED",
        402: "PI_CNTR_WAV_TYPE_NOT_SUPPORTED",
        403: "PI_CNTR_WAV_LENGTH_EXCEEDS_LIMIT",
        404: "PI_CNTR_WAV_PARAMETER_NR",
        405: "PI_CNTR_WAV_PARAMETER_OUT_OF_LIMIT",
        406: "PI_CNTR_WGO_BIT_NOT_SUPPORTED",
        500: "PI_CNTR_EMERGENCY_STOP_BUTTON_ACTIVATED",
        501: "PI_CNTR_EMERGENCY_STOP_BUTTON_WAS_ACTIVATED",
        502: "PI_CNTR_REDUNDANCY_LIMIT_EXCEEDED",
        503: "PI_CNTR_COLLISION_SWITCH_ACTIVATED",
        504: "PI_CNTR_FOLLOWING_ERROR",
        555: "PI_CNTR_UNKNOWN_ERROR",
        601: "PI_CNTR_NOT_ENOUGH_MEMORY",
        602: "PI_CNTR_HW_VOLTAGE_ERROR",
        603: "PI_CNTR_HW_TEMPERATURE_ERROR",
        604: "PI_CNTR_POSITION_ERROR_TOO_HIGH",
        606: "PI_CNTR_INPUT_OUT_OF_RANGE",
        1000: "PI_CNTR_TOO_MANY_NESTED_MACROS",
        1001: "PI_CNTR_MACRO_ALREADY_DEFINED",
        1002: "PI_CNTR_NO_MACRO_RECORDING",
        1003: "PI_CNTR_INVALID_MAC_PARAM",
        1004: "PI_CNTR_RESERVED_1004",
        1005: "PI_CNTR_CONTROLLER_BUSY",
        1006: "PI_CNTR_INVALID_IDENTIFIER",
        1007: "PI_CNTR_UNKNOWN_VARIABLE_OR_ARGUMENT",
        1008: "PI_CNTR_RUNNING_MACRO",
        1009: "PI_CNTR_MACRO_INVALID_OPERATOR",
        1063: "PI_CNTR_EXT_PROFILE_UNALLOWED_CMD",
        1064: "PI_CNTR_EXT_PROFILE_EXPECTING_MOTION_ERROR",
        1065: "PI_CNTR_PROFILE_ACTIVE",
        1066: "PI_CNTR_PROFILE_INDEX_OUT_OF_RANGE",
        1071: "PI_CNTR_PROFILE_OUT_OF_MEMORY",
        1072: "PI_CNTR_PROFILE_WRONG_CLUSTER",
        1073: "PI_CNTR_PROFILE_UNKNOWN_CLUSTER_IDENTIFIER",
        2000: "PI_CNTR_ALREADY_HAS_SERIAL_NUMBER",
        4000: "PI_CNTR_SECTOR_ERASE_FAILED",
        4001: "PI_CNTR_FLASH_PROGRAM_FAILED",
        4002: "PI_CNTR_FLASH_READ_FAILED",
        4003: "PI_CNTR_HW_MATCHCODE_ERROR",
        4004: "PI_CNTR_FW_MATCHCODE_ERROR",
        4005: "PI_CNTR_HW_VERSION_ERROR",
        4006: "PI_CNTR_FW_VERSION_ERROR",
        4007: "PI_CNTR_FW_UPDATE_ERROR",
        4008: "PI_CNTR_FW_CRC_PAR_ERROR",
        4009: "PI_CNTR_FW_CRC_FW_ERROR",
        5000: "PI_CNTR_INVALID_PCC_SCAN_DATA",
        5001: "PI_CNTR_PCC_SCAN_RUNNING",
        5002: "PI_CNTR_INVALID_PCC_AXIS",
        5003: "PI_CNTR_PCC_SCAN_OUT_OF_RANGE",
        5004: "PI_CNTR_PCC_TYPE_NOT_EXISTING",
        5005: "PI_CNTR_PCC_PAM_ERROR",
        5006: "PI_CNTR_PCC_TABLE_ARRAY_TOO_LARGE",
        5100: "PI_CNTR_NEXLINE_ERROR",
        5101: "PI_CNTR_CHANNEL_ALREADY_USED",
        5102: "PI_CNTR_NEXLINE_TABLE_TOO_SMALL",
        5103: "PI_CNTR_RNP_WITH_SERVO_ON",
        5104: "PI_CNTR_RNP_NEEDED",
        5200: "PI_CNTR_AXIS_NOT_CONFIGURED",
    }

    def __init__(self, host, port=50000, device_id=None, config=None):
        self.channel_mapping = MutableBidict()
        self.valid_commands = []
        super().__init__(host, port, device_id, config)

    def _init_attributes(self):
        super()._init_attributes()
        self.create_attribute(ATTR_SERIAL_NUMBER, readonly=True)
        self.create_attribute(ATTR_CHANNELS, readonly=True, default_type=np.uint16)
        self.create_attribute(
            ATTR_SYNTAX_VERSION, readonly=True, default_type=np.float16, decimals=3
        )
        self.create_attribute(ATTR_POSITIONS, readonly=True)
        self.create_attribute(
            ATTR_TRIGGER_OUTPUTS_COUNT, readonly=True, default_type=np.uint16
        )
        self.create_attribute(
            ATTR_WAVE_GEN_COUNT, readonly=True, default_type=np.uint16
        )
        self.create_attribute(
            ATTR_SERVO_UPDATE_TIME,
            readonly=True,
            default_type=np.float64,
            decimals=12,
            unit="ms",
        )

    def valid_command_format(self, command):
        return command is not None and command[-1] == "\n"

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

        self.command("ERR?\n")
        # Get PI serial number
        self.command("IDN?\n")
        # Get PI syntax version
        self.command("CSV?\n")
        # Get available commands
        self.command("HLP?\n")
        # Get Channels configuration
        self.get_memory_parameters([SERVO_UPDATE_TIME_PARAM])
        self.get_configuration_of_trigger_outputs(callback=self._set_trigger_output)
        self.get_wave_generator_mode(callback=self._set_wave_generators)
        self.command("SAI?\n", callback=_finish_configuration)

    def _set_trigger_output(self, output):
        output = "".join(output).split(" \n")
        trigger_output_count = 0
        for line in output:
            trigger_output, value = line.split(" ")
            attribute, value = value.split("=")

            attribute = trigger_output_config.inv.get(int(attribute), None)
            if attribute is not None:
                trigger_output = int(trigger_output) - 1
                trigger_group_name = "Trigger output {}".format(trigger_output)

                if self.attributes.get(trigger_group_name) is None:
                    self.attributes[trigger_group_name] = {}
                    trigger_output_count += 1

                self.create_attribute(
                    ATTR_TRIGGER_LINE_DATA, trigger_group_name, readonly=True
                )
                set_attribute = lambda value, parameter=attribute, trigger_output=trigger_output: self.set_configuration_of_trigger_output(
                    trigger_output, parameter, value
                )
                if attribute == TRIG_OUTPUT_AXIS:
                    set_attribute = lambda value, parameter=attribute, trigger_output=trigger_output: self.set_configuration_of_trigger_output(
                        trigger_output, parameter, int(value) + 1
                    )
                    self.create_attribute(
                        attribute,
                        trigger_group_name,
                        default_value=int(value) - 1,
                        default_type=np.uint16,
                        set_function=set_attribute,
                    )
                elif attribute == TRIG_OUTPUT_MODE:
                    self.create_attribute(
                        attribute,
                        trigger_group_name,
                        default_value=trigger_output_mode.inv.get(int(value)),
                        default_type=list(trigger_output_mode.keys()),
                        set_function=set_attribute,
                    )
                else:
                    self.create_attribute(
                        attribute,
                        trigger_group_name,
                        default_value=float(value),
                        default_type=np.float64,
                        decimals=12,
                        set_function=set_attribute,
                    )

        self.set_value(ATTR_TRIGGER_OUTPUTS_COUNT, trigger_output_count)

    def _set_wave_generators(self, output):
        output = "".join(output).split(" \n")
        for line in output:
            generator_id, mode = line.split("=")
            generator_id = int(generator_id) - 1
            mode = int(mode)
            generator_group_name = "Wave generator {}".format(generator_id)
            self.create_attribute(
                ATTR_STATUS,
                generator_group_name,
                default_value=STATUS_IDLE,
                readonly=True,
            )
            self.create_attribute(
                ATTR_WAVETABLE_DATA, generator_group_name, readonly=True
            )
            self.create_attribute(
                ATTR_RECORD_TABLE_DATA, generator_group_name, readonly=True
            )
            self.create_attribute(
                ATTR_PRESCAN_PIXELS,
                generator_group_name,
                default_value=0,
                default_type=np.uint,
                readonly=True,
            )
            self.create_attribute(
                ATTR_POSTSCAN_PIXELS,
                generator_group_name,
                default_value=0,
                default_type=np.uint,
                readonly=True,
            )
            self.create_attribute(
                ATTR_RECORDED_POSITIONS,
                generator_group_name,
                default_type=TYPE_ARRAY,
                readonly=True,
            )
            self.create_attribute(
                ATTR_WAVETABLE_LENGTH,
                generator_group_name,
                readonly=True,
                default_type=np.uint32,
            )
            set_function = (
                lambda offset, gen_id=generator_id: self.set_wave_gen_output_offset(
                    gen_id, offset
                )
            )
            self.create_attribute(
                ATTR_WAVETABLE_OFFSET,
                generator_group_name,
                readonly=False,
                decimals=12,
                default_type=np.float64,
                set_function=set_function,
            )
            self.create_attribute(
                ATTR_WAVE_TABLE,
                generator_group_name,
                readonly=True,
                default_type=np.uint32,
            )

            set_function = lambda table_rate, gen_id=generator_id: self.set_wave_generator_rate_and_interpolation_type(
                gen_id, wave_table_rate=table_rate
            )
            self.create_attribute(
                ATTR_WAVETABLE_RATE,
                generator_group_name,
                default_type=np.uint32,
                set_function=set_function,
            )

            set_function = lambda interpolation_type, gen_id=generator_id: self.set_wave_generator_rate_and_interpolation_type(
                gen_id, interpolation_type=interpolation_type
            )
            self.create_attribute(
                ATTR_WAVETABLE_INTERPOLATION,
                generator_group_name,
                default_type=list(data_interpolation.keys()),
                set_function=set_function,
            )

        self.set_value(ATTR_WAVE_GEN_COUNT, len(output))
        self.get_wave_generator_rate_and_interpolation_type()
        self.get_wave_gen_output_offset()
        self.get_connected_table_to_generator()

    def found_terminator(self):
        if len(self.buffer) == 0:
            return
        elif self.buffer[-1][-1] == " ":
            self.buffer[-1] += self.terminator.decode()
        else:
            super().found_terminator()

    def collect_incoming_data(self, data: bytes) -> None:
        self.buffer.append(data.decode("latin-1"))

    def command(self, command, callback=None, with_token=False, returning=True):
        # Send requested format
        out = super().command(
            command, callback=callback, with_token=with_token, returning=True
        )
        # Send command to check for possible error immediately after
        if not returning:
            super().command(
                "ERR?\n", callback=None, with_token=with_token, returning=False
            )
        return out

    def handle_readout(self, readout_buffer):
        command, output, callback, token = super().handle_readout(readout_buffer)
        is_error_message = self.error_pattern.match(output)
        if is_error_message is not None:
            error_code = int(is_error_message.group(0))
            if command == "ERR?\n" and error_code != 0:
                readout_buffer = self.error_description.get(error_code, "Unknown error")
                self.handle_command_error(command, readout_buffer)
                command = RESPONSE_ERROR
            elif command not in ("#5\n", "#9\n", "STP\n") and error_code != 0:
                command = RESPONSE_ERROR
                readout_buffer = self.error_description.get(error_code, "Unknown error")
                self.handle_command_error(command, readout_buffer)

        if command == "IDN?\n":
            self.set_raw_value(ATTR_SERIAL_NUMBER, "{}".format(output))
        elif command == "SAI?\n":
            for channel_id in output.split(" \n"):
                try:
                    self.channel_mapping[channel_id] = len(self.channel_mapping)
                except bidict._exc.KeyAndValueDuplicationError:
                    continue
            self.set_raw_value(ATTR_CHANNELS, len(self.channel_mapping))
        elif command == "CSV?\n":
            self.set_raw_value(ATTR_SYNTAX_VERSION, float(output))
        elif command == "HLP?\n":
            for valid_command in output.split("\n")[1:-1]:
                cmd, _desc = valid_command.split(" - ")
                self.valid_commands.append(cmd)
        elif command == "#5\n":
            stat = int(output)
            for channel in range(0, self.get_value(ATTR_CHANNELS)):
                self.notify((channel, ATTR_MOVING), bool(stat & (1 << channel)))
        elif command == "#9\n":
            stat = int(output)
            for generator_id in range(0, self.get_value(ATTR_WAVE_GEN_COUNT)):
                state = bool(stat & (1 << generator_id))
                if (
                    not state
                    and self.get_value(
                        ("Wave generator {}".format(generator_id), ATTR_STATUS)
                    )
                    == STATUS_BUSY
                ):
                    self.get_recorder_data(generator_id)
                self.set_raw_value(
                    ("Wave generator {}".format(generator_id), ATTR_STATUS),
                    STATUS_BUSY if state else STATUS_IDLE,
                )
                trigger_axis = self.get_value(
                    ("Trigger output {}".format(generator_id), TRIG_OUTPUT_AXIS)
                )
                self.notify((trigger_axis, ATTR_SCANNING), state)
            if stat == 0:
                self.set_status(STATUS_IDLE)
            else:
                self.set_status(STATUS_BUSY)
        elif "PUN?" in command:
            channel, unit = output.split("=")
            self.notify((self.channel_mapping[channel], ATTR_ENCODER_BASE_UNIT), unit)
        elif "POS?" in command:
            positions = output.split(" \n")
            positions_list = []
            for position in positions:
                channel, position = position.split("=")
                positions_list.append(position)
                self.notify(
                    (self.channel_mapping[channel], ATTR_POSITION), float(position)
                )
            self.set_raw_value(ATTR_POSITIONS, " ".join(positions_list))
        elif "FRF?" in command:
            channel, flag = output.split("=")
            self.notify(
                (self.channel_mapping[channel], ATTR_REFERENCED), bool(int(flag))
            )
        elif "SVO?" in command:
            channel, flag = output.split("=")
            self.notify(
                (self.channel_mapping[channel], ATTR_SERVO_STATE), bool(int(flag))
            )
        elif "TMN?" in command:
            channel, position = output.split("=")
            self.notify(
                (self.channel_mapping[channel], ATTR_POSITION_LOWER_LIMIT),
                float(position),
            )
        elif "TMX?" in command:
            channel, position = output.split("=")
            self.notify(
                (self.channel_mapping[channel], ATTR_POSITION_UPPER_LIMIT),
                float(position),
            )
        elif "VEL?" in command:
            channel, velocity = output.split("=")
            self.notify((self.channel_mapping[channel], ATTR_VELOCITY), float(velocity))
        elif "WOS?" in command:
            lines = output.split(" \n")
            for line in lines:
                generator_id, generator_offset = line.split("=")
                self.set_raw_value(
                    [
                        "Wave generator {}".format(int(generator_id) - 1),
                        ATTR_WAVETABLE_OFFSET,
                    ],
                    float(generator_offset),
                )
        elif "WSL?" in command:
            lines = output.split(" \n")
            for line in lines:
                generator_id, wave_table_id = line.split("=")
                self.set_raw_value(
                    [
                        "Wave generator {}".format(int(generator_id) - 1),
                        ATTR_WAVE_TABLE,
                    ],
                    int(wave_table_id),
                )
        elif "WTR?" in command:
            lines = output.split(" \n")
            for line in lines:
                generator_id, rate_interpolation = line.split("=")
                rate, interpolation = rate_interpolation.split(" ")
                interpolation = data_interpolation.inv.get(int(interpolation))
                if int(generator_id) == 0:
                    for generator_id in range(self.get_value(ATTR_WAVE_GEN_COUNT)):
                        self.set_raw_value(
                            [
                                "Wave generator {}".format(generator_id),
                                ATTR_WAVETABLE_RATE,
                            ],
                            int(rate),
                        )
                        self.set_raw_value(
                            [
                                "Wave generator {}".format(generator_id),
                                ATTR_WAVETABLE_INTERPOLATION,
                            ],
                            interpolation,
                        )
                else:
                    self.set_raw_value(
                        [
                            "Wave generator {}".format(int(generator_id) - 1),
                            ATTR_WAVETABLE_RATE,
                        ],
                        int(rate),
                    )
                    self.set_raw_value(
                        [
                            "Wave generator {}".format(int(generator_id) - 1),
                            ATTR_WAVETABLE_INTERPOLATION,
                        ],
                        interpolation,
                    )
        elif "SEP?" in command:
            lines = output.split(" \n")
            for line in lines:
                parameter, value = line.split("=")
                _, parameter = parameter.split(" ")

                if parameter == SERVO_UPDATE_TIME_PARAM:
                    self.set_raw_value(ATTR_SERVO_UPDATE_TIME, float(value) * 1e3)
        elif "GWD?" in command:
            lines = output.split(" \n")
            wave_table_id = int(lines[5][-1])
            wave_table_data = ", ".join(lines[7:])
            generator_id = wave_table_id - 1
            self.set_raw_value(
                ["Wave generator {}".format(generator_id), ATTR_WAVETABLE_DATA],
                wave_table_data,
            )
        elif "TWS?" in command:
            lines = output.split(" \n")
            cmd, _start, _end, trigger_output = command.split(" ")
            trigger_group_name = "Trigger output {}".format(int(trigger_output) - 1)
            triggers_level = ", ".join(lines[6:])
            self.set_raw_value(
                [trigger_group_name, ATTR_TRIGGER_LINE_DATA], triggers_level
            )
        elif "DRR?" in command:
            lines = output.split(" \n")
            wave_table_id = int(lines[5][-1])
            generator_id = wave_table_id - 1

            wto = self[f"Wave generator {generator_id}"][ATTR_WAVETABLE_OFFSET]

            recorded_data = []
            for i in range(0, len(lines[7:])):
                fixed_position = wto.remove_offset_factor(float(lines[7 + i]))
                recorded_data.append(fixed_position)

            trigger_group_name = "Trigger output {}".format(generator_id)
            self.set_raw_value(
                ["Wave generator {}".format(generator_id), ATTR_RECORD_TABLE_DATA],
                recorded_data,
            )
            trigger_line = [
                int(i)
                for i in self.get_value(
                    [trigger_group_name, ATTR_TRIGGER_LINE_DATA]
                ).split(",")
            ]
            trigger_positions = [
                recorded_data[index]
                for index, trigger in enumerate(trigger_line)
                if trigger
            ]
            self.set_raw_value(
                ["Wave generator {}".format(generator_id), ATTR_RECORDED_POSITIONS],
                trigger_positions,
            )

            channel = self.get_value([trigger_group_name, "Trigger axis"])
            self.notify((channel, ATTR_RECORD_TABLE_DATA), recorded_data)
            self.notify((channel, ATTR_RECORDED_POSITIONS), trigger_positions)
        if callback is not None:
            self.handle_readout_callback(callback, command, readout_buffer)
        if token:
            kamzik3.session.publisher.push_message(
                self.device_id, [command, readout_buffer], token
            )
            for observer in self._observers[:]:
                if isinstance(observer, DevicePiChannel):
                    kamzik3.session.publisher.push_message(
                        observer.device_id, [command, readout_buffer], token
                    )

    def start_polling(self):
        super().start_polling()
        self.poll_command("POS?\n", 200)
        self.poll_command("#5\n", 200)
        self.poll_command("#9\n", 300)

    def get_memory_parameters(self, list_of_parameters, callback=None):
        assert isinstance(list_of_parameters, list)
        attributes = " ".join(
            [
                " ".join(c)
                for c in zip(
                    [str(b + 1) for b in range(len(list_of_parameters))],
                    list_of_parameters,
                )
            ]
        )
        return self.command(
            "SEP? {}\n".format(attributes), with_token=True, callback=callback
        )

    def clear_wave_table(self, wave_table_id):
        """
        Clears the content of the given wave table

        As long as a wave generator is running, it is not
        possible to clear the connected wave table.

        :param wave_table_id: int
        :return:
        """
        self.logger.info("Clearing wave table generator {}".format(wave_table_id))
        return self.command(
            "WCL {}\n".format(wave_table_id + 1), with_token=True, returning=False
        )

    def clear_wave_table_triggers(self):
        """
        Here comes a short description of clear_wave_table_triggers.

        Clears all output trigger settings for the wave
        generators (the settings made with TWS by
        switching the signal state for all points to "low".

        :return:
        """
        self.logger.info("Clearing all wave table triggers")
        return self.command("TWC\n", with_token=True, returning=False)

    def get_wave_generator_rate_and_interpolation_type(self, callback=None):
        """
        Here comes a short description of get_wave_generator_rate_and_interpolation_type.

        Gets the current wave generator table rate, i.e. the
        number of servo-loop cycles used by the wave
        generator to output one waveform point (Wave
        Generator Table Rate parameter value in volatile
        memory (ID 0x13000109)). Gets also the interpolation
        type used with table rate values > 1

        :param callback:
        :return:
        """
        return self.command("WTR?\n", with_token=True, callback=callback)

    def set_wave_generator_rate_and_interpolation_type(
        self,
        wave_generator_id=0,
        wave_table_rate=None,
        interpolation_type=None,
        callback=None,
    ):
        """
        Set wave generator interpolation type.

        :param wave_generator_id: int
        :param wave_table_rate: int
        :param interpolation_type: int
        :param callback:
        :type interpolation_type: 0 = no interpolation, 1 = straight line (default)
        :return:
        """
        if wave_table_rate is None:
            wave_table_rate = self.get_value(
                ["Wave generator {}".format(wave_generator_id), ATTR_WAVETABLE_RATE]
            )
        if interpolation_type is None:
            interpolation_type = self.get_value(
                [
                    "Wave generator {}".format(wave_generator_id),
                    ATTR_WAVETABLE_INTERPOLATION,
                ]
            )
        interpolation_type = data_interpolation.get(interpolation_type)
        self.logger.info(
            "Set wave generator interpolation type to {}".format(wave_generator_id)
        )
        output = self.command(
            "WTR {} {} {}\n".format(
                wave_generator_id, int(wave_table_rate), interpolation_type
            ),
            returning=False,
            with_token=True,
            callback=callback,
        )
        self.get_wave_generator_rate_and_interpolation_type()
        return output

    def get_wave_gen_cycles(self, wave_generator_id, callback=None):
        """
        Gets the number of output cycles set for the given wave generator.

        :param wave_generator_id: int
        :param callback:
        """
        return self.command(
            "WGC? {}\n".format(wave_generator_id + 1),
            with_token=True,
            callback=callback,
        )

    def set_wave_gen_cycles(self, wave_generator_id, cycles, callback=None):
        """
        Gets the number of output cycles set for the given wave generator.

        :param wave_generator_id: int
        :param cycles: int
        :param callback:
        """
        self.logger.info(
            "Set wave generator {} cycles to {}".format(wave_generator_id, cycles)
        )
        return self.command(
            "WGC {} {}\n".format(wave_generator_id + 1, cycles),
            returning=False,
            with_token=True,
            callback=callback,
        )

    def get_wave_gen_output_offset(self, wave_generator_id=None, callback=None):
        """
        Here comes a short description of get_wave_gen_output_offset.

        Reads the current value of the offset which is added to
        the wave generator output (Wave Offset parameter
        value in volatile memory (ID 0x1300010b)). This value
        results either from WOS (p. 97) / SPA (p. 65) / SEP
        (p. 62) settings, or from internal calculation during the
        wave generator output; see WOS for details.

        :param wave_generator_id: int
        :param callback:
        :return:
        """
        if wave_generator_id is None:
            return self.command("WOS?\n", with_token=True, callback=callback)
        else:
            return self.command(
                "WOS? {}\n".format(wave_generator_id + 1),
                with_token=True,
                callback=callback,
            )

    def set_wave_gen_output_offset(self, wave_generator_id, offset, callback=None):
        """
        Here comes a short description of set_wave_gen_output_offset.

        Sets an offset to the output of a wave generator. The
        current wave generator output is then created by
        adding the offset value to the current wave value:
        Generator Output = Offset + Current Wave Value

        :param wave_generator_id:
        :param offset:
        :param callback:
        :return:
        """
        self.logger.info(
            "Set wave generator {} offset to {}".format(wave_generator_id, offset)
        )
        return self.command(
            "WOS {} {}\n".format(wave_generator_id + 1, offset),
            returning=False,
            with_token=True,
            callback=callback,
        )

    def get_connected_table_to_generator(self, wave_generator_id=None, callback=None):
        if wave_generator_id is None:
            return self.command("WSL?\n", with_token=True, callback=callback)
        else:
            return self.command(
                "WSL? {}\n".format(wave_generator_id + 1),
                with_token=True,
                callback=callback,
            )

    def set_connected_table_to_generator(
        self, wave_generator_id, wave_table_id, callback=None
    ):
        self.logger.info(
            "Set connected generator {} to table {}".format(
                wave_generator_id, wave_table_id
            )
        )
        return self.command(
            "WSL {} {}\n".format(wave_generator_id + 1, wave_table_id + 1),
            returning=False,
            with_token=True,
            callback=callback,
        )

    def get_configuration_of_trigger_outputs(self, callback=None):
        return self.command("CTO?\n", with_token=True, callback=callback)

    def set_configuration_of_trigger_output(
        self, trigger_output, parameter, value, callback=None
    ):
        self.logger.info(
            "Set trigger output {} parameter {} = {}".format(
                trigger_output, parameter, value
            )
        )
        if parameter == TRIG_OUTPUT_MODE:
            value = trigger_output_mode.get(value)
        parameter = trigger_output_config.get(parameter)
        return self.command(
            "CTO {} {} {}\n".format(trigger_output + 1, parameter, value),
            returning=False,
            with_token=True,
            callback=callback,
        )

    def set_wave_generator_mode(self, generator_id, start_mode, callback=None):
        return self.command(
            "WGO {} {}\n".format(generator_id + 1, start_mode),
            returning=False,
            with_token=True,
            callback=callback,
        )

    def get_wave_generator_mode(self, generator_id=None, callback=None):
        if generator_id is None:
            return self.command("WGO?\n", with_token=True, callback=callback)
        else:
            return self.command(
                "WGO? {}\n".format(generator_id + 1), with_token=True, callback=callback
            )

    def set_trigger_line(self, trigger_output, trigger_line_params, callback=None):
        """
        Here comes a short description of set_trigger_line.

        :param trigger_output: int
        :param trigger_line_params: list
        :param callback:
        :type trigger_line_params: [(PointNumber, Switch), (...), ...]
        :return:
        """
        sliced = 0
        trigger_appendix = (trigger_output + 1,)
        prepared_command = None
        while sliced <= len(trigger_line_params):
            if prepared_command is not None:
                self.command(prepared_command, returning=False)

            sliced_params = trigger_line_params[sliced : sliced + self.N_TRIG_PER_CMD]
            params = " ".join(
                [
                    " ".join([str(b) for b in trigger_appendix + a])
                    for a in sliced_params
                ]
            )
            prepared_command = "TWS {}\n".format(params)
            sliced += self.N_TRIG_PER_CMD

        if prepared_command is not None:
            return self.command(
                prepared_command, returning=False, with_token=True, callback=callback
            )

    def get_trigger_line(
        self, trigger_output, start_point=1, number_of_points=None, callback=None
    ):
        if number_of_points is None:
            number_of_points = self.get_value(
                ["Wave generator {}".format(trigger_output), ATTR_WAVETABLE_LENGTH]
            )
        return self.command(
            "TWS? {} {} {}\n".format(start_point, number_of_points, trigger_output + 1),
            with_token=True,
            callback=callback,
        )

    def get_wavetable_data(
        self, wave_table_id, start_point=1, number_of_points=None, callback=None
    ):
        if number_of_points is None:
            number_of_points = self.get_value(
                ["Wave generator {}".format(wave_table_id), ATTR_WAVETABLE_LENGTH]
            )
        return self.command(
            "GWD? {} {} {}\n".format(start_point, number_of_points, wave_table_id + 1),
            with_token=True,
            callback=callback,
        )

    def set_wave_form_definition(
        self, wave_table_id, wave_add_method, wave_type, wave_type_param, callback=None
    ):
        if wave_type == WAVE_TYPE_PNT:
            # In this case we need (WaveStartPoint, WaveLength, (WavePoints))
            command_parameter = wave_type_param[0]
            points = wave_type_param[2]

            sliced = 0
            prepared_command = None

            def _make_command(command, command_parameter, sliced_points):
                joined_points = " ".join("%.6f" % point for point in sliced_points)
                return "{} {} {} {}\n".format(
                    command, command_parameter, len(sliced_points), joined_points
                )

            # sliced_points is not defined and its type is not obvious (same type as
            # points). Disable this for now.
            # pylint: disable=used-before-assignment
            while sliced <= len(points):
                if prepared_command is not None:
                    self.command(
                        _make_command(
                            prepared_command, command_parameter, sliced_points
                        ),
                        returning=False,
                    )
                if sliced > 0:
                    wave_add_method = WAVE_TYPE_APPEND

                prepared_command = "WAV %s %s %s" % (
                    wave_table_id + 1,
                    wave_add_method,
                    wave_type,
                )
                sliced_points = points[sliced : sliced + self.N_WAV_POINTS_PER_CMD]
                sliced += self.N_WAV_POINTS_PER_CMD

            if prepared_command is not None:
                return self.command(
                    _make_command(prepared_command, command_parameter, sliced_points),
                    returning=False,
                    with_token=True,
                    callback=callback,
                )

        elif wave_type == WAVE_TYPE_SINP:
            # In this case we need (SegLength, Amp, Offset, WaveLength, StartPoint, CurveCenterPoint)
            command_parameter = "%i %f %f %i %i %i" % wave_type_param
        elif wave_type == WAVE_TYPE_RAMP:
            # In this case we need (SegLength, Amp, Offset, WaveLength, StartPoint, SpeedUpDown, CurveCenterPoint)
            command_parameter = "%i %f %f %i %i %i %i" % wave_type_param
        elif wave_type == WAVE_TYPE_LIN:
            # In this case we need (SegLength, Amp, Offset, WaveLength, StartPoint, SpeedUpDown)
            command_parameter = "%i %f %f %i %i %i" % wave_type_param

        command = "WAV %s %s %s" % (wave_table_id + 1, wave_add_method, wave_type)
        return self.command(
            "%s %s\n" % (command, command_parameter),
            returning=False,
            with_token=True,
            callback=callback,
        )

    def set_record_table_rate(self, rate, callback=None):
        """
        Here comes a short description of set_record_table_rate.

        Sets the record table rate, i.e. the number of servo-loop
        cycles to be used in data recording operations. Settings
        larger than 1 make it possible to cover longer time
        periods.

        :param rate: int
        :param callback:
        :return:
        """
        return self.command(
            "RTR {}\n".format(int(rate)),
            returning=False,
            with_token=True,
            callback=callback,
        )

    def set_recorded_configuration(self, table_id, source, option, callback=None):
        """
        Here comes a short description of set_recorded_configuration.

        Set data recorder configuration: determines the data
        source and the kind of data (RecordOption) used for
        the given data recorder table.

        :param table_id:
        :param source:
        :param option:
        :param callback:
        :return:
        """
        return self.command(
            "DRC {} {} {}\n".format(table_id + 1, source + 1, option),
            returning=False,
            with_token=True,
            callback=callback,
        )

    def get_recorder_data(
        self, table_id, start_point=1, number_of_points=None, callback=None
    ):
        if number_of_points is None:
            number_of_points = self.get_value(
                ["Wave generator {}".format(table_id), ATTR_WAVETABLE_LENGTH]
            )
        return self.command(
            "DRR? {} {} {}\n".format(start_point, number_of_points, table_id + 1),
            with_token=True,
            callback=callback,
        )

    def set_recorded_trigger_source(self, table_id, source, value, callback=None):
        """
        Here comes a short description of set_recorded_configuration.

        Set data recorder configuration: determines the data
        source and the kind of data (RecordOption) used for
        the given data recorder table.

        :param table_id:
        :param source:
        :param value:
        :param callback:
        :return:
        """
        return self.command(
            "DRT {} {} {}\n".format(table_id + 1, source, value),
            returning=False,
            with_token=True,
            callback=callback,
        )

    def _move_absolute(self, channel, position, callback=None):
        self.logger.info(
            "Move channel {} to absolute position {}".format(channel, position)
        )
        return self.command(
            "MOV {} {}\n".format(channel + 1, position),
            callback,
            with_token=True,
            returning=False,
        )

    @expose_method({"generator_id": "0"})
    def start_fly_scan(self, generator_id):
        self.set_wave_generator_mode(int(generator_id), 1)
        self.command("#9\n")

    @expose_method(
        {
            "channel": "0",
            "center": "Center of scan",
            "step_size": "steps size",
            "pixels": "Scan points",
            "dwell_time": "usec",
            "trigger_mode": "0",
            "interpolating": "0",
        }
    )
    def set_fly_scan(
        self,
        channel=0,
        center=50,
        step_size=1,
        pixels=10,
        dwell_time=100,
        trigger_mode=TRIG_MODE_GENERATOR,
        interpolating=False,
    ):
        self.stop_polling()
        self.set_status(STATUS_BUSY)
        channel = int(channel)
        center = float(center)

        step_size = float(step_size)
        pixels = int(pixels)
        dwell_time = float(dwell_time)
        # trigger_mode = int(trigger_mode)
        interpolating = bool(int(interpolating))

        generator_id = None
        for trigger_id in range(self.get_value(ATTR_TRIGGER_OUTPUTS_COUNT)):
            trigger_axis = self.get_value(
                ("Trigger output {}".format(trigger_id), TRIG_OUTPUT_AXIS)
            )
            if trigger_axis == channel:
                generator_id = trigger_id
                break

        wto = self[f"Wave generator {generator_id}"][ATTR_WAVETABLE_OFFSET]
        center = wto.remove_offset_factor(center)

        if generator_id is None:
            raise DeviceError("Cannot find trigger output bound to selected channel")

        # Clear wave table and all triggers
        self.clear_wave_table(generator_id)
        self.clear_wave_table_triggers()
        # Calculate setpoints, dwell time and offsets
        fly_scan_params = self._prepare_fly_scan_parameters(
            center, step_size, pixels, dwell_time, trigger_mode
        )
        (
            dwell_time,
            start_position,
            setpoints,
            pre_scan_pixels,
            post_scan_pixels,
            total_pixels,
            pixels,
        ) = fly_scan_params
        self.set_value(
            ["Wave generator {}".format(generator_id), ATTR_PRESCAN_PIXELS],
            pre_scan_pixels,
        )
        self.set_value(
            ["Wave generator {}".format(generator_id), ATTR_POSTSCAN_PIXELS],
            post_scan_pixels,
        )
        # Set interpolation and table rate
        interpolation_type = INTERPOLATION_LINE if interpolating else INTERPOLATION_NONE
        wave_table_rate = dwell_time / self.get_value(ATTR_SERVO_UPDATE_TIME)
        self.set_wave_generator_rate_and_interpolation_type(
            wave_table_rate=wave_table_rate, interpolation_type=interpolation_type
        )
        # Set wave generator cycles
        self.set_wave_gen_cycles(generator_id, 1)

        # Set recorder table rate
        self.set_record_table_rate(int(wave_table_rate))
        self.set_value(
            ["Wave generator {}".format(generator_id), ATTR_WAVETABLE_LENGTH],
            total_pixels,
        )
        self.set_wave_form_definition(
            generator_id,
            WAVE_TYPE_START,
            WAVE_TYPE_PNT,
            (1, total_pixels + 50, setpoints),
        )
        # Set generator offset to start position

        self.set_wave_gen_output_offset(generator_id, start_position)
        # Connect generator to wave table
        self.set_connected_table_to_generator(generator_id, generator_id)

        if trigger_mode == TRIG_MODE_GENERATOR:
            self.set_configuration_of_trigger_output(
                generator_id, TRIG_OUTPUT_MODE, TRIG_MODE_GENERATOR
            )
            trigger_points_count = int(pixels / 2 + 1)
            trigger_points = []
            for j in range(trigger_points_count):
                trigger_points.append(((pre_scan_pixels + j * 2) + 1, 1))
            self.set_trigger_line(generator_id, trigger_points)
            self.get_trigger_line(generator_id, 1, total_pixels)
        elif trigger_mode == TRIG_MODE_POSITION_DISTANCE:
            self.set_configuration_of_trigger_output(
                generator_id, TRIG_OUTPUT_MODE, TRIG_MODE_POSITION_DISTANCE
            )
            self.set_configuration_of_trigger_output(
                generator_id, TRIG_START, start_position
            )
            # We need to set stop position to + 1 pixel to stop last trigger
            self.set_configuration_of_trigger_output(
                generator_id, TRIG_STOP, step_size * (pixels + 1)
            )

        self.set_recorded_configuration(
            generator_id, generator_id, REC_CURRENT_POSITION
        )
        self.set_recorded_trigger_source(generator_id, 0, 0)
        self._move_absolute(channel, start_position)

        self.get_wavetable_data(generator_id, 1, total_pixels)
        self.get_wave_gen_output_offset(generator_id)
        self.set_status(STATUS_IDLE)
        self.start_polling()
        self.notify((channel, ATTR_WAVE_GENERATOR), generator_id)
        return generator_id

    def _prepare_fly_scan_parameters(
        self, center, step_size, pixels, dwell_time, trigger_mode
    ):
        j = 0
        # set motion parameters
        acceleration_speed = 0.02  # the value of acceleration and deceleration
        fly_back_speed = 0.2  # the maximum speed on the way back
        line_dwell = 0  # 12 the time to wait at the beginning of each line (after flyback mainly)
        drift_pixels = 2  # the number of pixels after acceleration and before taking data; 2 pixels should be enough for anything to settle down

        def forHelper(j, k, condition_callback, positions, callback, null_J=True):
            if null_J:
                j = 0
            while condition_callback(j, k):
                positions[k] = callback(j, k)
                j += 1
                k += 1
            return j, k

        if (
            trigger_mode == TRIG_MODE_GENERATOR
        ):  # we need 2 points of the wave generator for a full trigger_mode period, so let's cut every pixel in half
            step_size /= 2
            pixels *= 2
            dwell_time /= 2
            drift_pixels *= 2

        # adjust to max speed
        dwell_time = max(dwell_time, abs(step_size) / self.MAX_SPEED_UMPMS)

        fly_back_speed = min(fly_back_speed, self.MAX_SPEED_UMPMS)
        fly_back_speed = max(fly_back_speed, abs(step_size / dwell_time))

        # The number of pixels we wait at the beginning of each line to let shaking settle down
        LineWaitPixels = int(around(line_dwell / dwell_time))

        # The following ceil will be compensated ("automatically") by a reduced acceleration
        AccelPixels = int(
            ceil(abs(step_size) / (dwell_time * dwell_time * acceleration_speed))
        )
        PrescanPixels = LineWaitPixels + AccelPixels + drift_pixels

        FullTravel_um = step_size * (pixels + drift_pixels + AccelPixels)
        Flyback_umpPix = (-1) * sign(step_size) * fly_back_speed * dwell_time
        FlybackAccelPixels = ceil(
            abs(Flyback_umpPix) / (dwell_time * dwell_time * acceleration_speed)
        )

        if FlybackAccelPixels < abs(FullTravel_um / Flyback_umpPix):
            # The overshot from this ceil will be corrected for in the end
            FlybackPixels = ceil(
                abs(FullTravel_um / Flyback_umpPix) - FlybackAccelPixels
            )
            AdjustedFlybackAccelPixels = FlybackAccelPixels
        else:
            FlybackPixels = 0
            # go as close to real value as possible (-> RoundRealToNearestInteger() instead of ceil())
            AdjustedFlybackAccelPixels = around(
                sqrt(FlybackAccelPixels * abs(FullTravel_um / Flyback_umpPix))
            )

        PostscanPixels = int(
            AccelPixels + FlybackPixels + 2 * AdjustedFlybackAccelPixels
        )
        TotalPixels = int(PrescanPixels + pixels + PostscanPixels)

        Positions_um = [0] * TotalPixels
        fStart_um = center - step_size * (drift_pixels + (pixels + AccelPixels) / 2)

        PostscanPixels = int(
            AccelPixels + FlybackPixels + 2 * AdjustedFlybackAccelPixels
        )
        TotalPixels = int(PrescanPixels + pixels + PostscanPixels)

        Positions_um = [0] * TotalPixels
        fStart_um = center - step_size * (drift_pixels + (pixels + AccelPixels) / 2)

        k = 0
        j, k = forHelper(
            j, k, lambda j, k: j < LineWaitPixels, Positions_um, lambda j, k: 0
        )
        j, k = forHelper(
            j,
            k,
            lambda j, k: j < AccelPixels,
            Positions_um,
            lambda j, k: step_size * (j + 1) * (j + 1) / (2 * AccelPixels),
        )

        TempStart_um = step_size * j * j / (2 * AccelPixels) if AccelPixels != 0 else 0

        j, k = forHelper(
            j,
            k,
            lambda j, k: j < drift_pixels + pixels,
            Positions_um,
            lambda j, k: TempStart_um + step_size * (j + 1),
        )
        TempStart_um += step_size * j
        j, k = forHelper(
            j,
            k,
            lambda j, k: j < AccelPixels,
            Positions_um,
            lambda j, k: TempStart_um
            + step_size * ((j + 1) - (j + 1) * (j + 1) / (2 * AccelPixels)),
        )
        if AccelPixels != 0:
            TempStart_um += step_size * (j - j * j / (2.0 * AccelPixels))

        # now fly back
        j, k = forHelper(
            j,
            k,
            lambda j, k: j < AdjustedFlybackAccelPixels,
            Positions_um,
            lambda j, k: TempStart_um
            + Flyback_umpPix * (j + 1) * (j + 1) / (2 * FlybackAccelPixels),
        )

        if FlybackAccelPixels != 0:
            TempStart_um += Flyback_umpPix * j * j / (2 * FlybackAccelPixels)
        j, k = forHelper(
            j,
            k,
            lambda j, k: j < FlybackPixels,
            Positions_um,
            lambda j, k: TempStart_um + Flyback_umpPix * (j + 1),
        )
        TempStart_um += Flyback_umpPix * j
        j, k = forHelper(
            j,
            k,
            lambda j, k: j < AdjustedFlybackAccelPixels,
            Positions_um,
            lambda j, k: TempStart_um
            + Flyback_umpPix
            * ((j + 1) * 2 * AdjustedFlybackAccelPixels - (j + 1) * (j + 1))
            / (2 * FlybackAccelPixels),
        )

        # Now let's fix possible jumps at the end of unidirectional lines
        # We just find the difference between the start and the last pixel
        Difference = -Positions_um[TotalPixels - 1]
        # and add a fraction of it to all return pixels (cheating!)
        try:
            Difference /= FlybackPixels + 2 * AdjustedFlybackAccelPixels
        except DivisionByZero:
            Difference = 0

        k = PrescanPixels + AccelPixels + pixels
        j = 0
        while j < FlybackPixels + 2 * AdjustedFlybackAccelPixels:
            Positions_um[k + j] += Difference * (j + 1)
            j += 1

        return (
            dwell_time,
            fStart_um,
            Positions_um,
            PrescanPixels,
            PostscanPixels,
            TotalPixels,
            pixels,
        )


# abstract methods `collect_incoming_data` and `found_terminator` are defined in
# DeviceSocket (base class of DevicePi). Since multiple inheritance is used here
# we better disable the pylint warning.
# pylint: disable=abstract-method
# see https://github.com/python/mypy/issues/9319 for mypy error
class DevicePiPort(DevicePort, DevicePi):  # type: ignore
    response_timeout = DevicePi.response_timeout
    terminator = DevicePi.terminator
    push_commands_max = DevicePi.push_commands_max

    def __init__(
        self,
        port,
        baud_rate=115200,
        parity=serial.PARITY_NONE,
        stop_bits=serial.STOPBITS_ONE,
        byte_size=serial.EIGHTBITS,
        device_id=None,
        config=None,
    ):
        self.channel_mapping = bidict.MutableBidict()
        self.valid_commands = []
        super().__init__(
            port, baud_rate, parity, stop_bits, byte_size, device_id, config
        )

    def handshake(self):
        self.logger.info("Handshake initiated")
        self.push(b"ERR?\n")
        time.sleep(0.05)  # Give some time for devices to reply
        if self.serial_port.in_waiting != 0:
            output = self.read_all().strip()
            is_error_message = self.error_pattern.match(output)
            if is_error_message is not None:
                return True
        return False


class DevicePiChannel(DeviceChannel):
    def __init__(self, device, channel, device_id=None, config=None):
        self.channel_id = None
        super().__init__(device, channel, device_id, config)

    def _init_attributes(self):
        super()._init_attributes()
        self.create_attribute(ATTR_ENCODER_BASE_UNIT, readonly=True)
        self.create_attribute(
            ATTR_POSITION,
            default_type=np.float64,
            decimals=9,
            set_function=self._move_absolute,
            set_value_when_set_function=False,
        )
        self.create_attribute(
            ATTR_POSITION_UPPER_LIMIT,
            default_type=np.float64,
            decimals=9,
            set_function=self.set_position_upper_limit,
        )
        self.create_attribute(
            ATTR_POSITION_LOWER_LIMIT,
            default_type=np.float64,
            decimals=9,
            set_function=self.set_position_lower_limit,
        )
        self.create_attribute(
            ATTR_VELOCITY,
            default_type=np.float64,
            decimals=9,
            set_function=self.set_velocity,
        )
        self.create_attribute(
            ATTR_SERVO_STATE, default_type=bool, set_function=self.set_servo_state
        )
        self.create_attribute(ATTR_REFERENCED, readonly=True, default_type=bool)
        self.create_attribute(ATTR_MOVING, readonly=True, default_type=bool)
        self.create_attribute(ATTR_SCANNING, readonly=True, default_type=bool)
        self.create_attribute(
            ATTR_WAVE_GENERATOR, readonly=True, default_type=np.uint16
        )
        self.create_attribute(ATTR_RECORD_TABLE_DATA, default_value=[], readonly=True)
        self.create_attribute(ATTR_RECORDED_POSITIONS, default_value=[], readonly=True)

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
        self.channel_id = self.device.channel_mapping.inv.get(self.channel)
        self.command("PUN? {}\n".format(self.channel_id))
        if "FRF?" in self.device.valid_commands:
            self.command("FRF? {}\n".format(self.channel_id))
        else:
            self.set_value(ATTR_REFERENCED, True)
        self.command("SVO? {}\n".format(self.channel_id))
        self.get_position_lower_limit()
        self.get_position_upper_limit()
        self.get_velocity(callback=_finish_configuration)

    def subject_update(self, key, value, subject):
        super().subject_update(key, value, subject)

        if self.connected and isinstance(key, tuple) and key[0] == self.channel:
            attribute = key[1]

            if attribute == ATTR_ENCODER_BASE_UNIT:
                self.set_attribute((ATTR_POSITION, UNIT), value)
                self.set_attribute((ATTR_POSITION_UPPER_LIMIT, UNIT), value)
                self.set_attribute((ATTR_POSITION_LOWER_LIMIT, UNIT), value)
                self.set_attribute((ATTR_RECORD_TABLE_DATA, UNIT), value)
                self.set_attribute((ATTR_VELOCITY, UNIT), "{}/s".format(value))
            elif attribute == ATTR_POSITION_UPPER_LIMIT:
                self.set_attribute((ATTR_POSITION, MAX), value)
            elif attribute == ATTR_POSITION_LOWER_LIMIT:
                self.set_attribute((ATTR_POSITION, MIN), value)
            elif attribute == ATTR_MOVING:
                if self.get_value(ATTR_SCANNING) or value:
                    self.set_status(STATUS_BUSY)
                else:
                    self.set_status(STATUS_IDLE)
            elif attribute == ATTR_SCANNING:
                if self.get_value(ATTR_MOVING) or value:
                    self.set_status(STATUS_BUSY)
                else:
                    self.set_status(STATUS_IDLE)

            self.set_raw_value(ATTR_LATENCY, self.device.get_value(ATTR_LATENCY))
            self.set_raw_value(attribute, value)

    @expose_method(
        {
            "Field_size": ATTR_POSITION,
            "Steps": "Number of steps",
            "Dwell_time": "milliseconds",
            "Interpolating": "bool",
        }
    )
    def set_relative_fly_scan(self, Field_size, Steps, Dwell_time, Interpolating):
        filed_size = device_units(self, ATTR_POSITION, Field_size).m
        step_size = filed_size / int(Steps)
        actual_position = self.get_value(ATTR_POSITION)
        generator_id = self.device.set_fly_scan(
            self.channel,
            actual_position,
            step_size,
            int(Steps),
            float(Dwell_time),
            interpolating=int(Interpolating),
        )
        self.set_value(ATTR_WAVE_GENERATOR, generator_id)
        return generator_id

    @expose_method()
    def start_fly_scan(self):
        generator_id = self.get_value(ATTR_WAVE_GENERATOR)
        assert isinstance(generator_id, int)
        self.device.start_fly_scan(generator_id)

    def get_position_upper_limit(self, callback=None):
        return self.command(
            "TMN? {}\n".format(self.channel_id), callback=callback, with_token=True
        )

    def get_position_lower_limit(self, callback=None):
        return self.command(
            "TMX? {}\n".format(self.channel_id), callback=callback, with_token=True
        )

    def set_position_upper_limit(self, position, callback=None):
        self.logger.info("Set upper position limit to {}".format(position))
        return self.set_attribute((ATTR_POSITION, MAX), position, callback=callback)

    def set_position_lower_limit(self, position, callback=None):
        self.logger.info("Set lower position limit to {}".format(position))
        return self.set_attribute((ATTR_POSITION, MIN), position, callback=callback)

    def get_velocity(self, callback=None):
        return self.command(
            "VEL? {}\n".format(self.channel_id), callback=callback, with_token=True
        )

    def set_velocity(self, velocity, callback=None):
        self.logger.info("Set velocity to {}".format(velocity))
        return self.command(
            "VEL {} {}\n".format(self.channel_id, velocity),
            callback=callback,
            with_token=True,
            returning=False,
        )

    def _move_absolute(self, position, callback=None):
        self.logger.info("Move to absolute position {}".format(position))
        return self.command(
            "MOV {} {}\n".format(self.channel_id, position),
            callback,
            with_token=True,
            returning=False,
        )

    @expose_method()
    def stop(self, callback=None):
        self.logger.info("Stop movement")
        return self.command("STP\n", callback, with_token=True, returning=False)

    @expose_method()
    def find_reference(self, callback=None):
        self.logger.info("Reference")
        return self.command(
            "FRF{}\n".format(self.channel_id),
            callback,
            with_token=True,
            returning=False,
        )

    @expose_method({"position": ATTR_POSITION})
    def move_absolute(self, position):
        try:
            position = device_units(self, ATTR_POSITION, position)
            self.logger.info(
                "Move motor channel to absolute position {}".format(position)
            )
            return self.set_value(ATTR_POSITION, position.m)
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

    def set_servo_state(self, flag, callback=None):
        self.logger.info("Set servo state to {}".format(flag))
        return self.command(
            "SVO {} {}\n".format(self.channel_id, int(flag)),
            callback,
            with_token=True,
            returning=False,
        )
