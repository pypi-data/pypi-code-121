import logging
import time
from logging import Logger
from logging.handlers import TimedRotatingFileHandler
from threading import Thread
from time import sleep
from typing import ValuesView

import numpy as np

from kamzik3 import DeviceError, DeviceUnknownError
from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.devices.device import Device
from kamzik3.snippets.snippetLogging import set_rotating_file_handler, set_file_handler
from kamzik3.snippets.snippetsTimer import PreciseCallbackTimer


class AttributeLogger(Device):
    """
    AttributeLogger is a parent Class for all derived Logger Classes.

    Logger itself is a Device.
    Logfile is rotating every day at 24:00.
    This Class is logging only Device's Attributes.
    Log entry is written every 'interval' tick.
    Logging starts automatically from the Session.

    Example of config file:
    session: !Device:kamzik3.devices.deviceSession.DeviceSession
        config:
            attributes:
              !!python/tuple [Log directory, Value]: ./server_log
            logged_attributes:
              # Device_Id: Device's Attribute
              # str: str | list
              X: Position
              Y: Position
              Z: Position
              Device: [Group, Attribute]
            # ... Other Session config attributes
    """

    # Logging interval in ms
    interval = 1e3
    # Value and separator separator
    separator = ";"
    logged_attributes = None
    attribute_logger = None
    attribute_logger_handler = None
    # User defined header, which is added before generated one
    preset_header = ""
    # Timer ticking at 'interval' frequency
    logger_ticker = None
    # Offset before start logging (10 seconds)
    start_offset = 10

    def __init__(self, log_file_name, device_id=None, config=None):
        # Check if logged_attributes were already set
        # (in case of Disconnected and Connected Device)
        if self.logged_attributes is None:
            self.logged_attributes = []
        # Holds actively logged attributes
        # This list is populated with Attribute's header
        self.active_log_attributes = []
        self.log_file_name = log_file_name
        # Define formatter for log entry
        self.log_formatter = logging.Formatter(
            self.separator.join(["%(asctime)s", "%(created)s", "%(message)s"]),
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        Device.__init__(self, device_id, config)
        self.connect()

    def connect(self, *args):
        self.handle_connect_event()
        self.set_status(STATUS_IDLE)

    def _init_attributes(self):
        """
        Init Device's attributes.

        ATTR_HEADER: Header of the current logfile
        ATTR_INTERVAL: Logging interval in ms
        ATTR_LAST_LOG_LINE: Last line written in logfile
        ATTR_LOGFILE: Path to the logfile, might be absolute or relative
        ATTR_LOGGING: Start / Stop logging toggle
        """
        super()._init_attributes()
        self.create_attribute(ATTR_HEADER, readonly=True)
        self.create_attribute(
            ATTR_INTERVAL,
            default_value=self.interval,
            min_value=100,
            max_value=3600 * 1e3,
            unit="ms",
            default_type=np.uint32,
            set_function=self._set_interval,
        )
        self.create_attribute(ATTR_LAST_LOG_LINE, readonly=True)
        self.create_attribute(
            ATTR_LOGFILE, default_value=self.log_file_name, readonly=True
        )
        self.create_attribute(ATTR_LOGGING, default_type=bool, set_function=self.start)

    def command(self, command, callback=None, with_token=False, returning=True):
        raise DeviceError("Device does not accept any commands.")

    def _set_interval(self, interval):
        """
        Set tick interval.

        :param int interval: interval in ms
        :return:
        """
        self.interval = interval
        if self.is_status(STATUS_BUSY):
            # If logging is running, stop it and start again
            self.stop()
            self.start()

    def _get_logged_attributes(self) -> ValuesView:
        """
        Collect all logged attributes.

        If a new attribute is discovered, it generates and writes a header.

        :return: ValuesView
        """
        logged_values = dict.fromkeys(self.active_log_attributes, str(np.NaN))
        generate_header = False
        if self.logged_attributes is not None:
            for device_id, attribute in self.logged_attributes:
                try:
                    device = self.session.get_device(device_id)
                    device_attribute = device.get_attribute(attribute)

                    if device_attribute is None:
                        logged_value = None
                        logged_type = ""
                        logged_unit = ""
                    else:
                        logged_value = device_attribute[VALUE]
                        logged_type = device_attribute[TYPE]
                        logged_unit = device_attribute[UNIT]
                    if logged_type == "":
                        logged_type = "str"
                    if logged_unit == "":
                        logged_unit = "None"
                    header_lookup = (
                        f"{device_id} {attribute} ({logged_type}, {logged_unit})"
                    )
                    if header_lookup not in self.active_log_attributes:
                        self.active_log_attributes.append(header_lookup)
                        generate_header = True
                    if logged_value is None:
                        logged_value = np.NaN
                    logged_values[header_lookup] = str(logged_value)

                except DeviceUnknownError:
                    continue
        if generate_header:
            self.write_header()
        return logged_values.values()

    def set_log_file_name(self, log_file_name) -> Logger:
        """
        Create a new logfile with the defined name.

        The logging level INFO is used for Attribute logging.

        :param filepath log_file_name: Filepath to the file
        :return: Logger
        """
        self.set_raw_value(ATTR_LOGFILE, log_file_name)
        attribute_logger = logging.getLogger(f"AttributeLogger.{self.device_id}")
        if self.attribute_logger_handler is not None:
            attribute_logger.removeHandler(self.attribute_logger_handler)

        if self.config.get("rotating", True):
            # Setup rotating log, if 'rotating' attribute is set
            self.attribute_logger_handler = set_rotating_file_handler(
                attribute_logger, self.log_file_name, self.log_formatter
            )

            def do_rollover():
                """
                Perform the rollover.

                We need to write the header at the beginning of each rotated file.
                """
                TimedRotatingFileHandler.doRollover(self.attribute_logger_handler)
                self.write_header()

            self.attribute_logger_handler.doRollover = do_rollover
        else:
            # In this case we have only one log file
            self.attribute_logger_handler = set_file_handler(
                attribute_logger, self.log_file_name, self.log_formatter
            )
        attribute_logger.setLevel(logging.INFO)
        return attribute_logger

    def handle_configuration(self):
        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()
            self.attribute_logger = self.set_log_file_name(self.log_file_name)
            self.set_status(STATUS_CONFIGURED)
            self.logger.info(
                "Device configuration took {} sec.".format(time.time() - start_at)
            )

        _finish_configuration()

    def handle_interval_timeout(self):
        """
        Callback for interval tick.

        In this method we write actual log entry.
        """
        logged_values = self._get_logged_attributes()
        if len(self.active_log_attributes) == 0:
            # If there is nothing to log, just return and don't write anything
            return
        last_log_line = self.separator.join(logged_values)
        self.set_raw_value(ATTR_LAST_LOG_LINE, last_log_line)
        if self.attribute_logger is not None:
            self.attribute_logger.info(last_log_line)

    def add_logged_attribute(self, device_id, attribute):
        """
        Add logged attribute.

        :param str device_id: Device ID
        :param Union[list, str, tuple] attribute: Device's Attribute
        """
        attribute = Attribute.list_attribute(attribute)
        item = (device_id, attribute)

        if item not in self.logged_attributes:
            self.logged_attributes.append(item)

    def remove_logged_attribute(self, device_id, attribute):
        """
        Remove logged Attribute.

        :param str device_id: Device ID
        :param Union[list, str, tuple] attribute: Device's Attribute
        """
        attribute = Attribute.list_attribute(attribute)
        self.logged_attributes.remove((device_id, attribute))

    def generate_header(self) -> str:
        """
        Generate the header for the log file.

        :return: str
        """
        header_line = [
            "Datetime ({}, {})".format("str", "None"),
            "Timestamp ({}, {})".format(np.dtype("float").name, "sec"),
        ]

        header_line += self.active_log_attributes
        return "# " + self.separator.join(header_line).replace("'", "").replace(
            ", ", ","
        )

    def write_line(self, line):
        """
        Write one line into log file.

        :param str line: formatted log line entry
        """
        self.attribute_logger_handler.flush()
        # Do we want to specify an encoding? Currently, it's system dependent
        # pylint: disable=unspecified-encoding
        with open(self.log_file_name, "a+") as fp:
            fp.write(line)
            fp.write("\n")

    def write_header(self):
        """
        Write header to the log file.

        New header is created from preset_header + generated_header
        """
        header = self.preset_header + self.generate_header()
        self.set_raw_value(ATTR_HEADER, header)
        self.write_line(header)

    def start(self, flag=True):
        """
        Start logging.

        By default Timer is started ticking at 'interval' frequency.
        Override this method if You need different start of the logger.
        If flag is True start logger, stop otherwise.

        :param bool flag: Toggle flag
        """
        if flag:
            if self.logger_ticker is not None and self.is_status(STATUS_BUSY):
                self.logger_ticker.stop()
                raise DeviceError("Logging is already running")
            self.logger_ticker = PreciseCallbackTimer(
                self.interval, self.handle_interval_timeout, with_correction=True
            )
            self.set_status(STATUS_BUSY)

            def _start():
                sleep(self.start_offset)
                self.logger_ticker.start()

            Thread(target=_start).start()
        else:
            self.stop()

    def stop(self):
        """Stop logging."""
        try:
            self.logger_ticker.stop()
            self.set_status(STATUS_IDLE)
        except TypeError:
            pass

    def close(self):
        self.stop()
        super().close()

    def disconnect(self):
        # Remove all handlers
        self.stop()
        try:
            for handler in self.attribute_logger.handlers[:]:
                handler.close()
        except AttributeError:
            # No attribute_logger in which case just continue
            pass
        self.logged_attributes = None
        self.attribute_logger = None
        self.attribute_logger_handler = None
        self.logged_attributes = []
        self.log_formatter = None
        return super().disconnect()


class AttributeLoggerTriggered(AttributeLogger):
    """
    Logger is used for Macros.

    Instead of periodically adding a new line, we log only when externally triggered.
    """

    def start(self, flag=True):
        """
        Generate the header and wait for external triggers.

        :param bool flag: Toggle flag
        """
        if flag:
            if self.is_status(STATUS_BUSY):
                raise DeviceError("Logging is already running")

            for device_id, attribute in self.logged_attributes:
                try:
                    device = self.session.get_device(device_id)
                    device_attribute = device.get_attribute(attribute)
                    logged_type = device_attribute[TYPE]
                    logged_unit = device_attribute[UNIT]
                    if logged_type == "":
                        logged_type = "str"
                    if logged_unit == "":
                        logged_unit = "None"
                    header_lookup = (
                        f"{device_id} {attribute} ({logged_type}, {logged_unit})"
                    )
                    if header_lookup not in self.active_log_attributes:
                        self.active_log_attributes.append(header_lookup)
                except DeviceUnknownError:
                    continue

            self.write_header()
            self.set_status(STATUS_BUSY)
        else:
            self.stop()

    def trigger(self):
        """
        Get a external trigger.

        This method is a wrapper for handle_interval_timeout of Parent AttributeLogger.
        """
        self.handle_interval_timeout()

    def stop(self):
        """Stop logging."""
        try:
            self.set_status(STATUS_IDLE)
        except TypeError:
            pass
