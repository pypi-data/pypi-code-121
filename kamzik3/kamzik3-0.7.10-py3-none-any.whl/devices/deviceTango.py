import datetime
import os
import re
import time
from threading import Thread

import numpy as np

from kamzik3 import DeviceError, units
from kamzik3.constants import *
from kamzik3.devices.device import Device
from kamzik3.snippets.snippetsDecorators import expose_method
from kamzik3.snippets.snippetsUnits import device_units

try:
    import PyTango
    from PyTango import DeviceProxy
except ImportError:
    raise DeviceError("PyTango import error!")

ATTR_TANGO_STATUS = "Tango status"

helptext = """
Example of yaml configuration

Lambda: !Device:kamzik3.devices.deviceTango.DeviceTango
    path: tango://mll-lambda.desy.de:10000/mll/lambda/01
    config:
      poll_attributes:
        - [SaveFileName, 300]
        - [FileStartNum, 300]
        - [SaveFilePath, 500]
        - [EnergyThreshold, 1000]
        - [ShutterTime, 1000]
        - [FilePreExt, 1000]
        - [FramesPerFile, 1000]
"""


class DeviceTango(Device, DeviceProxy):
    def __init__(self, path, device_id=None, config=None):
        self.path = path
        self.tango_attributes = []
        self.tango_commands = []
        self.tango_exceptions = (
            PyTango.ConnectionFailed,
            PyTango.CommunicationFailed,
            PyTango.DevFailed,
            PyTango.DeviceUnlocked,
        )
        Device.__init__(self, device_id, config)
        self.connect()

    def connect(self, *args):
        """
        Call only this function to connect devices to port / socket / library / ...
        :param args: connect attributes
        """
        self.connecting = True
        try:
            DeviceProxy.__init__(self, self.path)
        except self.tango_exceptions as e:
            self.handle_connection_error(e)
            return

        self.handle_configuration_event()
        self.connected = True
        self.connecting = False

    def handle_configuration(self):
        start_at = time.time()

        try:
            self.tango_attributes = set(self.get_attribute_list()) - set(
                self.attributes.keys()
            )
        except self.tango_exceptions as e:
            self.handle_connection_error(e)
            raise e

        self.tango_commands = self.command_list_query()

        for attribute in self.tango_attributes:
            try:
                ta = self.read_attribute(attribute)
            except self.tango_exceptions as e:
                self.handle_command_error(attribute, str(e))
                continue

            # FIXME: Can't we just disable the callback here? Check back when we have a type for the "set_function"
            # parameter for create_attribute
            def set_function(value, attribute_name=attribute, callback=None):
                try:
                    self.write_attribute(attribute_name, value)
                except (self.tango_exceptions, (AttributeError, TypeError)) as e:
                    raise DeviceError(e)

            tc = self.get_attribute_config(attribute)

            default_type = "str"
            value = ta.value
            min_value, max_value = None, None
            decimals = 0
            if isinstance(value, np.ndarray):
                continue
            if tc.data_type == PyTango._tango.CmdArgType.DevLong:
                # Not array
                if tc.max_dim_x == 1 and tc.max_dim_y == 0:
                    default_type = np.float32
                    min_value, max_value = self._get_tango_limits(tc, default_type)
                    value = float(value)
            elif tc.data_type == PyTango._tango.CmdArgType.DevBoolean:
                # Not array
                if tc.max_dim_x == 1 and tc.max_dim_y == 0:
                    default_type = bool
                    value = bool(value)
            elif tc.data_type in (
                PyTango._tango.CmdArgType.DevDouble,
                PyTango._tango.CmdArgType.DevFloat,
            ):
                # Not array
                if tc.max_dim_x == 1 and tc.max_dim_y == 0:
                    default_type = np.float64
                    min_value, max_value = self._get_tango_limits(tc, default_type)
                    value = float(value)
                    decimals_re = re.search(r"%[0-9]+\.([0-9]+)f", tc.format)
                    if decimals_re is not None:
                        decimals = int(decimals_re.group(1))
            elif tc.data_type == PyTango._tango.CmdArgType.DevULong:
                # Not array
                if tc.max_dim_x == 1 and tc.max_dim_y == 0:
                    default_type = np.uint32
                    min_value, max_value = self._get_tango_limits(tc, default_type)
                    value = int(value)
            elif tc.data_type == PyTango._tango.CmdArgType.DevShort:
                # Not array
                if tc.max_dim_x == 1 and tc.max_dim_y == 0:
                    default_type = np.int16
                    min_value, max_value = self._get_tango_limits(tc, default_type)
                    value = int(value)
            elif tc.data_type == PyTango._tango.CmdArgType.DevUShort:
                # Not array
                if tc.max_dim_x == 1 and tc.max_dim_y == 0:
                    default_type = np.uint16
                    min_value, max_value = self._get_tango_limits(tc, default_type)
                    value = int(value)
            else:
                value = str(value)

            try:
                if tc.unit is None:
                    unit = ""  # "" raises an AttributeError in pint
                elif tc.unit == "%":
                    unit = tc.unit  # "%" raises an AttributeError in pint
                elif tc.unit != "" and tc.unit not in units:
                    self.logger.info(
                        f"{self.device_id}: not a valid unit '{tc.unit}', "
                        "default unit to ''"
                    )
                    unit = ""
                else:
                    unit = tc.unit
            except (ValueError, TypeError):  # issue with parsing in pint
                self.logger.error(
                    f"{self.device_id}: can't parse {tc.unit}, default unit to ''"
                )
                unit = ""

            self.create_attribute(
                attribute,
                default_value=value,
                readonly=not ta.nb_written,
                description=tc.description,
                default_type=default_type,
                set_function=set_function,
                unit=unit,
                min_value=min_value,
                max_value=max_value,
                decimals=decimals,
            )

        for command in self.tango_commands:
            command_name = command.cmd_name
            # Since this device is already DeviceProxy all methods are callable
            # Just add them to exposed methods and we are done :)
            self.exposed_methods.append((command_name, None))

        self.start_polling()
        self._config_commands()
        self._config_attributes()
        self.set_status(STATUS_CONFIGURED)
        self.logger.info(
            "Device configuration took {} sec.".format(time.time() - start_at)
        )

    def start_polling(self):
        super().start_polling()
        self.poll_attribute("State", self.config.get("base polling rate", 100))
        self.poll_command("State", self.config.get("base polling rate", 100))

        for poll_attribute in self.config.get("poll_attributes", []):
            tango_attribute, timeout = poll_attribute
            self.poll_attribute(tango_attribute, timeout)
            self.poll_command(tango_attribute, timeout)

    def stop_polling(self):
        super().stop_polling()
        try:
            self.stop_poll_attribute("State")

            for poll_attribute in self.config.get("poll_attributes", []):
                tango_attribute, _timeout = poll_attribute
                self.stop_poll_attribute(tango_attribute)
        except self.tango_exceptions:
            pass

    def command(self, command, callback=None, with_token=False, returning=True):
        raise DeviceError("Device does not accept any commands.")

    def command_inout(self, param):
        try:
            return DeviceProxy.command_inout(self, param)
        except self.tango_exceptions as e:
            raise DeviceError(e)

    def send_command(self, commands):
        for command in commands:
            tango_attribute = command[0]
            try:
                polled_attribute = self.attribute_history(tango_attribute, 1)[0]
            except UnicodeDecodeError:
                continue
            except self.tango_exceptions as e:
                if e.args[0].reason == "API_CantConnectToDevice":
                    self.handle_connection_error(e)
                    return []
                elif e.args[0].reason == "API_NoDataYet":
                    return []
                else:
                    self.handle_command_error(command, e)
                    continue

            self.set_raw_value(tango_attribute, polled_attribute.value)
            if tango_attribute == "State":
                if polled_attribute.value in (
                    PyTango.DevState.MOVING,
                    PyTango.DevState.RUNNING,
                ):
                    self.set_status(STATUS_BUSY)
                elif polled_attribute.value in (
                    PyTango.DevState.ON,
                    PyTango.DevState.STANDBY,
                ):
                    self.set_status(STATUS_IDLE)
                elif polled_attribute.value == PyTango.DevState.INIT:
                    self.set_status(STATUS_CONFIGURING)
                elif polled_attribute.value in (
                    PyTango.DevState.DISABLE,
                    PyTango.DevState.UNKNOWN,
                ):
                    self.set_status(STATUS_DISCONNECTED)
                else:
                    self.set_status(STATUS_ERROR)
        self.response_timestamp = time.time()
        return []

    def valid_command_format(self, command):
        return True

    @staticmethod
    def _get_tango_limits(tc, type_cast):
        if tc.min_value == "Not specified":
            min_value = None
        else:
            min_value = type_cast(tc.min_value)
        if tc.max_value == "Not specified":
            max_value = None
        else:
            max_value = type_cast(tc.max_value)
        return min_value, max_value


