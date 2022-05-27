import socket
import time
from _socket import timeout
from threading import Thread
import re
import numpy as np
import serial

import kamzik3
from kamzik3.constants import *
from kamzik3.devices.device import Device
from kamzik3.devices.devicePort import DevicePort
from kamzik3.devices.deviceSocket import DeviceSocket
from kamzik3.snippets.snippetsDecorators import expose_method


class DeviceGalil(DeviceSocket):
    terminator = b":"
    analog_input_readout_command = (
        "MG @AN[0],@AN[1],@AN[2],@AN[3],@AN[4],@AN[5],@AN[6],@AN[7];"
    )
    analog_output_readout_command = (
        "MG @AO[0],@AO[1],@AO[2],@AO[3],@AO[4],@AO[5],@AO[6],@AO[7];"
    )
    analog_output_limits_command = "MG _DQ0,_DQ1,_DQ2,_DQ3,_DQ4,_DQ5,_DQ6,_DQ7;"
    analog_input_limits_command = "MG _AQ0,_AQ1,_AQ2,_AQ3,_AQ4,_AQ5,_AQ6,_AQ7;"
    digital_lO_readout_command = "MG _TI0,_TI1,_OP0,_OP1;"
    push_commands_max = 1
    response_timeout = 1000
    digital_mask = (1, 2, 4, 8, 16, 24, 48)

    def __init__(
        self, host, port, udp_host=None, udp_port=None, device_id=None, config=None
    ):
        self.udp_host = udp_host
        self.udp_port = udp_port
        self.udp_socket = None
        self.DO_config = []
        self.DI_config = []
        self.AO_config = []
        self.AI_config = []
        self.analog_input_date_type = np.dtype(
            [
                ("AI0", np.ushort),
                ("AI1", np.ushort),
                ("AI2", np.ushort),
                ("AI3", np.ushort),
                ("AI4", np.ushort),
                ("AI5", np.ushort),
                ("AI6", np.ushort),
                ("AI7", np.ushort),
            ]
        )
        self.analog_output_date_type = np.dtype(
            [
                ("AO0", np.ushort),
                ("AO1", np.ushort),
                ("AO2", np.ushort),
                ("AO3", np.ushort),
                ("AO4", np.ushort),
                ("AO5", np.ushort),
                ("AO6", np.ushort),
                ("AO7", np.ushort),
            ]
        )
        self.preset_io_attributes()
        super().__init__(host, port, device_id, config)

    def _init_attributes(self):
        super()._init_attributes()

        self.create_attribute(ATTR_MODEL, default_value="", readonly=True)

        self[ATTR_ANALOG_INPUT] = {}
        self[ATTR_ANALOG_OUTPUT] = {}
        self[ATTR_DIGITAL_INPUT] = {}
        self[ATTR_DIGITAL_OUTPUT] = {}

        for i in range(8):
            self.create_attribute(
                self.AI_config[i],
                ATTR_ANALOG_INPUT,
                unit="V",
                default_type=np.float16,
                decimals=4,
                readonly=True,
            )
            self.create_attribute(
                self.AO_config[i],
                ATTR_ANALOG_OUTPUT,
                unit="V",
                set_function=lambda value, output=i: self.set_analog_output(
                    output, value
                ),
                default_type=np.float16,
                decimals=4,
            )
            self.create_attribute(
                self.DI_config[i], ATTR_DIGITAL_INPUT, default_type=bool, readonly=True
            )
            self.create_attribute(
                self.DI_config[8 + i],
                ATTR_DIGITAL_INPUT,
                default_type=bool,
                readonly=True,
            )
            self.create_attribute(
                self.DO_config[i],
                ATTR_DIGITAL_OUTPUT,
                default_type=bool,
                set_value_when_set_function=False,
                set_function=lambda value, output=i: self.set_digital_output(
                    output, value
                ),
            )
            self.create_attribute(
                self.DO_config[8 + i],
                ATTR_DIGITAL_OUTPUT,
                default_type=bool,
                set_value_when_set_function=False,
                set_function=lambda value, output=8 + i: self.set_digital_output(
                    output, value
                ),
            )

    def preset_io_attributes(self):
        self.DO_config = [
            "DO[0]",
            "DO[1]",
            "DO[2]",
            "DO[3]",
            "DO[4]",
            "DO[5]",
            "DO[6]",
            "DO[7]",
            "DO[8]",
            "DO[9]",
            "DO[10]",
            "DO[11]",
            "DO[12]",
            "DO[13]",
            "DO[14]",
            "DO[15]",
        ]
        self.DI_config = [
            "DI[0]",
            "DI[1]",
            "DI[2]",
            "DI[3]",
            "DI[4]",
            "DI[5]",
            "DI[6]",
            "DI[7]",
            "DI[8]",
            "DI[9]",
            "DI[10]",
            "DI[11]",
            "DI[12]",
            "DI[13]",
            "DI[14]",
            "DI[15]",
        ]
        self.AO_config = [
            "AO[0]",
            "AO[1]",
            "AO[2]",
            "AO[3]",
            "AO[4]",
            "AO[5]",
            "AO[6]",
            "AO[7]",
        ]
        self.AI_config = [
            "AI[0]",
            "AI[1]",
            "AI[2]",
            "AI[3]",
            "AI[4]",
            "AI[5]",
            "AI[6]",
            "AI[7]",
        ]

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

        self.command("EO 0;")

        if self.udp_port is not None:
            self.command(
                "IHC={} <{} >1;".format(self.udp_host.replace(".", ","), self.udp_port)
            )  # Set UDP connection to provided host and port
            self.command("CFC;")  # Set interface C as main output for any UDP packet
            self.command(
                "DR200,2;"
            )  # Start recording data at 200ms and send it to second interface (C)
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_socket.bind((self.udp_host, self.udp_port))
            self.udp_socket.settimeout(self.response_timeout * 1e-3)
            Thread(target=self._udp_readout).start()

        self.command("\x12\x16;")  # Get galil model and firmware version
        # self.command("TZ;") # Get all inputs and outputs
        # self.command(self.analog_output_limits_command)
        # self.command(self.analog_input_limits_command)
        self.command("ID;")  # Get input / output configuration
        self.command(self.analog_input_readout_command)
        self.command(self.analog_output_readout_command)
        self.command(self.digital_lO_readout_command, callback=_finish_configuration)

    def _udp_readout(self):
        self.request_timestamp = time.time()
        while self.connected:
            try:
                data, _ = self.udp_socket.recvfrom(1024)  # buffer size is 1024 bytes
                self._handle_udp_readout(data)
                self.response_timestamp = time.time()
            except timeout:
                self.request_timestamp = time.time()
                # DevicePoller.check_device_alive(self)
            except OSError:
                # Socket doesn't exist
                pass
        try:
            self.udp_socket.close()
            self.udp_socket = None
        except AttributeError:
            pass  # udp socket was already closed

    def _handle_udp_readout(self, data):
        try:
            model_name, _revision = self.get_value(ATTR_MODEL).split(" ", maxsplit=1)
            if model_name == "RIO47100":
                for index, ao in enumerate(
                    np.frombuffer(data[8:24], dtype=self.analog_output_date_type)[0]
                ):
                    ao_attribute = self[ATTR_ANALOG_OUTPUT][self.AO_config[index]]
                    ao_min, ao_max = ao_attribute.remove_offset_factor(
                        ao_attribute[MIN]
                    ), ao_attribute.remove_offset_factor(ao_attribute[MAX])
                    dt_info = np.iinfo(self.analog_output_date_type[index])
                    self.set_raw_value(
                        (ATTR_ANALOG_OUTPUT, self.AO_config[index]),
                        (
                            ((ao - dt_info.min) * (ao_max - ao_min))
                            / (dt_info.max - dt_info.min)
                        )
                        + ao_min,
                    )

                for index, ai in enumerate(
                    np.frombuffer(data[24:40], dtype=self.analog_input_date_type)[0]
                ):
                    ai_attribute = self[ATTR_ANALOG_INPUT][self.AI_config[index]]
                    ai_min, ai_max = ai_attribute.remove_offset_factor(
                        ai_attribute[MIN]
                    ), ai_attribute.remove_offset_factor(ai_attribute[MAX])
                    dt_info = np.iinfo(self.analog_input_date_type[index])
                    self.set_raw_value(
                        (ATTR_ANALOG_INPUT, self.AI_config[index]),
                        (
                            ((ai - dt_info.min) * (ai_max - ai_min))
                            / (dt_info.max - dt_info.min)
                        )
                        + ai_min,
                    )

                digital_output = format(
                    np.frombuffer(data[40:42], dtype=np.ushort)[0], "b"
                )
                digital_input = format(
                    np.frombuffer(data[42:44], dtype=np.ushort)[0], "b"
                )
                digital_output = [bool(int(x)) for x in reversed(digital_output)] + (
                    [False] * (16 - len(digital_output))
                )
                digital_input = [bool(int(x)) for x in reversed(digital_input)] + (
                    [False] * (16 - len(digital_input))
                )

                for i, do in enumerate(digital_output):
                    self.set_raw_value([ATTR_DIGITAL_OUTPUT, self.DO_config[i]], do)
                for i, di in enumerate(digital_input):
                    self.set_raw_value([ATTR_DIGITAL_INPUT, self.DI_config[i]], di)
        except ValueError:
            pass

    def start_polling(self):
        if self.udp_port is None:
            Device.start_polling(self)
            self.poll_command(self.analog_input_readout_command, 200)
            self.poll_command(self.analog_output_readout_command, 200)
            self.poll_command(self.digital_lO_readout_command, 200)

    def handle_readout(self, readout_buffer):
        command, output, callback, token = super().handle_readout(readout_buffer)
        # Strip white characters from output
        output = output.strip()
        if output and output[0] == "?":
            self.handle_command_error(command, output)
        elif command == "TC 1;":
            readout_buffer = output
            self.handle_command_error(command, output)
        elif command == self.analog_input_readout_command:
            analog_inputs = map(float, output.split())
            for i, value in enumerate(analog_inputs):
                self.set_raw_value((ATTR_ANALOG_INPUT, self.AI_config[i]), value)
        elif command == self.analog_output_readout_command:
            analog_outputs = map(float, output.split())
            for i, value in enumerate(analog_outputs):
                self.set_raw_value((ATTR_ANALOG_OUTPUT, self.AO_config[i]), value)
        elif command == self.digital_lO_readout_command:
            di0, di1, do0, do1 = map(lambda v: int(float(v)), output.split())
            for bit in range(8):
                self.set_raw_value(
                    (ATTR_DIGITAL_INPUT, self.DI_config[bit]), bool(di0 & (1 << bit))
                )
                self.set_raw_value(
                    (ATTR_DIGITAL_INPUT, self.DI_config[8 + bit]),
                    bool(di1 & (1 << bit)),
                )
                self.set_raw_value(
                    (ATTR_DIGITAL_OUTPUT, self.DO_config[bit]), bool(do0 & (1 << bit))
                )
                self.set_raw_value(
                    (ATTR_DIGITAL_OUTPUT, self.DO_config[8 + bit]),
                    bool(do1 & (1 << bit)),
                )
        elif command == "ID;":
            for line in output.split("\r\n"):
                if line.startswith("analog inputs"):
                    if "programmable range" in line:
                        self.command(self.analog_input_limits_command)
                    else:
                        values = re.search(
                            r"analog inputs ([0-9]+)-([0-9]+) = [0-9]+ bits range ([0-9]+) to ([0-9]+)",
                            line,
                        )
                        if values is not None:
                            first_input, last_input, min_value, max_value = (
                                values.group(1),
                                values.group(2),
                                values.group(3),
                                values.group(4),
                            )
                            for index in range(int(first_input), int(last_input) + 1):
                                if self.get_attribute(
                                    (ATTR_ANALOG_INPUT, self.AI_config[index], MIN)
                                ) in (None, np.inf, -np.inf):
                                    self.set_raw_value(
                                        (ATTR_ANALOG_INPUT, self.AI_config[index]),
                                        float(min_value),
                                        key=MIN,
                                    )
                                if self.get_attribute(
                                    (ATTR_ANALOG_INPUT, self.AI_config[index], MAX)
                                ) in (None, np.inf, -np.inf):
                                    self.set_raw_value(
                                        (ATTR_ANALOG_INPUT, self.AI_config[index]),
                                        float(max_value),
                                        key=MAX,
                                    )
                if line.startswith("analog outputs"):
                    if "programmable range" in line:
                        self.command(self.analog_output_limits_command)
                    else:
                        values = re.search(
                            r"analog outputs ([0-9]+)-([0-9]+) = [0-9]+ bits range ([0-9]+) to ([0-9]+)",
                            line,
                        )
                        if values is not None:
                            first_input, last_input, min_value, max_value = (
                                values.group(1),
                                values.group(2),
                                values.group(3),
                                values.group(4),
                            )
                            for index in range(int(first_input), int(last_input) + 1):
                                if self.get_attribute(
                                    (ATTR_ANALOG_OUTPUT, self.AO_config[index], MIN)
                                ) in (None, np.inf, -np.inf):
                                    self.set_raw_value(
                                        (ATTR_ANALOG_OUTPUT, self.AO_config[index]),
                                        float(min_value),
                                        key=MIN,
                                    )
                                if self.get_attribute(
                                    (ATTR_ANALOG_OUTPUT, self.AO_config[index], MAX)
                                ) in (None, np.inf, -np.inf):
                                    self.set_raw_value(
                                        (ATTR_ANALOG_OUTPUT, self.AO_config[index]),
                                        float(max_value),
                                        key=MAX,
                                    )
        elif command == "\x12\x16;":
            self.set_raw_value(ATTR_MODEL, output)
        elif command == self.analog_output_limits_command:
            analog_outputs_limits = output.strip().split()
            # This is analog output channels limits mapping from Galil doc
            analog_limit_ranges = [(-10, 10), (0, 5), (0, 10), (-5, 5), (-10, 10)]
            new_date_type = []
            for index, limit_range_option in enumerate(analog_outputs_limits):
                # Get lower and uper limit for each analog output channel
                lower_limit, upper_limit = analog_limit_ranges[
                    int(float(limit_range_option))
                ]
                # Figure out data type
                dt = np.ushort
                # Append tuple representing analog output data type
                new_date_type.append((self.AO_config[index], dt))
                # Set both limits for analog channel
                if self.get_attribute(
                    (ATTR_ANALOG_OUTPUT, self.AO_config[index], MIN)
                ) in (None, np.inf, -np.inf):
                    self.set_raw_value(
                        (ATTR_ANALOG_OUTPUT, self.AO_config[index]),
                        lower_limit,
                        key=MIN,
                    )
                if self.get_attribute(
                    (ATTR_ANALOG_OUTPUT, self.AO_config[index], MAX)
                ) in (None, np.inf, -np.inf):
                    self.set_raw_value(
                        (ATTR_ANALOG_OUTPUT, self.AO_config[index]),
                        upper_limit,
                        key=MAX,
                    )
            # Set numpy data type, which is used to parse binary UDP readout
            self.analog_output_date_type = np.dtype(new_date_type)
        elif command == self.analog_input_limits_command:
            analog_inputs_limits = output.strip().split()
            # This is analog input channels limits mapping from Galil doc
            analog_limit_ranges = [(-10, 10), (-5, 5), (-10, 10), (0, 5), (0, 10)]
            new_date_type = []
            for index, limit_range_option in enumerate(analog_inputs_limits):
                # Get lower and uper limit for each analog output channel
                lower_limit, upper_limit = analog_limit_ranges[
                    int(float(limit_range_option))
                ]
                # Figure out data type
                dt = np.short if lower_limit < 0 else np.ushort
                # Append tuple representing analog output data type
                new_date_type.append((self.AO_config[index], dt))
                # Set both limits for analog channel
                if self.get_attribute(
                    (ATTR_ANALOG_INPUT, self.AI_config[index], MIN)
                ) in (None, np.inf, -np.inf):
                    self.set_raw_value(
                        (ATTR_ANALOG_INPUT, self.AI_config[index]), lower_limit, key=MIN
                    )
                if self.get_attribute(
                    (ATTR_ANALOG_INPUT, self.AI_config[index], MAX)
                ) in (None, np.inf, -np.inf):
                    self.set_raw_value(
                        (ATTR_ANALOG_INPUT, self.AI_config[index]), upper_limit, key=MAX
                    )
            # Set numpy data type, which is used to parse binary UDP readout
            self.analog_input_date_type = np.dtype(new_date_type)

        if callback is not None:
            self.handle_readout_callback(callback, command, readout_buffer)
        if token:
            kamzik3.session.publisher.push_message(
                self.device_id, [command, readout_buffer], token
            )

        return command, output, callback, token

    def set_analog_output(self, output, value, callback=None):
        """
        Set analog output to value 0-10V.

        :param output: int
        :param value: float
        :param callback: callable
        """
        self.logger.debug("Set analogue AO{} to value {}".format(output, value))
        return self.command("AO{},{};".format(output, value), callback, with_token=True)

    def set_digital_output(self, output, value, callback=None):
        """
        Set digital output to value 0 or 1.

        :param output: int
        :param value: bool
        :param callback: callable
        """
        self.logger.debug("Set digital output to value {}".format(value))
        if value == 0:
            return self.command("CB{};".format(output), callback, with_token=True)
        else:
            return self.command("SB{};".format(output), callback, with_token=True)

    @expose_method({"bitmask": "0-65535"})
    def set_digital_output_mask(self, bitmask):
        self.logger.debug("Set digital output mask to value {}".format(bitmask))
        bitmask = int(bitmask)
        self.command("OP{};".format(bitmask))

    def set_command_echo(self, value, callback=None):
        r"""
        Set printing command for serial port together with command output.

        Example::

            EO 0: MG 1; => '1.0000\r\n:'

            EO 1: MG 1; => 'MG1; 1.0000\r\n:'

        :param value:
        :param callback: callable
        :return:
        """
        self.logger.debug("Set command echo to value {}".format(value))
        return self.command("EO {};".format(value), callback, with_token=True)

    def valid_command_format(self, command):
        return command is not None and command[-1] == ";"

    def collect_incoming_data(self, data: bytes) -> None:
        datastr = data.decode("utf-8")
        if datastr.find("?") != -1:
            (
                _attribute,
                token,
                callback,
                _returning,
            ), _command_init_timestamp = self.commands_buffer.popleft()
            self.command("TC 1;", with_token=token, callback=callback)
            datastr = datastr[datastr.find("?") + 2 :]

        self.buffer.append(datastr)

    def get_error_code(self, callback=None):
        self.command("TC 1;", callback=callback)

    def close_connection(self):
        super().close_connection()
        if self.udp_socket is not None:
            self.udp_socket.close()


