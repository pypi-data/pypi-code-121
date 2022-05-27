import time

import numpy as np
import serial
from pint import Quantity
from typing import Optional

import kamzik3
from kamzik3 import units, WriteException
from kamzik3.constants import *
from kamzik3.devices.devicePort import DevicePort
from kamzik3.devices.deviceSocket import DeviceSocket


class DeviceThermoCube(DeviceSocket):
    """
    Chiller device.
    Documentation is here: https://svnsrv.desy.de/desy/cfel-cxi/doc/manuals/thermo/ThermoCube.pdf
    The ThermoCube 200/300/400 can store 8 bytes of transmission and can only handle up to 3
    commands per second.
    """

    terminator: Optional[bytes] = b"\r\n"
    push_commands_max = 1

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

        # Check for error
        self.command(b"\xC8")
        # Get temperature readout
        self.command(b"\xC9")
        # Get temperature setpoint
        self.command(b"\xC1", callback=_finish_configuration)

    def _init_attributes(self):
        """
        Attributes;
            ATTR_FAULT_BYTE: True if ERROR occurred
            ATTR_TEMPERATURE: Temperature readout
            ATTR_SETPOINT: Temperature setpoint
        """
        DeviceSocket._init_attributes(self)
        self.create_attribute(
            ATTR_FAULT_BYTE,
            readonly=True,
            min_value=0,
            max_value=8,
            default_type=np.uint8,
        )
        self.create_attribute(
            ATTR_TEMPERATURE,
            readonly=True,
            min_value=-100,
            max_value=100,
            unit="degC",
            default_type=np.float,
            decimals=3,
        )
        self.create_attribute(
            ATTR_SETPOINT,
            min_value=-100,
            max_value=100,
            unit="degC",
            default_type=np.float,
            decimals=3,
            set_function=self.set_setpoint,
        )

    def handle_readout(self, readout_buffer):
        """
        Handle readout from Device.
        To get value from readout we have to convert HEX to DECIMAL.
        :param str readout_buffer: raw readout buffer from Device
        """
        command, output, callback, token = DeviceSocket.handle_readout(
            self, readout_buffer
        )
        if command == b"\xC9":
            temperature = self.hex_to_temperature(
                self.parse_temperature_readout(output)
            )
            self.set_raw_value(ATTR_TEMPERATURE, temperature.m)
        elif command == b"\xC1":
            setpoint = self.hex_to_temperature(self.parse_temperature_readout(output))
            self.set_raw_value(ATTR_SETPOINT, setpoint.m)
        elif command == b"\xC8":
            errorByte = int(output)
            self.set_raw_value(ATTR_FAULT_BYTE, errorByte)
            if errorByte == 0:
                self.set_status(STATUS_IDLE)
            else:
                self.set_status(STATUS_ERROR)

        if callback is not None:
            self.handle_readout_callback(callback, command, readout_buffer)
        if token:
            kamzik3.session.publisher.push_message(
                self.device_id, [command, readout_buffer], token
            )

    def start_polling(self):
        DeviceSocket.start_polling(self)
        # Poll current temperature
        self.poll_command(b"\xC9", 500)
        # Poll temperature setpoint
        self.poll_command(b"\xC1", 5000)
        # Poll for error
        self.poll_command(b"\xC8", 500)

    @staticmethod
    def parse_temperature_readout(readout) -> str:
        """
        Return HEX representation of temperature
        :param str readout: Raw Device readout
        :return hex: temperature readout in HEX
        """
        low_byte, high_byte = readout.split(",")
        return "0x%x%x" % (int(high_byte), int(low_byte))

    @staticmethod
    def temperature_to_hex(temperature) -> str:
        """
        Convert temperature to HEX
        :param float temperature: Temeprature setpoint
        :return str: Setpoint in HEX
        """
        temperature_in_kelvin = units.Quantity(temperature, "celsius").to("fahrenheit")
        return "{:04X}".format(int(temperature_in_kelvin.m * 10))

    @staticmethod
    def hex_to_temperature(hex_temperature) -> Quantity:
        """
        Convert temp from HEX to Pint units Quantity
        :param str hex_temperature: Temperature in HEX
        :return Quantity: Temperature in Pint units Quantity
        """
        temperature_in_fahrenheit = int(hex_temperature, 16) / 10
        return units.Quantity(temperature_in_fahrenheit, "fahrenheit").to("celsius")

    def get_temperature(self):
        """
        Get temperature readout.
        """
        self.command(b"\xC9")

    def get_setpoint(self):
        """
        Get temperature setpoint value.
        """
        self.command(b"\xC1")

    def get_error(self):
        """
        Get error flag
        """
        self.command(b"\xC8")

    # FIXME: Can't we just remove the argument here? Check back when we have a type for the argument to create_attribute
    def set_setpoint(self, temperature, callback=None):
        """
        Set temperature setpoint.
        We need to send three commands.
        E1, Low data byte, High data byte.
        :param float temperature: temperature setpoint
        :param callback: not used
        """
        temperature_in_hex = self.temperature_to_hex(temperature)
        self.command(b"\xE1", returning=False)
        self.command(bytes.fromhex(temperature_in_hex[2:]), returning=False)
        self.command(
            bytes.fromhex(temperature_in_hex[:2]), returning=False, with_token=True
        )

    def send_command(self, commands):
        """
        We need to modify a bit send_command routine.
        :param list commands: list of commands to be send
        :return list: list of NOT sent commands
        """
        try:
            if self.connected:
                command = commands.pop(0)
                if command[3]:  # If command is returning
                    self.commands_buffer.append((command, time.time()))
                else:  # Command is not returning, simulate immediate execution
                    self.response_timestamp = time.time()
                self.push(command[0])
            else:
                self.handle_response_error("Device is not connected")
        except IndexError:
            self.handle_connection_error(
                "Device {} buffer error".format(self.device_id)
            )
        except (WriteException, serial.SerialException):
            self.handle_response_error("Device {} writing error".format(self.device_id))
        finally:
            # FIXME: Is it an error if exceptions get swallowed?
            return commands


