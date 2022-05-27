import re
import time

import bidict
import numpy as np
from kamzik3.snippets.snippetsDecorators import expose_method

import kamzik3
from kamzik3.constants import *
from kamzik3.devices.deviceSocket import DeviceSocket

VAL_NEGATIVE = "Negative"
VAL_POSITIVE = "Positive"
VAL_POWER_HOLD = "Power hold"
VAL_POWER_RELEASED = "Power released"
VAL_OFF = "Off"
VAL_UP_AND_DOWN = "Up and down"
VAL_UP_ONLY = "Up only"
VAL_UP_ONLY_SPECIAL = "Up only - special"
VAL_UP_ONLY_SPECIAL_2 = "Up only - special 2"


class DeviceProbusV(DeviceSocket):
    terminator = b"\n"
    push_commands_max = 1
    polarity_modes = bidict.frozenbidict(
        {
            VAL_POSITIVE: 0,
            VAL_NEGATIVE: 1,
        }
    )
    ramping_modes = bidict.frozenbidict(
        {
            VAL_OFF: 0,
            VAL_UP_AND_DOWN: 1,
            VAL_UP_ONLY: 2,
            VAL_UP_ONLY_SPECIAL: 3,
            VAL_UP_ONLY_SPECIAL_2: 4,
        }
    )
    error_check_pattern = re.compile(r"E(\d+)")
    error_description = {
        "E0": "No Error",
        "E1": "No data available",
        "E2": "Unknown register type",
        "E4": "Invalid argument",
        "E5": "Argument out of range",
        "E6": "Register is read only",
        "E7": "Receive overflow",
        "E8": "EEPROM is write protected",
        "E9": "Address error",
        "E10": "Unknown SCPI command",
        "E11": "Not allowed Trigger-on-Talk",
        "E12": "Invalid argument in ~Tn command",
        "E13": "Invalid N-value",
        "E14": "Register is write only",
        "E15": "String too long",
        "E16": "Wrong checksum",
    }

    # pylint: disable=unused-argument
    def __init__(
        self, host, port=2101, udp_host=None, udp_port=None, device_id=None, config=None
    ):
        DeviceSocket.__init__(self, host, port, device_id, config)

    def _init_attributes(self):
        DeviceSocket._init_attributes(self)

        self.create_attribute(
            ATTR_VOLTAGE_SETPOINT,
            default_type=np.float16,
            min_value=0,
            max_value=2000,
            decimals=3,
            unit="V",
            set_function=self.set_voltage,
        )
        self.create_attribute(
            ATTR_CURRENT_SETPOINT,
            default_type=np.float16,
            min_value=0,
            max_value=1.5,
            decimals=3,
            unit="A",
            set_function=self.set_current,
        )
        self.create_attribute(
            ATTR_VOLTAGE_READOUT,
            readonly=True,
            default_type=np.float16,
            min_value=0,
            decimals=3,
            unit="V",
        )
        self.create_attribute(
            ATTR_CURRENT_READOUT,
            readonly=True,
            default_type=np.float16,
            min_value=0,
            decimals=6,
            unit="A",
        )
        self.create_attribute(
            ATTR_OUTPUT_RELEASED,
            default_value=None,
            default_type=bool,
            set_function=self.set_release_output,
        )
        self.create_attribute(
            ATTR_DIGITAL_PROGRAMMING_ACTIVE,
            readonly=True,
            default_value=None,
            default_type=bool,
        )
        self.create_attribute(
            ATTR_ANALOGUE_PROGRAMMING_ACTIVE,
            readonly=True,
            default_value=None,
            default_type=bool,
        )
        self.create_attribute(
            ATTR_CONTROL_VOLTAGE, readonly=True, default_value=None, default_type=bool
        )
        self.create_attribute(
            ATTR_CONTROL_CURRENT, readonly=True, default_value=None, default_type=bool
        )
        self.create_attribute(
            ATTR_CALIBRATION_MODE, readonly=True, default_value=None, default_type=bool
        )
        self.create_attribute(
            ATTR_POLARITY_REVERSAL, readonly=True, default_value=None, default_type=bool
        )
        self.create_attribute(
            ATTR_CURRENT_ON_TARGET, readonly=True, default_value=None, default_type=bool
        )
        self.create_attribute(
            ATTR_VOLTAGE_ON_TARGET, readonly=True, default_value=None, default_type=bool
        )
        self.create_attribute(
            ATTR_RAMP_VOLTAGE_MODE,
            default_value=None,
            default_type=self.ramping_modes.keys(),
            set_function=self.set_voltage_ramping_mode,
        )
        self.create_attribute(
            ATTR_RAMP_CURRENT_MODE,
            default_value=None,
            default_type=self.ramping_modes.keys(),
            set_function=self.set_current_ramping_mode,
        )
        self.create_attribute(
            ATTR_OUTPUT_POLARITY,
            default_value=None,
            default_type=self.polarity_modes.keys(),
            set_function=self.set_polarity,
        )
        self.create_attribute(
            ATTR_VOLTAGE_RAMPING_RATE,
            default_type=np.float16,
            min_value=0,
            max_value=10000,
            decimals=3,
            unit="V/s",
            set_function=self.set_voltage_ramping_rate,
        )
        self.create_attribute(
            ATTR_CURRENT_RAMPING_RATE,
            default_type=np.float16,
            min_value=0,
            max_value=10000,
            decimals=3,
            unit="A/s",
            set_function=self.set_current_ramping_rate,
        )

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

        self.get_digital_programming_output_bit()
        self.get_analog_programming_active_bit()
        self.get_release_output_bit()
        self.get_control_voltage_bit()
        self.get_control_current_bit()
        self.get_polarity_reversal_bit()
        self.get_output_polarity_bit()
        self.get_voltage_ramping_rate()
        self.get_current_ramping_rate()
        self.get_voltage_ramping_mode()
        self.get_current_ramping_mode()
        # Set output measurement for V and A to normal precision
        self.command(">S0H 0\r\n")
        self.command(">S1H 0\r\n", callback=_finish_configuration)

    def handle_readout(self, readout_buffer):
        command, output, callback, token = DeviceSocket.handle_readout(
            self, readout_buffer
        )
        # Strip white characters from output
        error_code = self.error_check_pattern.match(output)
        if error_code is not None:
            if (int(error_code.group(1))) != 0:
                # We have error code
                self.handle_command_error(
                    command, self.error_description.get(output, "Unknown error")
                )
                return None
        else:
            (_request, value) = output.split(":")
            if command == ">S0?\r\n":
                self.set_raw_value(ATTR_VOLTAGE_SETPOINT, float(value))
            elif command == ">S1?\r\n":
                self.set_raw_value(ATTR_CURRENT_SETPOINT, float(value) * 1000)
            elif command == ">BON?\r\n":
                self.set_raw_value(ATTR_OUTPUT_RELEASED, bool(int(value)))
            elif command == ">KS?\r\n":
                self.set_raw_value(ATTR_CONTROL_CURRENT, bool(int(value[0])))
                self.set_raw_value(ATTR_CONTROL_VOLTAGE, bool(int(value[1])))
                self.set_raw_value(ATTR_OUTPUT_RELEASED, bool(int(value[2])))
                self.set_raw_value(ATTR_CALIBRATION_MODE, bool(int(value[5])))
                self.set_status(STATUS_BUSY if bool(int(value[2])) else STATUS_IDLE)
            elif command == ">DSD?\r\n":
                self.set_raw_value(ATTR_DIGITAL_PROGRAMMING_ACTIVE, bool(int(value)))
            elif command == ">DSA?\r\n":
                self.set_raw_value(ATTR_ANALOGUE_PROGRAMMING_ACTIVE, bool(int(value)))
            elif command == ">DVR?\r\n":
                self.set_raw_value(ATTR_CONTROL_VOLTAGE, bool(int(value)))
            elif command == ">DIR?\r\n":
                self.set_raw_value(ATTR_CONTROL_CURRENT, bool(int(value)))
            elif command == ">DCAL?\r\n":
                self.set_raw_value(ATTR_CALIBRATION_MODE, bool(int(value)))
            elif command == ">BX?\r\n":
                self.set_raw_value(ATTR_POLARITY_REVERSAL, bool(int(value)))
            elif command == ">DX?\r\n":
                self.set_raw_value(
                    ATTR_OUTPUT_POLARITY, self.polarity_modes.inv.get(int(value))
                )
            elif command == ">S0R?\r\n":
                self.set_raw_value(ATTR_VOLTAGE_RAMPING_RATE, float(value))
            elif command == ">S1R?\r\n":
                self.set_raw_value(ATTR_CURRENT_RAMPING_RATE, float(value))
            elif command == ">M0?\r\n":
                value = float(value)
                if self.get_value(ATTR_POLARITY_REVERSAL):
                    value *= -1
                self.set_raw_value(ATTR_VOLTAGE_READOUT, value)
            elif command == ">M1?\r\n":
                self.set_raw_value(ATTR_CURRENT_READOUT, float(value) * 1000)
            elif command == ">S0S?\r\n":
                self.set_raw_value(ATTR_VOLTAGE_ON_TARGET, bool(int(value)))
            elif command == ">S1S?\r\n":
                self.set_raw_value(ATTR_CURRENT_ON_TARGET, bool(int(value)))
            elif command == ">S0?\r\n":
                self.set_raw_value(ATTR_VOLTAGE_SETPOINT, float(value))
            elif command == ">S0B?\r\n":
                self.set_raw_value(
                    ATTR_RAMP_VOLTAGE_MODE, self.ramping_modes.inv.get(int(value))
                )
            elif command == ">S1B?\r\n":
                self.set_raw_value(
                    ATTR_RAMP_CURRENT_MODE, self.ramping_modes.inv.get(int(value))
                )
        if callback is not None:
            self.handle_readout_callback(callback, command, readout_buffer)
        if token:
            kamzik3.session.publisher.push_message(
                self.device_id, [command, readout_buffer], token
            )

        return command, output, callback, token

    def start_polling(self):
        DeviceSocket.start_polling(self)
        self.poll_command(">S0?\r\n", 1000)
        self.poll_command(">S1?\r\n", 1000)
        self.poll_command(">M0?\r\n", 500)
        self.poll_command(">M1?\r\n", 500)
        self.poll_command(">KS?\r\n", 300)
        self.poll_command(">S0S?\r\n", 1000)
        self.poll_command(">S1S?\r\n", 1000)

    def get_voltage_ramping_mode(self):
        self.command(">S0B?\r\n")

    def get_current_ramping_mode(self):
        self.command(">S1B?\r\n")

    def get_voltage(self):
        self.command(">S0?\r\n")

    def get_current(self):
        self.command(">S1?\r\n")

    def get_release_output_bit(self):
        self.command(">BON?\r\n")

    def get_polarity_reversal_bit(self):
        self.command(">BX?\r\n")

    def get_control_voltage_bit(self):
        self.command(">DVR?\r\n")

    def get_control_current_bit(self):
        self.command(">DIR?\r\n")

    def get_output_polarity_bit(self):
        self.command(">DX?\r\n")

    def get_digital_programming_output_bit(self):
        self.command(">DSD?\r\n")

    def get_analog_programming_active_bit(self):
        self.command(">DSA?\r\n")

    def get_voltage_readout(self):
        self.command(">M0?\r\n")

    def get_current_readout(self):
        self.command(">M1?\r\n")

    def get_offset(self):
        self.command(">CM0O?\r\n")
        self.command(">CM1O?\r\n")

    def get_gain(self):
        self.command(">CM0GP?\r\n")
        self.command(">CM0GN?\r\n")

    def get_voltage_ramping_rate(self):
        self.command(">S0R?\r\n")

    def get_current_ramping_rate(self):
        self.command(">S1R?\r\n")

    def get_state(self):
        self.command(">KS?\r\n")

    def set_voltage(self, value):
        self.command(f">S0 {value}\r\n")

    def set_current(self, value):
        value = float(value) * 1e-3
        self.command(f">S1 {value:.5e}\r\n")

    def set_release_output(self, value):
        self.command(f">BON {int(value)}\r\n")

    def set_polarity(self, value):
        self.command(f">BX {self.polarity_modes.get(value)}\r\n")

    def set_voltage_ramping_rate(self, value):
        self.command(f">S0R {value}\r\n")

    def set_current_ramping_rate(self, value):
        self.command(f">S1R {value}\r\n")

    def set_voltage_ramping_mode(self, value):
        self.command(f">S0B {self.ramping_modes.get(value)}\r\n")

    def set_current_ramping_mode(self, value):
        self.command(f">S1B {self.ramping_modes.get(value)}\r\n")

    @expose_method()
    def release_output(self):
        self.set_release_output(True)

    @expose_method()
    def stop(self):
        self.set_release_output(False)