# abstract methods `collect_incoming_data` and `found_terminator` are defined in
# DeviceSocket (base class of DeviceGalil). Since multiple inheritance is used here
# we better disable the pylint warning.
# pylint: disable=abstract-method
# see https://github.com/python/mypy/issues/9319 for mypy error
class DeviceGalilPort(DevicePort, DeviceGalil):  # type: ignore
    terminator = DeviceGalil.terminator

    # Not sure _why_ super init isn't called though.
    # pylint: disable=super-init-not-called
    def __init__(
        self,
        port,
        baud_rate=115200,
        parity=serial.PARITY_NONE,
        stop_bits=serial.STOPBITS_ONE,
        byte_size=serial.EIGHTBITS,
        device_id=None,
        udp_host=None,
        udp_port=None,
        config=None,
    ):
        self.udp_host = udp_host
        self.udp_port = udp_port
        self.udp_socket = None
        self.DO_config = []
        self.DI_config = []
        self.AO_config = []
        self.AI_config = []
        self.analog_input_date_type = np.dtype(
            [
                ("AI0", np.ushort),
                ("AI1", np.ushort),
                ("AI2", np.ushort),
                ("AI3", np.ushort),
                ("AI4", np.ushort),
                ("AI5", np.ushort),
                ("AI6", np.ushort),
                ("AI7", np.ushort),
            ]
        )
        self.analog_output_date_type = np.dtype(
            [
                ("AO0", np.ushort),
                ("AO1", np.ushort),
                ("AO2", np.ushort),
                ("AO3", np.ushort),
                ("AO4", np.ushort),
                ("AO5", np.ushort),
                ("AO6", np.ushort),
                ("AO7", np.ushort),
            ]
        )
        self.preset_io_attributes()
        DevicePort.__init__(
            self, port, baud_rate, parity, stop_bits, byte_size, device_id, config
        )

    def handshake(self):
        self.logger.info("Handshake initiated")
        self.push(b"MG 1;")
        time.sleep(0.02)  # Give some time for devices to reply
        if self.serial_port.in_waiting != 0:
            if self.read_all().strip() in ("1.0000\r\n:", "MG 1; 1.0000\r\n:"):
                return True
        return False
