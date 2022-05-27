import time
import numpy as np
import re

from kamzik3.snippets.snippetsDecorators import expose_method

from kamzik3.devices.deviceChannel import DeviceChannel
from serial import PARITY_NONE, STOPBITS_ONE, EIGHTBITS

import kamzik3
from kamzik3.constants import *
from kamzik3.devices.devicePort import DevicePort
from kamzik3.devices.deviceSocket import DeviceSocket


class DeviceMaxiGauge(DeviceSocket):
    terminator = b"\r\n"
    push_commands_max = 1
    measurement_statuses = {
        0: "Measurement data okay",
        1: "Underrange",
        2: "Overrange",
        3: "Sensor error",
        4: "Sensor off",
        5: "No sensor",
        6: "Identification error",
    }
    ch_status = re.compile("^PR[1-9].$")
    channel_names = None

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

        self.get_error_status()
        self.get_software_version()
        self.get_sensor_identification(callback=_finish_configuration)

    def _init_attributes(self):
        DeviceSocket._init_attributes(self)
        self.create_attribute(ATTR_MODEL, readonly=True)
        self.create_attribute(ATTR_CHANNELS, readonly=True)
        self.create_attribute(
            ATTR_CHANNELS_CONFIGURATION, readonly=True, default_type=TYPE_LIST
        )

    def handle_readout(self, readout_buffer):
        command, output, callback, token = DeviceSocket.handle_readout(
            self, readout_buffer
        )
        if output == "\x15":
            self.handle_command_error(command, readout_buffer)
        elif command == "PNR\r":
            self.set_value(ATTR_MODEL, output)
        elif command == "ERR\r" and output != "0,0":
            err1, err2 = output.split(",")
            self.handle_command_error(
                command, f"Error code 1: {err1}, Error code 2: {err2}"
            )
        elif command == "TID\r":
            channels = output.split(",")
            self.set_value(ATTR_CHANNELS, len(channels))
            self.set_value(ATTR_CHANNELS_CONFIGURATION, channels)
        elif command == "CID\r":
            self.channel_names = []
            for channel, name in enumerate(output.split(",")):
                self.notify((channel, ATTR_NAME), name)
                self.channel_names.append(name)
        elif self.ch_status.match(command):
            channel = int(command[2])
            status, pressure = output.split(",")
            self.notify((channel - 1, ATTR_PRESSURE), float(pressure))
            self.notify(
                (channel - 1, ATTR_MEASUREMENT_STATUS),
                self.measurement_statuses[int(status)],
            )

        if callback is not None:
            self.handle_readout_callback(callback, command, readout_buffer)
        if token:
            kamzik3.session.publisher.push_message(
                self.device_id, [command, readout_buffer], token
            )
            for observer in self._observers[:]:
                if isinstance(observer, DeviceMaxiGaugeChannel):
                    kamzik3.session.publisher.push_message(
                        observer.device_id, [command, readout_buffer], token
                    )

    def found_terminator(self):
        returning_flag = self.commands_buffer[0][0][3]
        if returning_flag and self.buffer[0] == "\x06":
            self.push(b"\x05\r")
            self.buffer = []
            return

        DeviceSocket.found_terminator(self)

    def get_software_version(self):
        self.command("PNR\r")

    def get_error_status(self):
        self.command("ERR\r")

    def get_sensor_identification(self, callback=None):
        self.command("TID\r", callback=callback)

    def start_polling(self):
        DeviceSocket.start_polling(self)
        self.poll_command("ERR\r", 1000)


# abstract methods `collect_incoming_data` and `found_terminator` are defined in
# DeviceSocket (base class of DeviceMaxiGauge). Since multiple inheritance is used here
# we better disable the pylint warning.
# pylint: disable=abstract-method
# see https://github.com/python/mypy/issues/9319 for mypy error
class DeviceMaxiGaugePort(DevicePort, DeviceMaxiGauge):  # type: ignore
    terminator = b"\r\n"

    # not sure why we don't call init for the other super class really
    # pylint: disable=super-init-not-called
    def __init__(
        self,
        port,
        baud_rate=19200,
        parity=PARITY_NONE,
        stop_bits=STOPBITS_ONE,
        byte_size=EIGHTBITS,
        device_id=None,
        config=None,
    ):
        DevicePort.__init__(
            self, port, baud_rate, parity, stop_bits, byte_size, device_id, config
        )

    def handshake(self):
        self.logger.info("Handshake initiated")
        # Ask for version
        self.push(b"PNR\r")
        # Give some time for devices to reply
        time.sleep(0.1)
        if self.serial_port.in_waiting != 0:
            if self.read_all().strip() == "\x06":
                # Request data
                self.push(b"\x05\r")
                # Give some time for devices to reply
                time.sleep(0.1)
                # Read reply
                self.read_all()
                return True
        return False


class DeviceMaxiGaugeChannel(DeviceChannel):
    def _init_attributes(self):
        DeviceChannel._init_attributes(self)
        self.create_attribute(ATTR_NAME, set_function=self.set_name)
        self.create_attribute(
            ATTR_PRESSURE, readonly=True, default_type=np.float, decimals=9, unit="mbar"
        )
        self.create_attribute(ATTR_MEASUREMENT_STATUS, readonly=True)

    def handle_configuration(self):
        if self.configured:
            return

        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()
            self.start_polling()
            self.configured = True
            self.set_status(STATUS_CONFIGURED)
            self.logger.info(
                "Device configuration took {} sec.".format(time.time() - start_at)
            )

        self.connected = True
        self.get_sensor_name()
        _finish_configuration()

    def subject_update(self, key, value, subject):
        DeviceChannel.subject_update(self, key, value, subject)
        if self.connected and isinstance(key, tuple) and key[0] == self.channel:
            attribute = key[1]
            if attribute == ATTR_MEASUREMENT_STATUS:
                if value != "Sensor off":
                    self.set_status(STATUS_BUSY)
                else:
                    self.set_status(STATUS_IDLE)
            self.set_value(ATTR_LATENCY, self.device.get_value(ATTR_LATENCY))
            self.set_raw_value(attribute, value)

    def get_sensor_name(self):
        self.command("CID\r")

    def start_polling(self):
        DeviceChannel.start_polling(self)
        self.poll_command(f"PR{self.channel+1}\r", 300)

    def set_name(self, value):
        self.device.channel_names[self.channel] = value
        channel_names = ",".join(self.device.channel_names)
        self.command(f"CID,{channel_names}\r")

    @expose_method()
    def sensor_on(self):
        channels_count = self.device.get_value(ATTR_CHANNELS)
        channels_setup = ["0"] * channels_count
        channels_setup[self.channel] = "2"
        channels_setup = ",".join(channels_setup)
        self.command(f"SEN,{channels_setup}\r")

    @expose_method()
    def sensor_off(self):
        channels_count = self.device.get_value(ATTR_CHANNELS)
        channels_setup = ["0"] * channels_count
        channels_setup[self.channel] = "1"
        channels_setup = ",".join(channels_setup)
        self.command(f"SEN,{channels_setup}\r")

    @expose_method()
    def stop(self):
        self.sensor_off()
