import struct
import time

import numpy
import pandas

import kamzik3
from kamzik3 import DeviceError
from kamzik3.constants import *
from kamzik3.devices.deviceChannel import DeviceChannel
from kamzik3.devices.deviceSocket import DeviceSocket
from kamzik3.snippets.snippetsDecorators import expose_method


class DeviceInficonQcm(DeviceSocket):
    terminator = None
    push_commands_max = 1
    command_encoding = None
    device_packet_error = {
        "C": "invalid checksum",
        "F": "illegal format",
        "I": "invalid message",
        "M": "too many commands",
        "O": "response length is larger than",
    }
    device_response_error = {
        "A": "illegal command",
        "B": "illegal parameter value",
        "D": "illegal ID",
        "E": "data not available",
        "F": "cannot do now",
        "L": "length error",
        "P": "prior command failed",
    }

    def __init__(self, host, port=2101, device_id=None, config=None):
        self._materials = pandas.read_csv(
            "./resources/inficon_qcm_materials.txt", sep="\t", names=["Formula", "Name"]
        )
        self.materials = (
            self._materials["Formula"] + " - " + self._materials["Name"]
        ).to_list()
        DeviceSocket.__init__(self, host, port, device_id, config)

    def _init_attributes(self):
        DeviceSocket._init_attributes(self)
        self.create_attribute(ATTR_PRODUCT_TYPE, readonly=True)
        self.create_attribute(ATTR_SOFTWARE_VERSION, readonly=True)
        self.create_attribute(ATTR_FIRMWARE, readonly=True)
        self.create_attribute(ATTR_SENSORS_COUNT, default_value=8, readonly=True)
        self.create_attribute(
            ATTR_ACTIVE_PROCESS, default_value=1, default_type=int, readonly=True
        )

        for i in range(1, self.get_value(ATTR_SENSORS_COUNT) + 1):
            self.create_attribute(
                f"{ATTR_MATERIAL}_{i}",
                default_value=None,
                default_type=self.materials,
                set_function=lambda v, i=i: self.set_material(i, v),
                group=GROUP_MATERIALS,
            )
            self.create_attribute(
                f"{ATTR_OUTPUT}_{i}",
                default_value=None,
                set_function=lambda v, i=i: self.set_output_name(i, v),
                group=GROUP_OUTPUTS,
            )
            self.create_attribute(
                f"{ATTR_PROCESS}_{i}",
                default_value=None,
                set_function=lambda v, i=i: self.set_process_name(i, v),
                group=GROUP_PROCESSES,
            )
            self.create_attribute(
                f"{ATTR_USER_MESSAGE}_{i}",
                default_value=None,
                set_function=lambda v, i=i: self.set_user_message(i, v),
                group=GROUP_USER_MESSAGES,
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

        self.get_revision()
        self.get_version()
        for i in range(1, self.get_value(ATTR_SENSORS_COUNT) + 1):
            self.send_command_data("QN", self.t_byte(i))
            # Disable multipoint for each sensor
            self.send_command_data(
                "UM", self.t_byte(48) + self.t_byte(i) + self.t_int(0)
            )
            self.send_command_data("QO", self.t_byte(i))
            self.send_command_data("QK", self.t_byte(i))
            self.send_command_data("QV", self.t_byte(i))
            # Set failure action to STOP = 2
            self.send_command_data(
                "UM", self.t_byte(115) + self.t_byte(i) + self.t_int(2)
            )
            # Disable backup sensor
            self.send_command_data(
                "UM", self.t_byte(119) + self.t_byte(i) + self.t_int(0)
            )
            # Set tooling to 100%
            self.send_command_data(
                "UM", self.t_byte(120) + self.t_byte(i) + self.t_float(100)
            )
            # Set quality control to 0
            self.send_command_data(
                "UM", self.t_byte(121) + self.t_byte(i) + self.t_int(0)
            )
            # Set quality counts to 0
            self.send_command_data(
                "UM", self.t_byte(122) + self.t_byte(i) + self.t_int(0)
            )
            # Set stability single to 0
            self.send_command_data(
                "UM", self.t_byte(123) + self.t_byte(i) + self.t_int(0)
            )
            # Set stability total to 0
            self.send_command_data(
                "UM", self.t_byte(124) + self.t_byte(i) + self.t_int(0)
            )
            # Set output type to NO
            self.send_command_data("UT", self.t_byte(i) + self.t_byte(0))
            # Set calibration to uncalibrated = 999.9
            for j in range(90, 97, 1):
                self.send_command_data(
                    "UM", self.t_byte(j) + self.t_byte(i) + self.t_float(999.9)
                )

        self.get_firmware(callback=_finish_configuration)

    def handle_readout(self, readout_buffer):
        command, output, callback, token = DeviceSocket.handle_readout(
            self, readout_buffer
        )
        error_flag = bool(output[0])
        _timer_tick = output[1]
        ack = output[2]
        if error_flag:
            raise DeviceError(self.device_packet_error.get(chr(ack)))
        if ack != 6:
            print(command)
            raise DeviceError(self.device_response_error.get(chr(ack)))

        first_ch = chr(command[2])
        if first_ch == "H":
            command_group, command_id = first_ch, command[3]
            command_data = output[3:]
        elif first_ch in ("Q", "R", "U", "S"):
            command_group, command_id = chr(command[2]) + chr(command[3]), command[4]
            command_data = output[3:]

        if command_group == "H":
            if command_id == 1:
                self.set_value(ATTR_PRODUCT_TYPE, self.f_string(command_data))
            elif command_id == 2:
                version_number = self.f_int(command_data[:4])
                compatibility_version = self.f_int(command_data[4:8])
                range_version = self.f_int(command_data[8:])
                self.set_value(
                    ATTR_SOFTWARE_VERSION,
                    f"VN:{version_number}, CV:{compatibility_version}, RV:{range_version}",
                )
            elif command_id == 3:
                firmware_version = self.f_float(command_data)
                self.set_value(ATTR_FIRMWARE, f"{firmware_version:.3f}")
        elif command_group == "QN":
            material_index = command[4]
            formula = self.f_string(command_data)
            if formula != "" and " - " in formula:
                formula, library_index = formula.split(" - ")
                material = self.materials[int(library_index)]
                self.set_raw_value(
                    [GROUP_MATERIALS, f"{ATTR_MATERIAL}_{material_index}"], material
                )
        elif command_group == "SG":
            for channel in range(self.get_value(ATTR_SENSORS_COUNT)):
                self.notify((channel, ATTR_STATE), int(command_data[channel]))
        elif command_group == "QO":
            output_index = command[4]
            name = self.f_string(command_data)
            self.set_raw_value([GROUP_OUTPUTS, f"{ATTR_OUTPUT}_{output_index}"], name)
        elif command_group == "QK":
            output_index = command[4]
            name = self.f_string(command_data)
            self.set_raw_value(
                [GROUP_PROCESSES, f"{ATTR_PROCESS}_{output_index}"], name
            )
        elif command_group == "QS" and int(command[4]) == 2:
            channel = int(command[5]) - 1
            self.notify((channel, ATTR_SENSOR_TYPE), self.f_int(command_data))
        elif command_group == "QS" and int(command[4]) == 4:
            channel = int(command[5]) - 1
            self.notify((channel, ATTR_AUTO_Z), bool(self.f_int(command_data)))
        elif command_group == "QV":
            output_index = command[4]
            value = self.f_string(command_data)
            self.set_raw_value(
                [GROUP_USER_MESSAGES, f"{ATTR_USER_MESSAGE}_{output_index}"], value
            )
        elif command_group == "SS":
            channel = int(command[5]) - 1
            if channel == -1:
                if command_id == 6:
                    for channel, bit_index in enumerate(range(0, len(command_data), 4)):
                        self.notify(
                            (channel, ATTR_Z_RATIO),
                            self.f_float(command_data[bit_index : bit_index + 4]),
                        )
                elif command_id == 4:
                    for channel, bit_index in enumerate(range(0, len(command_data), 8)):
                        self.notify(
                            (channel, ATTR_FUNDAMENTAL_FREQUENCY),
                            self.f_double_int(command_data[bit_index : bit_index + 8]),
                        )
                elif command_id == 7:
                    for channel, bit_index in enumerate(range(0, len(command_data), 8)):
                        self.notify(
                            (channel, ATTR_AHARMONIC_FREQUENCY),
                            self.f_double_int(command_data[bit_index : bit_index + 8]),
                        )
                elif command_id == 12:
                    for channel, bit_index in enumerate(range(0, len(command_data), 4)):
                        self.notify(
                            (channel, ATTR_SENSOR_THICKNESS),
                            self.f_float(command_data[bit_index : bit_index + 4]),
                        )
                elif command_id == 0:
                    for channel, bit_index in enumerate(range(0, len(command_data), 1)):
                        self.notify(
                            (channel, ATTR_CRYSTAL_LIFE),
                            int.from_bytes(
                                command_data[bit_index : bit_index + 1], "little"
                            ),
                        )
                elif command_id == 13:
                    for channel, bit_index in enumerate(range(0, len(command_data), 4)):
                        self.notify(
                            (channel, ATTR_RAW_RATE),
                            self.f_float(command_data[bit_index : bit_index + 4]),
                        )
            else:
                if command_id == 6:
                    self.notify((channel, ATTR_Z_RATIO), self.f_float(command_data))
                elif command_id == 4:
                    self.notify(
                        (channel, ATTR_FUNDAMENTAL_FREQUENCY),
                        self.f_double_int(command_data),
                    )
                elif command_id == 7:
                    self.notify(
                        (channel, ATTR_AHARMONIC_FREQUENCY),
                        self.f_double_int(command_data),
                    )
                elif command_id == 12:
                    self.notify(
                        (channel, ATTR_SENSOR_THICKNESS), self.f_float(command_data)
                    )
                elif command_id == 0:
                    self.notify(
                        (channel, ATTR_CRYSTAL_LIFE),
                        int.from_bytes(command_data, "little"),
                    )
                elif command_id == 14:
                    self.notify((channel, ATTR_RAW_RATE), self.f_float(command_data))
        elif command_group == "SL":
            self.notify(
                (self.get_value(ATTR_ACTIVE_PROCESS) - 1, ATTR_LAYER_THICKNESS),
                self.f_float(command_data),
            )

        if callback is not None:
            self.handle_readout_callback(callback, command, readout_buffer)
        if token:
            kamzik3.session.publisher.push_message(
                self.device_id, [command, readout_buffer], token
            )
            for observer in self._observers[:]:
                if isinstance(observer, InficonQcmSensorChannel):
                    kamzik3.session.publisher.push_message(
                        observer.device_id, [command, readout_buffer], token
                    )

    def notify_channels(self, attribute, value):
        for channel in range(self.get_value(ATTR_SENSORS_COUNT)):
            self.notify((channel, attribute), value)

    def set_material(self, material_index, material):
        library_index = self.materials.index(material)
        # Set material from library into controller material index 1-32
        command_data = (
            self.t_byte(38) + self.t_byte(material_index) + self.t_byte(library_index)
        )
        self.send_command_data("RG", command_data)
        # Rename material, add library index
        formula, _full_name = material.split(" - ")
        controller_name = f"{formula} - {library_index}"
        command_data = self.t_byte(material_index) + self.t_str(controller_name)
        self.send_command_data("UN", command_data)

    @staticmethod
    def f_string(readout):
        return readout[:-1].decode()

    @staticmethod
    def f_int(readout):
        return int.from_bytes(readout, "little")

    @staticmethod
    def f_float(readout):
        return struct.unpack("f", readout)[0]

    @staticmethod
    def f_double_int(readout):
        return struct.unpack("q", readout)[0]

    @staticmethod
    def t_int(int_value):
        return int(int_value).to_bytes(4, "little")

    @staticmethod
    def t_float(float_value):
        return bytearray(struct.pack("f", float_value))

    @staticmethod
    def t_byte(int_value):
        return int(int_value).to_bytes(1, "little")

    @staticmethod
    def t_str(str_value):
        return str_value.encode() + b"\0"

    def start_polling(self):
        DeviceSocket.start_polling(self)
        self.poll_command(
            self.send_command_data("SG", self.t_byte(10), execute=False), 1000
        )
        self.poll_command(
            self.send_command_data(
                "SS", self.t_byte(4) + self.t_byte(0), execute=False
            ),
            1000,
        )
        self.poll_command(
            self.send_command_data(
                "SS", self.t_byte(6) + self.t_byte(0), execute=False
            ),
            1000,
        )
        self.poll_command(
            self.send_command_data(
                "SS", self.t_byte(7) + self.t_byte(0), execute=False
            ),
            1000,
        )
        self.poll_command(
            self.send_command_data(
                "SS", self.t_byte(12) + self.t_byte(0), execute=False
            ),
            1000,
        )
        self.poll_command(
            self.send_command_data(
                "SS", self.t_byte(0) + self.t_byte(0), execute=False
            ),
            1000,
        )
        self.poll_command(
            self.send_command_data(
                "SS", self.t_byte(13) + self.t_byte(0), execute=False
            ),
            1000,
        )
        self.poll_command(
            self.send_command_data(
                "SL", self.t_byte(4) + self.t_byte(1), execute=False
            ),
            1000,
        )

    def get_available_materials(self):
        materials_list = []
        for i in range(1, 33):
            materials_list.append(
                self.get_value([GROUP_MATERIALS, f"{ATTR_MATERIAL}_{i}"])
            )
        return materials_list

    def send_command_data(
        self,
        command_group,
        command_data=b"",
        callback=None,
        with_token=False,
        returning=True,
        execute=True,
    ):
        message = command_group.encode() + command_data
        message_length = len(message).to_bytes(2, "little")

        # In order to have final command, checksum needs to be calculated
        checksum = sum(message) % 256
        packet = message_length + message + checksum.to_bytes(1, "little")
        if execute:
            self.command(packet, callback, with_token, returning)
            return None
        else:
            return packet

    def collect_incoming_data(self, data: bytes) -> None:
        """
        This method serves to collect data from communication port.

        After device replies, we have to confirm receiving it by sending x06.
        Accumulate data until we have expected response length and its checksum is correct.

        :param data: input data stream
        """
        # Append new data into buffer
        self.buffer.append(data)
        # Generate bytearray
        full_response = b"".join(self.buffer)
        response_length = int.from_bytes(full_response[:2], "little")
        if len(full_response) >= response_length + 3:
            response = full_response[: response_length + 3]
            self.buffer = (
                [full_response[response_length:]]
                if response_length > len(full_response)
                else []
            )
            response_checksum = sum(full_response[2:-1]) % 256
            control_checksum = response[-1]

            response = response[2:-1]
            if response_checksum == control_checksum:
                self.handle_readout(response)
            else:
                # checksum is not OK, request packet again
                self.buffer = []
                # Ask for response again
                DeviceError("Checksum error!")

    def get_revision(self):
        self.send_command_data("H", self.t_byte(1))

    def get_version(self):
        self.send_command_data("H", self.t_byte(2))

    def get_firmware(self, callback=None):
        self.send_command_data("H", self.t_byte(3), callback=callback)

    def set_output_name(self, output, name):
        command_data = self.t_byte(output) + self.t_str(name)
        self.send_command_data("UO", command_data)

    def set_process_name(self, process, name):
        command_data = self.t_byte(process) + self.t_str(name)
        self.send_command_data("UK", command_data)

    def set_user_message(self, message, value):
        command_data = self.t_byte(message) + self.t_str(value)
        self.send_command_data("UV", command_data)

    @expose_method()
    def init_measurement(self):
        self.set_run_number(1)
        self.reset_thickness(1)
        self.set_start_layer(1)

    @expose_method()
    def stop_measurement(self):
        pass

    def set_active_process(self, process):
        command_data = self.t_byte(1) + self.t_int(process)
        self.send_command_data("UG", command_data)
        self.set_raw_value(ATTR_ACTIVE_PROCESS, process)

    def set_start_layer(self, layer):
        command_data = self.t_byte(2) + self.t_int(layer)
        self.send_command_data("UG", command_data)

    def set_run_number(self, value):
        command_data = self.t_byte(3) + self.t_int(value)
        self.send_command_data("UG", command_data)

    def remove_layers(self, process):
        command_data = self.t_byte(28) + self.t_byte(process)
        self.send_command_data("RG", command_data)

    def reset_thickness(self, layer):
        command_data = self.t_byte(1) + self.t_byte(layer)
        self.send_command_data("RL", command_data)

    def get_layer_thickness(self, layer):
        command_data = self.t_byte(4) + self.t_byte(layer)
        self.send_command_data("SL", command_data)


class InficonQcmSensorChannel(DeviceChannel):
    sensor_state = [
        "Good Crystal and active",
        "Failed Crystal and active",
        "Invalid Measurement on Crystal and active",
        "Good Crystal and inactive",
        "Failed Crystal and inactive",
        "Invalid Measurement on Crystal and inactive",
    ]
    sensor_type = ["Single", "XtalTwo", "XtalSix", "Xtal12", "Generic"]

    def __init__(self, device, channel, device_id=None, config=None):
        self.sensor_id = DeviceInficonQcm.t_int(channel + 1)
        DeviceChannel.__init__(self, device, channel, device_id, config)

    def _init_attributes(self):
        DeviceChannel._init_attributes(self)
        self.create_attribute(ATTR_STATE, readonly=True)
        self.add_attribute(
            ATTR_MATERIAL,
            self.device.get_attribute(
                [GROUP_MATERIALS, f"{ATTR_MATERIAL}_{self.channel + 1}"]
            ),
        )
        self.create_attribute(
            ATTR_SENSOR_TYPE,
            default_type=self.sensor_type,
            set_function=self.set_sensor_type,
        )
        self.create_attribute(
            ATTR_AUTO_Z, default_type=bool, set_function=self.set_auto_z
        )
        self.create_attribute(
            ATTR_Z_RATIO,
            default_value=None,
            default_type=float,
            readonly=True,
            decimals=9,
        )
        self.create_attribute(
            ATTR_FUNDAMENTAL_FREQUENCY,
            unit="Hz",
            default_value=None,
            default_type=numpy.double,
            readonly=True,
            decimals=9,
            factor=0.000873114913702011,
        )
        self.create_attribute(
            ATTR_AHARMONIC_FREQUENCY,
            unit="Hz",
            default_value=None,
            default_type=numpy.double,
            readonly=True,
            decimals=9,
            factor=0.000873114913702011,
        )
        self.create_attribute(
            ATTR_SENSOR_THICKNESS,
            unit="nm",
            default_value=0,
            default_type=float,
            readonly=True,
            decimals=9,
            factor=0.1,
        )
        self.create_attribute(
            ATTR_CRYSTAL_LIFE,
            unit="%",
            default_value=None,
            default_type=int,
            readonly=True,
        )
        self.create_attribute(
            ATTR_RAW_RATE,
            unit="nm/s",
            default_value=0,
            default_type=float,
            readonly=True,
            decimals=9,
            factor=0.1,
        )
        self.create_attribute(
            ATTR_SHUTTER_STROKES,
            default_value=0,
            default_type=int,
            readonly=True,
            save_change=True,
            min_value=0,
        )
        self.create_attribute(
            ATTR_SHUTTER_OPEN, default_value=False, default_type=bool, readonly=True
        )
        self.create_attribute(
            ATTR_LAYER_THICKNESS,
            unit="nm",
            default_value=0,
            default_type=float,
            readonly=True,
            decimals=9,
            factor=0.1,
        )

    def handle_configuration(self):
        if self.configured:
            return

        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()
            self.start_polling()
            self.close_shutter()
            self.configured = True
            self.set_status(STATUS_CONFIGURED)
            self.logger.info(
                "Device configuration took {} sec.".format(time.time() - start_at)
            )

        self.connected = True
        self.get_sensor_type()
        self.get_auto_z()
        self.set_shutter_logic()
        self.set_channel_to_material(callback=_finish_configuration)
        # Assign material # to process #
        self.device.send_command_data(
            "UP",
            self.device.t_byte(1)
            + self.device.t_byte(self.channel + 1)
            + self.device.t_byte(self.channel + 1)
            + self.sensor_id,
        )
        self.get_z_ratio()
        self.get_fundamental_frequency()
        self.get_aharmonic_frequency()
        self.get_sensor_thickness()
        self.get_raw_rate()
        _finish_configuration()

    def get_sensor_type(self):
        command_data = DeviceInficonQcm.t_byte(2) + DeviceInficonQcm.t_byte(
            self.channel + 1
        )
        self.device.send_command_data("QS", command_data)

    def get_auto_z(self):
        command_data = DeviceInficonQcm.t_byte(4) + DeviceInficonQcm.t_byte(
            self.channel + 1
        )
        self.device.send_command_data("QS", command_data)

    def get_z_ratio(self):
        command_data = DeviceInficonQcm.t_byte(6) + DeviceInficonQcm.t_byte(
            self.channel + 1
        )
        self.device.send_command_data("SS", command_data)

    def get_fundamental_frequency(self):
        command_data = DeviceInficonQcm.t_byte(4) + DeviceInficonQcm.t_byte(
            self.channel + 1
        )
        self.device.send_command_data("SS", command_data)

    def get_aharmonic_frequency(self):
        command_data = DeviceInficonQcm.t_byte(7) + DeviceInficonQcm.t_byte(
            self.channel + 1
        )
        self.device.send_command_data("SS", command_data)

    def get_sensor_thickness(self):
        command_data = DeviceInficonQcm.t_byte(12) + DeviceInficonQcm.t_byte(
            self.channel + 1
        )
        self.device.send_command_data("SS", command_data)

    def get_crystal_life(self):
        command_data = DeviceInficonQcm.t_byte(0) + DeviceInficonQcm.t_byte(
            self.channel + 1
        )
        self.device.send_command_data("SS", command_data)

    def get_raw_rate(self):
        command_data = DeviceInficonQcm.t_byte(13) + DeviceInficonQcm.t_byte(
            self.channel + 1
        )
        self.device.send_command_data("SS", command_data)

    def set_sensor_type(self, type):
        type_index = self.sensor_type.index(type)
        command_data = (
            DeviceInficonQcm.t_byte(2)
            + DeviceInficonQcm.t_byte(self.channel + 1)
            + DeviceInficonQcm.t_int(type_index)
        )
        self.device.send_command_data("US", command_data)

    def set_auto_z(self, value):
        command_data = (
            DeviceInficonQcm.t_byte(4)
            + DeviceInficonQcm.t_byte(self.channel + 1)
            + DeviceInficonQcm.t_int(value)
        )
        self.device.send_command_data("US", command_data)

    def subject_update(self, key, value, subject):
        DeviceChannel.subject_update(self, key, value, subject)
        if self.connected and isinstance(key, tuple) and key[0] == self.channel:
            if key[1] == ATTR_STATE:
                self.set_raw_value(key[1], self.sensor_state[value])
            elif key[1] == ATTR_SENSOR_TYPE:
                self.set_raw_value(key[1], self.sensor_type[value])
            else:
                self.set_raw_value(key[1], value)

    @expose_method()
    def open_shutter(self):
        index = 2 * (self.channel + 1)
        command_data = DeviceInficonQcm.t_byte(6) + DeviceInficonQcm.t_byte(index)
        self.device.send_command_data("RG", command_data)
        command_data = DeviceInficonQcm.t_byte(5) + DeviceInficonQcm.t_byte(index - 1)
        self.device.send_command_data("RG", command_data)
        if not self.get_value(ATTR_SHUTTER_OPEN):
            self.set_value(
                ATTR_SHUTTER_STROKES, self.get_value(ATTR_SHUTTER_STROKES) + 1
            )
            self.set_value(ATTR_SHUTTER_OPEN, True)

    @expose_method()
    def close_shutter(self):
        index = 2 * (self.channel + 1)
        command_data = DeviceInficonQcm.t_byte(6) + DeviceInficonQcm.t_byte(index - 1)
        self.device.send_command_data("RG", command_data)
        command_data = DeviceInficonQcm.t_byte(5) + DeviceInficonQcm.t_byte(index)
        self.device.send_command_data("RG", command_data)
        if self.get_value(ATTR_SHUTTER_OPEN):
            self.set_value(
                ATTR_SHUTTER_STROKES, self.get_value(ATTR_SHUTTER_STROKES) + 1
            )
            self.set_value(ATTR_SHUTTER_OPEN, False)

    @expose_method()
    def measure_layer_thickness(self):
        self.device.set_active_process(self.channel + 1)
        self.device.get_layer_thickness(1)

    @expose_method()
    def clear_shutter_strokes(self):
        self.set_value(ATTR_SHUTTER_STROKES, 0)

    def set_channel_to_material(self, callback=None):
        command_data = (
            DeviceInficonQcm.t_byte(114)
            + DeviceInficonQcm.t_byte(self.channel + 1)
            + self.sensor_id
        )
        self.device.send_command_data("UM", command_data, callback=callback)

    def set_shutter_logic(self):
        # Count starting index for Logic commands
        index = 2 * (self.channel + 1)
        # Setting logic for Shutter Open
        self.device.set_value(
            [GROUP_USER_MESSAGES, f"{ATTR_USER_MESSAGE}_{index}"],
            f"Shutter {self.channel + 1} open",
        )
        logic_statements = [
            DeviceInficonQcm.t_byte(0x7C),
            DeviceInficonQcm.t_byte(0x20),
            DeviceInficonQcm.t_byte(0x41),
            DeviceInficonQcm.t_byte(self.channel + 1),
            DeviceInficonQcm.t_byte(0x65),
            DeviceInficonQcm.t_byte(index - 1),
            DeviceInficonQcm.t_byte(0x64),
            DeviceInficonQcm.t_byte(index),
            DeviceInficonQcm.t_byte(0x03),
        ]
        command_data = [
            DeviceInficonQcm.t_byte(index - 1),
            DeviceInficonQcm.t_byte(len(logic_statements)),
        ] + logic_statements
        self.device.send_command_data("UL", b"".join(command_data))
        # Setting logic for Shutter Close
        self.device.set_value(
            [GROUP_USER_MESSAGES, f"{ATTR_USER_MESSAGE}_{index - 1}"],
            f"Shutter {self.channel + 1} closed",
        )
        logic_statements = [
            DeviceInficonQcm.t_byte(0x7C),
            DeviceInficonQcm.t_byte(0x20),
            DeviceInficonQcm.t_byte(0x42),
            DeviceInficonQcm.t_byte(self.channel + 1),
            DeviceInficonQcm.t_byte(0x65),
            DeviceInficonQcm.t_byte(index),
            DeviceInficonQcm.t_byte(0x64),
            DeviceInficonQcm.t_byte(index - 1),
            DeviceInficonQcm.t_byte(0x03),
        ]
        command_data = [
            DeviceInficonQcm.t_byte(index),
            DeviceInficonQcm.t_byte(len(logic_statements)),
        ] + logic_statements
        self.device.send_command_data("UL", b"".join(command_data))