# abstract method `found_terminator` is defined in DeviceSocket (base class of
# DeviceThermoCube). Since multiple inheritance is used here we better disable the
# pylint warning.
# pylint: disable=abstract-method
# see https://github.com/python/mypy/issues/9319 for mypy error
class DeviceThermoCubePort(DevicePort, DeviceThermoCube):  # type: ignore
    """
    Extend ETH controller to enable RS232 connection.
    """

    terminator: Optional[bytes] = None
    push_commands_max = 1

    # pylint: disable=super-init-not-called
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
        DevicePort.__init__(
            self, port, baud_rate, parity, stop_bits, byte_size, device_id, config
        )

    def handshake(self) -> bool:
        """
        Confirm connection to Device via RS232.
        :return bool: True if handshake successful
        """
        self.logger.info("Handshake initiated")
        self.push(b"\xC8")
        time.sleep(0.3)  # Give some time for devices to reply
        if self.serial_port.in_waiting != 0:
            readout = ord(self.read_all())
            if readout >= 0:
                return True
        return False

    def collect_incoming_data(self, data: bytes) -> None:
        """
        Modify collect_incoming_data method to match Device's communication protocol specification.
        :param bytes data: Device response bytes
        """
        # Get all bytes as separate string
        for c in data:
            self.buffer.append(str(c))

        cmd_query = self.commands_buffer[0][0][0]
        # Commands that queries temperature consist of two bytes
        if cmd_query in (b"\xC9", b"\xC1") and len(self.buffer) != 2:
            return
        # Create final string by joining buffer content with comma
        self.buffer = [",".join(self.buffer)]
        # Invoke found_terminator even though there is now terminator
        # We just want to continue in normal controller workflow and process command
        self.found_terminator()
