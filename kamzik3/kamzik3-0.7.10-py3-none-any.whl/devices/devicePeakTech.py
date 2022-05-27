import time

import numpy as np
import serial

import kamzik3
from kamzik3.constants import *
from kamzik3.devices.devicePort import DevicePort
from kamzik3.devices.deviceSocket import DeviceSocket


class DevicePeakTech(DeviceSocket):
    terminator = b"OK\r"
    push_commands_max = 1

    def _init_attributes(self):
        super()._init_attributes()
        self.create_attribute(ATTR_CONSTANT_CURRENT, readonly=True, default_type=bool)
        self.create_attribute(ATTR_CONSTANT_VOLTAGE, readonly=True, default_type=bool)
        self.create_attribute(
            ATTR_VOLTAGE,
            default_type=np.float16,
            min_value=0,
            decimals=3,
            unit="V",
            set_function=self.set_voltage_output,
        )
        self.create_attribute(
            ATTR_MAX_VOLTAGE,
            default_type=np.float16,
            min_value=0,
            decimals=1,
            unit="V",
            max_value=99.9,
            set_function=self.set_max_voltage_output,
            set_value_when_set_function=False,
        )
        self.create_attribute(
            ATTR_CURRENT,
            default_type=np.float16,
            min_value=0,
            decimals=3,
            unit="A",
            set_function=self.set_current_output,
        )
        self.create_attribute(
            ATTR_MAX_CURRENT,
            default_type=np.float16,
            min_value=0,
            max_value=99.9,
            decimals=1,
            unit="A",
            set_function=self.set_max_current_output,
            set_value_when_set_function=False,
        )
        self.create_attribute(
            ATTR_OUTPUT_SWITCH,
            default_type=bool,
            set_function=self.switch_output,
            set_value_when_set_function=False,
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

        self.command("GOVP\r")
        self.command("GOCP\r", callback=_finish_configuration)

    def handle_readout(self, readout_buffer):
        """
        Input command: GETD [CR]
        Meaning: The PS Display value is 15V and 16A. It is in CC mode.
        Return value: 150016001[CR] OK[CR]

        Input command: GOVP [CR]
        Meaning: The preset upper limit of output Voltage is 11.1V
        Return value: 111[CR] OK[CR]

        Input command: GOCP [CR]
        Meaning: The preset upper limit of output Current is 11.1A
        Return value: 111[CR] OK[CR]
        """
        command, output, callback, token = super().handle_readout(readout_buffer)

        if command == "GETD\r":
            voltage, current, cv_cc_flag = (
                int(output[:4]) / 100.0,
                int(output[4:8]) / 100,
                int(output[8:]),
            )
            self.set_offsetted_value(ATTR_CONSTANT_VOLTAGE, cv_cc_flag == 0)
            self.set_offsetted_value(ATTR_CONSTANT_CURRENT, cv_cc_flag == 1)
            self.set_offsetted_value(ATTR_VOLTAGE, voltage)
            self.set_offsetted_value(ATTR_CURRENT, current)
            if voltage < 0.75:
                self.set_offsetted_value(ATTR_OUTPUT_SWITCH, False)
            else:
                self.set_offsetted_value(ATTR_OUTPUT_SWITCH, True)
        elif command == "GOVP\r":
            max_voltage = int(output[:3]) / 10
            self.set_attribute((ATTR_VOLTAGE, MAX), max_voltage)
            self.set_offsetted_value(ATTR_MAX_VOLTAGE, max_voltage)
        elif command == "GOCP\r":
            max_current = int(output[:3]) / 10
            self.set_attribute((ATTR_CURRENT, MAX), max_current)
            self.set_offsetted_value(ATTR_MAX_CURRENT, max_current)

        if callback is not None:
            self.handle_readout_callback(callback, command, readout_buffer)
        if token:
            kamzik3.session.publisher.push_message(
                self.device_id, [command, readout_buffer], token
            )

    def start_polling(self):
        super().start_polling()
        self.poll_command("GETD\r", 200)

    def set_max_voltage_output(self, value, callback=None):
        """
        Preset the upper limit of output Voltage.

        <voltage>=000<???<Max Volt where Max Volt value refer to product specification.

        Input command: SOVP 151[CR]
        Meaning: Preset upper limit of output Voltage as 15.1V
        Return value: OK[CR]
        """
        self.logger.info("Set max voltage output to {} V".format(value))
        self.command(
            "SOVP{0:03d}\r".format(int(float(value) * 10.0)), callback, with_token=True
        )
        return self.command("GOVP\r")

    def set_max_current_output(self, value, callback=None):
        """
        Preset the upper limit of output Current.

        <current>=000<???<Max Curr where Max Curr value refer to product specification.

        Input command: SOCP 151[CR]
        Meaning: Preset upper limit of output Current as 15.1A
        Return value: OK[CR]
        """
        self.logger.info("Set max current output to {} A".format(value))
        self.command(
            "SOCP{0:03d}\r".format(int(float(value) * 10.0)), callback, with_token=True
        )
        return self.command("GOCP\r")

    def set_voltage_output(self, value, callback=None):
        """
        Preset Voltage value.

        <voltage>=000<???<Max Volt where Max Volt value refer to product specification.
        Input command: VOLT 127[CR]
        Meaning: Set Voltage value as 12.7V
        Return value: OK[CR]
        """
        self.logger.info("Set voltage output to {} V".format(value))
        return self.command(
            "VOLT{0:03d}\r".format(int(float(value) * 10.0)), callback, with_token=True
        )

    def set_current_output(self, value, callback=None):
        """
        Preset Current value.

        <current>=000<???<Max Curr where Max Curr value refer to product specification.

        Input command: CURR 120[CR]
        Meaning: Set Current value as 12.0A
        Return value: OK[CR]
        """
        self.logger.info("Set current output to {} A".format(value))
        return self.command(
            "CURR{0:03d}\r".format(int(float(value) * 10.0)), callback, with_token=True
        )

    def switch_output(self, value, callback=None):
        """
        Switch on/off the output of PS.

        <status>=0/1 (0=ON, 1=OFF)

        Input command: SOUT0 [CR]
        Meaning: Switch on the output of PS
        Return value: OK[CR]
        """
        self.logger.info("Switch output to {}".format(value))
        return self.command(
            "SOUT{}\r".format(int(not value)), callback, with_token=True
        )

    def stop(self):
        self.set_voltage_output(0)
        self.set_current_output(0)


# abstract methods `collect_incoming_data` and `found_terminator` are defined in
# DeviceSocket (base class of DevicePeakTech). Since multiple inheritance is used here
# we better disable the pylint warning.
# pylint: disable=abstract-method
# see https://github.com/python/mypy/issues/9319 for mypy error
class DevicePeakTechPort(DevicePort, DevicePeakTech):  # type: ignore
    terminator = DevicePeakTech.terminator
    push_commands_max = DevicePeakTech.push_commands_max

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

    def handshake(self):
        self.logger.info("Handshake initiated")
        self.push(b"GETD\r")
        time.sleep(0.1)  # Give some time for devices to reply
        if self.serial_port.in_waiting != 0:
            readout = self.read_all().split("\r")
            if readout[1] == "OK":
                return True
        return False
