""" module:: hcscom.hcscom
    :synopsis: An interface class to manson hcs lab power supplies
    moduleauthor:: Patrick Menschel (menschel.p@posteo.de)
    license:: GPLv3 or later.
"""

import serial
import logging

from typing import Union
from enum import Enum, IntEnum

from hcscom.lockfile import LockFile, DeviceAlreadyInUseException

LOGGER = logging.getLogger(__name__)


class ResponseStatus(Enum):
    """
    An Enumeration for the response status.

    Only "OK" has been seen so far.
    """
    ok = "OK"


class OutputStatus(IntEnum):
    """
    An Enumeration for the output status.

    The logic is inverted: off (1), on (0).
    """
    off = 1
    on = 0


class DisplayStatus(IntEnum):
    """
    An Enumeration of display status.

    There are also undocumented values.
    """
    cv = 0
    cc = 1


# Format values for printing
FORMAT_THREE_DIGITS = "{:04.1f}"
FORMAT_FOUR_DIGITS = "{:05.2f}"


def format_to_width_and_decimals(fmt: str):
    """
    A helper function to extract width and number of decimal places out of a format string.

    :param fmt: a regular format string
    :return: The number of overall decimal places in the data representation and
             the number of decimal places behind the colon (.)
    """
    width, decimals = [int(x) for x in fmt.split(":")[-1].strip("f}").split(".")]
    return width - 1, decimals


def split_data_to_values(data: str = "320160", width: int = 3, decimals: int = 1):
    """
    A helper function to split the values from device.

    :param data: The data bytes that are to be split
    :param width: The width of one item in data, usually set by device type
    :param decimals: The number of decimal places right of the colon (.)
    :return: A tuple of values that were extracted from data.
    """
    values = tuple(int(data[idx:idx + width]) / (10 ** decimals) for idx in range(0, len(data), width))
    return values


def format_val(val, fmt):
    """
    A helper function to format a value to the data representation.

    :param val: The value to be formatted.
    :param fmt: The format string to be used.
    :return: The formatted data representation.
    """
    ret = fmt.format(val).replace(".", "")
    return ret


