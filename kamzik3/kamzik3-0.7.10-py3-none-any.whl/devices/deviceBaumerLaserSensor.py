import re
import time
from typing import Optional

import numpy as np
import serial
from bidict import bidict

import kamzik3
from kamzik3.constants import *
from kamzik3.devices.devicePort import DevicePort
from kamzik3.devices.deviceSocket import DeviceSocket
from kamzik3.snippets.snippetsDecorators import expose_method

MEASUREMENT_SCALE = bidict(
    {
        "U": "Value in 1um",
        "H": "Value in 0.01mm",
        "Z": "Value in 0.1mm",
        "M": "Value in 1mm",
        "S": "Sensor unit",
        "R": "Raw value",
    }
)
MEASUREMENT_FACTORS = {
    "Value in 1um": 1000,
    "Value in 0.01mm": 100,
    "Value in 0.1mm": 10,
    "Value in 1mm": 1,
    "Sensor unit": 1,
    "Raw value": 1,
}
MEASUREMENT_UNITS = {
    "Value in 1um": "um",
    "Value in 0.01mm": "mm",
    "Value in 0.1mm": "mm",
    "Value in 1mm": "mm",
    "Sensor unit": "",
    "Raw value": "",
}


class DeviceBaumerLaserSensorPort(DeviceSocket):
    """
    Optoelectronic sensor, using laser to measure distance.

    Documentation at:
    https://svnsrv.desy.de/desy/cfel-cxi/doc/manuals/Baumer/OADM_13T7480_S35A_manual.pdf

    Example of config file:

    Laser_Sensor: &Laser_Sensor !Device:kamzik3.devices.deviceBaumerLaserSensor.DeviceBaumerLaserSensorSocket
    port: /dev/ttyS2
    device_id: Laser_Sensor
    config:
      attributes:
        !!python/tuple [Distance, Offset]: 50
        !!python/tuple [Measuring scale, Value]: Value in 0.1mm
    """

    error_pattern = re.compile(r"^{0E[A-Z0-9]+}$")
    terminator = b"}"
    push_commands_max = 1

    def handle_configuration(self):
        """Send Command '{0}' to get sensor configuration."""
        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()
            self.start_polling()
            self.set_status(STATUS_CONFIGURED)
            self.logger.info(
                "Device configuration took {} sec.".format(time.time() - start_at)
            )

        self.command("{0V}", callback=_finish_configuration)

    def _init_attributes(self):
        """
        Initialize the attributes.

        All values are readonly.

        Attributes:
            ATTR_SOFTWARE_VERSION: Version of sensor's SW
            ATTR_HARDWARE_VERSION: Version of sensor's HW
            ATTR_MANUFACTURE_DATE: Sensor's manufacture date
            ATTR_MODES: Modes of operation
            ATTR_MEASURING_SCALE: Measurement scale
            ATTR_DISTANCE: Measured distance
        """
        DeviceSocket._init_attributes(self)
        self.create_attribute(ATTR_SOFTWARE_VERSION, readonly=True)
        self.create_attribute(ATTR_HARDWARE_VERSION, readonly=True)
        self.create_attribute(ATTR_MANUFACTURE_DATE, readonly=True)
        self.create_attribute(ATTR_MODES, readonly=True)
        self.create_attribute(
            ATTR_MEASURING_SCALE,
            readonly=True,
            default_type=MEASUREMENT_SCALE.inv.keys(),
            set_function=self.set_measuring_scale,
        )
        self.create_attribute(
            ATTR_DISTANCE,
            default_value=0,
            default_type=np.float,
            readonly=True,
            unit="mm",
            decimals=4,
        )

    def handle_readout(self, readout_buffer):
        """
        Handle readout from Device.

        :param str readout_buffer: raw readout buffer from Device
        """
        command, output, callback, token = DevicePort.handle_readout(
            self, readout_buffer
        )
        is_error_message = self.error_pattern.match(output + "}")
        # checksum = output[-2:]  # to simplify communication, ignore checksum
        output = output[2:-2]
        if is_error_message is not None:
            # Handle device error
            self.handle_command_error(command, readout_buffer)
            command = RESPONSE_ERROR
        elif command == "{0V}":
            # Parse Device configuration
            # output_format = output[2]  # not used
            # waiting_time_pddm = output[3]  # not used
            readout_modes = output[18:]
            self.set_raw_value(ATTR_SOFTWARE_VERSION, output[4:10])
            self.set_raw_value(ATTR_HARDWARE_VERSION, output[10:12])
            self.set_raw_value(ATTR_MANUFACTURE_DATE, output[12:18])
            self.set_raw_value(ATTR_MODES, readout_modes)
            self.set_raw_value(ATTR_MEASURING_SCALE, MEASUREMENT_SCALE[output[1]])
            self.set_attribute(
                [ATTR_DISTANCE, UNIT], MEASUREMENT_UNITS[MEASUREMENT_SCALE[output[1]]]
            )
        elif command == "{0M}":
            # Parse and store measured distance
            values = re.match("^M([MA]+[0-9]+)+$", output)
            for group in values.groups():
                if group[0] == "M":
                    factor = MEASUREMENT_FACTORS[self.get_value(ATTR_MEASURING_SCALE)]
                    distance = int(group[1:]) / factor
                    self.set_raw_value(ATTR_DISTANCE, distance)

        if callback is not None:
            # Call Callback in case it's set
            self.handle_readout_callback(callback, command, readout_buffer)
        if token:
            # Publish command, readout_buffer in case token was set
            kamzik3.session.publisher.push_message(
                self.device_id, [command, str(readout_buffer)], token
            )

    def set_measuring_scale(self, value, callback=None) -> Optional[int]:
        """
        Set measuring scale.

        :param str value: One of MEASUREMENT_UNITS values
        :param Callable callback: Optional callback function
        :return int: token
        """
        self.logger.info("Setting measuring scale to {}".format(value))
        self.set_attribute([ATTR_DISTANCE, UNIT], MEASUREMENT_UNITS[value])
        return self.command(
            "{{0S{}}}".format(MEASUREMENT_SCALE.inverse.get(value)),
            callback,
            with_token=True,
        )

    @expose_method()
    def laser_on(self, callback=None) -> Optional[int]:
        """
        Turn on the laser.

        Measure distance continuously.
        :param Callable callback: Optional callback function
        :return int: token
        """
        self.logger.info("Setting laser On")
        return self.command("{0L1}", callback, with_token=True)

    @expose_method()
    def laser_off(self, callback=None) -> Optional[int]:
        """
        Torn off the laser.

        Stop measurement.
        :param Callable callback: Optional callback function
        :return int: token
        """
        self.logger.info("Setting laser Off")
        return self.command("{0L0}", callback, with_token=True)

    @expose_method()
    def measure_distance(self, callback=None) -> Optional[int]:
        """
        Sample out one distance measurement.

        Turn Laser on, Measure distance, Turn Lase off
        In our use case we don't need constant measurement.
        If You need in other use case constant measurement, just setup polling for
        '{0M}' command.

        :param Callable callback: Optional callback function
        :return int: token
        """
        self.logger.info("Measuring distance")
        self.laser_on()
        out = self.command("{0M}", callback, with_token=True)
        self.laser_off()
        return out

    def stop(self):
        """Turn off the laser."""
        self.logger.info("Stop device")
        self.laser_off()


# abstract methods `collect_incoming_data` and `found_terminator` are defined in
# DeviceSocket (base class of DeviceBaumerLaserSensorPort). Since multiple inheritance
# is used here we better disable the pylint warning.
# pylint: disable=abstract-method
# see https://github.com/python/mypy/issues/9319 for mypy error
class DeviceBaumerLaserSensorSocket(DevicePort, DeviceBaumerLaserSensorPort):  # type: ignore
    """Extend ETH controller to enable RS232 connection."""

    terminator = b"}"

    # pylint: disable=super-init-not-called
    def __init__(
        self,
        port,
        baud_rate=38400,
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
        self.push(b"{0V}")
        time.sleep(0.05)  # Give some time for devices to reply
        if self.serial_port.in_waiting != 0:
            output = self.read_all().strip()
            is_error_message = self.error_pattern.match(output)
            return is_error_message is None
        return False