class DeviceTangoLambdaDetector(DeviceTango):
    def handle_configuration(self):
        try:
            super().handle_configuration()
            current_mode = self.attributes["OperatingMode"][VALUE]
            self.create_attribute(
                "OperatingMode",
                group="Mode",
                default_value=current_mode,
                default_type=["ContinuousReadWrite", "TwentyFourBit"],
                set_function=self.set_mode,
            )
            self.attributes["FrameNumbers"][MIN] = 1
        except self.tango_exceptions:
            # Exception was handled on DeviceTango level
            pass

    @expose_method({"Mode": "Opertaing mode"})
    def set_mode(self, Mode):
        """
        For some reason changing mode is completely blocking action.

        There is no status indication, no documentation.
        We just have to stop polling and waiting for some time.
        To be safe waiting time is set to 10s.
        :param Mode:
        """
        if self.get_value("OperatingMode") != Mode:

            def _set():
                self.stop_polling()
                self.set_attribute([ATTR_ENABLED, VALUE], False)
                self.set_status(STATUS_BUSY)
                time.sleep(0.2)
                self.write_attribute_asynch("OperatingMode", Mode)
                self._set(["OperatingMode", VALUE], Mode)
                time.sleep(9)
                self.start_polling()
                self.set_attribute([ATTR_ENABLED, VALUE], True)

            Thread(target=_set).start()

    @expose_method(
        {
            "Name": "FilePrefix",
            "Exposure": "ShutterTime",
            "Frames": "FrameNumbers",
            "Save": "SaveAllImages",
        }
    )
    def acquire_frame(self, Name, Exposure, Frames, Save):
        now = datetime.datetime.now()
        self.set_attribute(["TriggerMode", VALUE], 0)
        self.set_attribute(["SaveFilePath", VALUE], self.config.get("shotDir"))
        self.set_attribute(
            ["FilePreExt", VALUE],
            "_{}_{}".format(self.device_id, now.strftime("%Y-%m-%d_%H:%M:%S")),
        )
        self.set_attribute(["FilePrefix", VALUE], Name)
        self.set_attribute(["FileStartNum", VALUE], 0)
        Exposure = device_units(self, "ShutterTime", Exposure).m
        self.set_attribute(["ShutterTime", VALUE], float(Exposure))
        Frames = device_units(self, "FrameNumbers", Frames).m
        self.set_attribute(["FrameNumbers", VALUE], int(float(Frames)))
        self.set_attribute(["SaveAllImages", VALUE], int(bool(Save)))
        self.StartAcq()

    @expose_method({"Exposure": "ShutterTime"})
    def live_view(self, Exposure):
        Exposure = device_units(self, "ShutterTime", Exposure).m
        self.set_attribute(["ShutterTime", VALUE], float(Exposure))
        self.set_attribute(["SaveAllImages", VALUE], False)
        self.set_attribute(["LiveMode", VALUE], True)
        self.set_attribute(["FrameNumbers", VALUE], 100000)
        self.set_attribute(["TriggerMode", VALUE], 0)
        self.StartAcq()

    @expose_method({"Exposure": "ShutterTime", "Frames": "FrameNumbers"})
    def acquire_scan_frame(self, Exposure, Frames):
        Exposure = float(device_units(self, "ShutterTime", Exposure).m)
        if Exposure != self.get_value("ShutterTime"):
            self.set_attribute(["ShutterTime", VALUE], Exposure)
        Frames = int(float(device_units(self, "FrameNumbers", Frames).m))
        if Frames != self.get_value("FrameNumbers"):
            self.set_attribute(["FrameNumbers", VALUE], Frames)
        time.sleep(1)
        self.StartAcq()

    @expose_method()
    def stop(self):
        self.StopAcq()