class HcsCom:
    """
    A class to abstract a smart power supply unit (psu) of hcs type.

    :param port: The serial port which the devices is connected to.
                 This can be either a serial.Serial or a port name string.
    """

    def __init__(self, port: Union[str, serial.Serial]):
        self.filelock = None
        if isinstance(port, str):
            try:
                self.filelock = LockFile(device_name=port)
                self.ser = serial.Serial(port=port, baudrate=9600, timeout=1)
            except (serial.SerialException, FileNotFoundError, DeviceAlreadyInUseException) as e:
                print(e)
                exit(1)
        elif isinstance(port, serial.Serial):
            # if a serial port is given we assume that the caller assured that the device is not in use.
            self.filelock = LockFile(device_name=port.name)
            self.ser = port
        else:
            raise ValueError("Not handling {0}".format(type(port)))

        self.ser.flush()
        self.model = None
        self.max_voltage = None
        self.max_current = None
        self.value_format = None
        self.width = None
        self.decimals = None
        self.set_format(FORMAT_THREE_DIGITS)
        self.presets = None

        self.probe_device()

    def __del__(self):
        if hasattr(self, "ser") and self.ser is not None:
            self.ser.close()
        if self.filelock is not None:
            self.filelock.release()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.filelock.release()

    def set_format(self, fmt: str) -> None:
        """
        A helper function to set the format and keep consistency.

        :param fmt: The format string.
        :return: None
        """
        self.value_format = fmt
        self.width, self.decimals = format_to_width_and_decimals(self.value_format)

    def request(self, message: str) -> Union[str, None]:
        """
        Send a command to the device and receive the response.

        This function handles the communication flow.

        :param message: The message to send to the device.
        :return: The returned "raw" response data.
        """
        LOGGER.debug(">> {0}".format(message))
        msg_ = bytearray()
        msg_.extend(message.encode())
        msg_.extend(b"\r")
        with self.ser as ser:
            ser.write(msg_)
            ret = None
            for i in range(2):
                data = ser.read_until(b"\r")
                LOGGER.debug("<< {0}".format(data.decode()))
                if data == b"OK\r":
                    return ret
                else:
                    ret = data.strip(b"\r").decode()
        raise RuntimeError("Got unexpected response, {0}".format(data))

    def probe_device(self) -> None:
        """
        Probe for a device.

        Find out if a device is present and retrieve device information if possible.

        :return: None
        """
        self.model = self.get_model()
        data = self.request("GMAX")
        if len(data) == 6:
            fmt = FORMAT_THREE_DIGITS
        elif len(data) == 8:
            fmt = FORMAT_FOUR_DIGITS
        else:
            raise RuntimeError("Could not determine format from {0}".format(data))
        self.set_format(fmt)
        self.max_voltage, self.max_current = split_data_to_values(data, width=self.width, decimals=self.decimals)
        self.presets = self.get_presets_from_memory()

    def __str__(self) -> str:
        """
        The string representation of the device.

        This is for informative purposes.
        """
        max_values = self.get_max_values()
        return "Device: {0}\nV: {1}V A: {2}".format(self.model, max_values.get("voltage"), max_values.get("current"))

    def get_max_values(self) -> dict:
        """
        Get the max values of the device.

        The Limits are device specific and are read out during probe_device().

        :return: A dictionary with keys "voltage" and "current".
        """
        return {"voltage": self.max_voltage,
                "current": self.max_current}

    def switch_output(self, output: OutputStatus) -> None:
        """
        Switch the output of the device.

        :param output: The switch value, either OutputStatus.on or OutputStatus.off.
        :return: None
        """
        assert output in [OutputStatus.off, OutputStatus.on]
        return self.request("SOUT{0}".format(output))

    def set_voltage(self, voltage: float) -> None:
        """
        Set the output voltage.

        This becomes effective immediately.

        :param voltage: The voltage (limit) to be set.
        :return: None
        """
        return self.request("VOLT{0}".format(format_val(voltage, self.value_format)))

    def set_current(self, current: float) -> None:
        """
        Set the output current limit.

        This becomes effective immediately.

        :param current: The current limit to be set.
        :return: None
        """
        return self.request("CURR{0}".format(format_val(current, self.value_format)))

    def get_presets(self) -> tuple:
        """
        Get the current active preset values for voltage and current.

        A preset is not necessarily what is currently active because
        that can be altered by set_voltage() and set_current() while
        leaving the preset alone.

        :return: A tuple of float values, voltage and current.
        """
        data = self.request("GETS")
        voltage, current = split_data_to_values(data, width=self.width, decimals=self.decimals)
        return voltage, current

    def get_display_status(self) -> dict:
        """
        Get the current display status.

        This basically returns a representation of the visual output of the device.
        What values are on the display and what indicators are set, etc..

        :return: A dictionary with the keys "voltage", "current" and "status".
        """
        data = self.request("GETD")
        voltage, current = split_data_to_values(data[:-1], width=4,
                                                decimals=2)  # XXXXYYYYZ FORMAT regardless of regular format
        status_ = int(data[-1])  # we don't know if this is a valid status yet.
        try:
            status = DisplayStatus(status_)
        except ValueError as e:
            LOGGER.error("get_display_status: {0}".format(e))
            status = status_
        return {"voltage": voltage,
                "current": current,
                "status": status}

    def set_presets_to_memory(self, presets: dict) -> None:
        """
        Program preset values into memory of the device.

        :param presets: A dictionary with keys 0,1 and 2.
                        Each item is a tuple of voltage and current.
        :return: None
        """
        # default_presets = {0: (5, self.max_current),
        #                    1: (13.8, self.max_current),
        #                    2: (self.max_voltage, self.max_current),
        #                    }
        values = []
        assert set(presets.keys()) == {0, 1, 2}
        for idx in range(len(presets)):
            values.extend(presets.get(idx))
        assert len(values) == 6
        content = "".join([format_val(value, self.value_format) for value in values])
        return self.request("PROM{0}".format(content))

    def get_presets_from_memory(self) -> dict:
        """
        Get the presets from device memory.

        The device has three presets.

        :return: A dictionary with keys 0,1 and 2.
                 Each item is a tuple of voltage and current.
        """
        data = self.request("GETM")
        voltage1, current1, voltage2, current2, voltage3, current3 = split_data_to_values(data,
                                                                                          width=self.width,
                                                                                          decimals=self.decimals)

        return {0: (voltage1, current1),
                1: (voltage2, current2),
                2: (voltage3, current3),
                }

    def load_preset(self, preset_index: int) -> None:
        """
        Load a preset.

        :param preset_index: The index of the preset. May be 0, 1 or 2.
        :return: None
        """
        assert preset_index in range(3)
        return self.request("RUNM{0}".format(preset_index))

    def get_output_voltage_preset(self) -> float:
        """
        Get the preset voltage.

        :return: The voltage value.
        """
        data = self.request("GOVP")
        voltage = split_data_to_values(data, width=self.width, decimals=self.decimals)[0]
        return voltage

    def set_output_voltage_preset(self, voltage: float) -> None:
        """
        Set the voltage of this preset.

        :param voltage: The voltage to be set.
        :return: None
        """
        return self.request("SOVP{0}".format(format_val(voltage, self.value_format)))

    def get_output_current_preset(self) -> float:
        """
        Get the preset current.

        :return: The current value.
        """
        data = self.request("GOCP")
        current = split_data_to_values(data, width=self.width, decimals=self.decimals)[0]
        return current

    def set_output_current_preset(self, current: float) -> None:
        """
        Set the current of this preset.

        :param current: The current to be set.
        :return: None
        """
        return self.request("SOCP{0}".format(format_val(current, self.value_format)))

    def get_model(self) -> str:
        """
        Get the model information from the device.

        :return: The model name.
        """
        model = self.request("GMOD")
        LOGGER.info("GMOD returned model {0}".format(model))
        return model


if __name__ == "__main__":
    import argparse
    import numpy as np
    import time

    parser = argparse.ArgumentParser()
    parser.add_argument("port")
    args = parser.parse_args()
    port = args.port
    hcs = HcsCom(port=port)
    max_volt = hcs.get_max_values().get("voltage")
    input("Testing stepping through the output voltage range - be sure nothing is connected! - Press Enter")
    hcs.set_current(0.5)  # This is a test, so expect user errors as well
    hcs.switch_output(OutputStatus.on)
    for volt in np.arange(1, max_volt, 0.5):
        hcs.set_voltage(volt)
        time.sleep(.5)
    hcs.load_preset(0)  # select a harmless preset with 5V
    hcs.switch_output(OutputStatus.off)
