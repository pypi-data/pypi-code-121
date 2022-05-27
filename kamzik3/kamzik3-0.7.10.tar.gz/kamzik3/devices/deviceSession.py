from __future__ import annotations
import logging
import os
import shutil
import time
from collections import OrderedDict
from threading import RLock
from multiprocessing import Process
from multiprocessing.synchronize import Event as EventType
import numpy as np
import oyaml as yaml
import psutil
from typing import List, Tuple, Union

import kamzik3
from kamzik3 import DeviceUnknownError, DeviceError
from kamzik3.constants import *
from kamzik3.devices.attributeLogger import AttributeLogger, ATTR_LOGGING
from kamzik3.devices.device import Device
from kamzik3.devices.deviceClient import DeviceClient
from kamzik3.devices.general.measurementGroup import MeasurementGroup
from kamzik3.snippets.snippetLogging import (
    set_rotating_file_handler,
    set_sys_exception_handler,
    get_console_handler,
    set_rocket_chat_handler,
)
from kamzik3.snippets.snippetsControlLoops import (
    control_asyncore_loop,
    control_device_poller,
    control_port_read_loop,
    control_device_connection_poller,
)
from kamzik3.snippets.snippetsDecorators import expose_method
from kamzik3.snippets.snippetsTimer import CallbackTimer
from kamzik3.snippets.snippetsYaml import YamlDumper, YamlConfigSerializer


class DeviceSession(Device):
    """
    Session is mandatory object, that have to exist for any Server or Client.
    It holds reference to any Device or polling loop.
    It must be first to initialize and last to close.
    Session is global and accessible from kamzik3.session object.
    """

    # Log files locations
    LOG_DEVICE_OUTPUT_FILE = "devices.log"
    LOG_CONSOLE_OUTPUT_FILE = "console.log"
    LOG_ATTRIBUTES_OUTPUT_FILE = "attributes.log"
    LOG_GUI_OUTPUT_FILE = "gui.log"
    LOG_MACRO_OUTPUT_FILE = "macro.log"
    # Default log level
    log_level = logging.INFO
    # Lock protecting config file writes
    config_lock = RLock()

    def __init__(self, device_id=None, config=None):
        kamzik3.session = self
        self.devices: OrderedDict[str, Device] = OrderedDict()
        if config is None:
            self.server = None
            self.publisher = None
        else:
            self.server = config.get("server")
            self.publisher = config.get("publisher")
        self.measurement_groups = {}
        # Polling timer of 1s collecting PC resources
        self.polling_timer = CallbackTimer(1000, self.measure_cpu_ram)
        # Current PID of running session
        self.os_process = psutil.Process(os.getpid())
        # Metadata for config file: (Config file location, config dict)
        self.session_config = None
        super().__init__(device_id, config)
        self.connect()

        if self.server is not None:
            self.server.start()
        if self.publisher is not None:
            self.publisher.start()

    def _init_attributes(self):
        """
        Attributes;
            ATTR_LOG_DIRECTORY: Main log directory
            ATTR_RESOURCE_DIRECTORY: Directory for all resources
            ATTR_CACHE_DIRECTORY: Directory for temporary cache
            ATTR_DEVICES_COUNT: Total number of Devices in Session
            ATTR_ALLOW_CONSOLE_LOG: Switch enabling console logging
            ATTR_ALLOW_GUI_LOG: Switch enabling gui logging
            ATTR_ALLOW_DEVICE_LOG: Switch enabling device logging
            ATTR_ALLOW_ATTRIBUTE_LOG: Switch enabling attribute logging
            ATTR_ALLOW_MACRO_LOG: Switch enabling macro logging
            GROUP_RC / ATTR_ALLOW_RC: Switch enabling use of Rocketchat (RC)
            GROUP_RC / ATTR_MAIN_ROOM: Main roop to use for RC
            GROUP_RC / ATTR_AUTH_TOKEN: Authentication token for RC
            GROUP_RC / ATTR_USER_NAME: RC user name
            GROUP_RC / ATTR_PASSWORD: RC password
            GROUP_RC / ATTR_RC_MACRO_DISCUSSION: RC Discussion ID for Macros
            GROUP_RC / ATTR_HOST: RC Host
            ATTR_LOOPS_RUNNING: Flag indicating loops state
            ATTR_CPU_USAGE: Current CPU usage
            ATTR_MEMORY_USAGE: Current Memory usage
            ATTR_AVAILABLE_MEMORY: Total Available Memory
        """
        super()._init_attributes()
        self.create_attribute(
            ATTR_LOG_DIRECTORY, set_function=self.set_log_directory, readonly=True
        )
        self.create_attribute(
            ATTR_RESOURCE_DIRECTORY,
            set_function=self.set_resource_directory,
            readonly=True,
        )
        self.create_attribute(
            ATTR_CACHE_DIRECTORY, set_function=self.set_cache_directory, readonly=True
        )
        self.create_attribute(
            ATTR_DEVICES_COUNT, default_value=0, default_type=np.uint64, readonly=True
        )
        self.create_attribute(
            ATTR_ALLOW_CONSOLE_LOG, default_value=True, default_type=bool
        )
        self.create_attribute(ATTR_ALLOW_GUI_LOG, default_value=True, default_type=bool)
        self.create_attribute(
            ATTR_ALLOW_DEVICE_LOG, default_value=True, default_type=bool
        )
        self.create_attribute(
            ATTR_ALLOW_ATTRIBUTE_LOG, default_value=True, default_type=bool
        )
        self.create_attribute(
            ATTR_ALLOW_MACRO_LOG, default_value=True, default_type=bool
        )
        self.create_attribute(
            ATTR_ALLOW_RC,
            group=GROUP_RC,
            default_value=False,
            readonly=True,
            default_type=bool,
        )
        self.create_attribute(
            ATTR_MAIN_ROOM,
            group=GROUP_RC,
            default_value=self.device_id.lower(),
            readonly=True,
        )
        self.create_attribute(
            ATTR_AUTH_TOKEN,
            group=GROUP_RC,
            default_value=None,
            readonly=True,
            display=False,
        )
        self.create_attribute(
            ATTR_USER_NAME,
            group=GROUP_RC,
            default_value=None,
            readonly=True,
            display=False,
        )
        self.create_attribute(
            ATTR_PASSWORD,
            group=GROUP_RC,
            default_value=None,
            readonly=True,
            display=False,
        )
        self.create_attribute(
            ATTR_RC_MACRO_DISCUSSION, group=GROUP_RC, default_value=None, readonly=True
        )
        self.create_attribute(
            ATTR_HOST,
            group=GROUP_RC,
            default_value="https://cfel-rocketchat.desy.de",
            readonly=True,
        )
        self.create_attribute(
            ATTR_LOOPS_RUNNING, default_value=False, default_type=bool, readonly=True
        )
        self.create_attribute(ATTR_PROCESS_ID, default_value=os.getpid(), readonly=True)
        self.create_attribute(
            ATTR_CPU_USAGE,
            default_value=0,
            default_type=float,
            readonly=True,
            unit="%",
            decimals=4,
        )
        self.create_attribute(
            ATTR_MEMORY_USAGE,
            default_value=0,
            default_type=float,
            readonly=True,
            decimals=3,
            unit="MB",
            factor=10e-7,
        )
        self.create_attribute(
            ATTR_AVAILABLE_MEMORY,
            default_value=0,
            default_type=float,
            readonly=True,
            unit="MB",
            factor=10e-7,
            decimals=3,
        )
        self.set_raw_value(ATTR_AVAILABLE_MEMORY, psutil.virtual_memory().total)

    def _config_attributes_log(self):
        """
        Config attribute log.
        Device and Attribute must be defined in Session config under logged_attributes key.
        """
        if self.config:
            logger = self.get_device("AttributeLogger")
            for device_id, attribute in self.config.get(
                "logged_attributes", {}
            ).items():
                if isinstance(attribute, list):
                    for sub_attribute in attribute:
                        assert isinstance(logger, AttributeLogger)
                        logger.add_logged_attribute(device_id, sub_attribute)
                else:
                    assert isinstance(logger, AttributeLogger)
                    logger.add_logged_attribute(device_id, attribute)
            logging_interval = self.config.get("logging_interval", False)
            if logging_interval:
                logger.set_value(ATTR_INTERVAL, logging_interval)
            logger.set_attribute((ATTR_LOGGING, VALUE), True)

    def handle_configuration(self):
        """
        Handle Session configuration.
        We want to set Loggers and initiate cache directory here.
        """
        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()

            if self.get_value(ATTR_ALLOW_CONSOLE_LOG):
                self.set_console_log_directory("Console")
            if self.get_value(ATTR_ALLOW_GUI_LOG):
                self.set_gui_log_directory("Gui")
            if self.get_value(ATTR_ALLOW_DEVICE_LOG):
                self.set_device_log_directory("Device")
            if self.get_value(ATTR_ALLOW_ATTRIBUTE_LOG):
                self.set_attribute_log_directory("Attributes")
                self._config_attributes_log()
            if self.get_value(ATTR_ALLOW_MACRO_LOG):
                self.set_macro_log_directory("Macro")
            if self.get_value(ATTR_CACHE_DIRECTORY) is None:
                self.set_value(ATTR_CACHE_DIRECTORY, ".cache")

            # Start polling of CPU and RAM usage
            self.start_polling()
            self.set_status(STATUS_CONFIGURED)
            self.logger.info(f"Device configuration took {time.time() - start_at} sec.")

        _finish_configuration()

    def add_measurement_group(self, measurement_group: MeasurementGroup):
        """
        Add new measurement group into the session.
        Measurement group is used to provide group of Device Attributes, which are interesting.
        This groups then can be used for logging or any other case.
        :param MeasurementGroup measurement_group: new measurement group
        :return:
        """
        assert isinstance(measurement_group, MeasurementGroup)
        self.measurement_groups[measurement_group.group_id] = measurement_group

    # pylint: disable=unused-argument
    def set_session(self, session: "DeviceSession") -> None:
        """
        Even Session has to have a reference to Session.
        In this case it reference to itself.
        :param DeviceSession session: Session object
        :return:
        """
        self.devices[self.device_id] = self
        self.session = self
        self.set_value(ATTR_DEVICES_COUNT, len(self.devices))

    def set_config(self, config_file: str):
        """
        Set config file for a Session.
        It's used for the case of config update and write.
        It set session_config variable as a tuple (config_file, config dict).
        Use set_config in the script that start the session (server.py, client.py).
        :param str config_file: Path to the configuration file
        """
        with self.config_lock:
            # pylint: disable=unspecified-encoding
            with open(config_file, "r") as configFile:
                self.session_config = (
                    config_file,
                    yaml.load(configFile, Loader=YamlConfigSerializer),
                )

    def update_config(
        self, device_id: str, attribute: Union[List, Tuple], value: object
    ):
        """
        When Device Attribute has save_change set to True, we want to update config and save it.
        This can be done only when session_config was set.
        :param str device_id: Device ID
        :param Attribute attribute: Attribute to update
        :param object value: Value of the Attribute
        """
        with self.config_lock:
            if self.session_config is None:
                return
            else:
                config_file, parsed_config = self.session_config
                device_config = parsed_config["devices"][device_id]
                if "config" not in device_config.conf:
                    device_config.conf["config"] = {
                        "attributes": {tuple(attribute): value}
                    }
                elif "attributes" not in device_config.conf["config"]:
                    device_config.conf["config"]["attributes"] = {
                        tuple(attribute): value
                    }
                else:
                    device_config.conf["config"]["attributes"][tuple(attribute)] = value
                # pylint: disable=unspecified-encoding
                with open(config_file, "w") as fp:
                    yaml.dump(parsed_config, fp, Dumper=YamlDumper)

    def command(self, command, callback=None, with_token=False, returning=True) -> int:
        """
        Session is Device, we have to disable command option.
        :param str command: Request to Device
        :param Callable callback: callback after Device replies to Command
        :param bool with_token: token
        :param returning: bool
        :return int: token
        """
        raise DeviceError("Device does not accept any commands.")

    def get_device(self, device_id: str, search_master: bool = True) -> Device:
        """
        Get Device object from the session.

        If master_server key is defined in config, the Session will try to obtain the
        Device from it. If the Device is not found, raise DeviceUnknownError exception.

        :param str device_id: Device ID
        :param bool search_master: Ask master server for Device
        :raises DeviceUnknownError
        :return Device: Device object
        """
        try:
            return self.devices[device_id]
        except KeyError:
            if search_master:
                master_server, master_port = (
                    self.config.get("master_server", False),
                    self.config.get("master_port", False),
                )
                if master_server and master_port:
                    return DeviceClient(master_server, master_port, device_id)
            raise DeviceUnknownError(f"Device {device_id} was not found.")

    def add_device(self, device: Device):
        """
        Add Device into the Session
        Raise DeviceError when Device is already registered.
        :param Device device: Device object
        :raises DeviceError
        """
        assert isinstance(device, Device)

        if device.device_id not in self.devices:
            self.devices[device.device_id] = device
            device.session = self
            self.set_value(ATTR_DEVICES_COUNT, len(self.devices))
        else:
            raise DeviceError(
                f"Device {device.device_id} is already registered within session."
            )

    def remove_device(self, device: Device):
        """
        Remove Device from the Session.
        If Device does not exists, not raise any Exception, this is on purpose :).
        :param Device device: Device object
        """
        assert isinstance(device, Device)
        if device.device_id in self.devices:
            device.session = None
            del self.devices[device.device_id]
            self.set_value(ATTR_DEVICES_COUNT, len(self.devices))

    def get_devices(
        self, class_filter=None, attribute_filter=None, method_filter=None
    ) -> OrderedDict[str, Device]:
        """
        Filter devices in current session.

        :param list class_filter: list of classes
        :param attribute_filter: attribute
        :param method_filter: method name
        :return list: list of filtered devices
        """
        filtered_devices = self.devices.copy()
        # Filter over device class
        if class_filter is not None:
            for device_id, device in filtered_devices.copy().items():
                if class_filter not in device.qualified_name:
                    del filtered_devices[device_id]
        # Filter over device attributes
        if attribute_filter is not None:
            for device_id, device in filtered_devices.copy().items():
                if device.get_attribute(attribute_filter) is None:
                    del filtered_devices[device_id]
        # Filter over device methods
        if method_filter is not None:
            for device_id, device in filtered_devices.copy().items():
                filtered_out_methods = filter(
                    lambda val: val[0] == method_filter, device.exposed_methods
                )
                try:
                    next(filtered_out_methods)
                except StopIteration:
                    del filtered_devices[device_id]

        return filtered_devices

    def change_device_id(self, device_id, new_device_id):
        """
        Change ID of Device in Session
        :param str device_id: old Device ID
        :param str new_device_id: new Device ID
        """
        device = self.get_device(device_id)
        device.device_id = new_device_id
        self.devices[new_device_id] = self.devices.pop(device_id)

    def set_log_directory(self, value: str):
        """
        Set main log Directory.
        Try to create it, if it does not exist.
        :param str value: Directory path
        """
        self.logger.info(f"Setting log directory to: {value}")
        if not os.path.exists(value):
            self.logger.info(f"Directory {value} does not exists, trying to create it.")
            os.makedirs(value)

    def set_resource_directory(self, value: str):
        """
        Set main resource Directory.
        Try to create it, if it does not exist.
        :param str value: Resource path
        """
        self.logger.info(f"Setting resource directory to: {value}")
        if not os.path.exists(value):
            self.logger.info(f"Directory {value} does not exists, trying to create it.")
            os.makedirs(value)

    def set_cache_directory(self, value: str):
        """
        Set main cache Directory.
        Try to create it, if it does not exist.
        :param str value: Cache path
        """
        self.logger.info("Setting cache directory to: {}".format(value))
        if not os.path.exists(value):
            self.logger.info(f"Directory {value} does not exists, trying to create it.")
            os.makedirs(value)

    def set_console_log_directory(self, value: str):
        """
        Set console log Directory.
        Try to create it, if it does not exist.
        :param str value: Console log Directory path
        :raises DeviceError
        """
        log_directory = self.get_value(ATTR_LOG_DIRECTORY)
        if log_directory is None:
            raise DeviceError(
                "Cannot set console log directory. Attribute 'Log directory' is not set."
            )
        log_directory = os.path.join(log_directory, value)
        self.logger.info(f"Setting console log directory to: {log_directory}")
        if not os.path.exists(log_directory):
            self.logger.info(
                f"Directory {log_directory} does not exists, trying to create it."
            )
            os.makedirs(log_directory)

        handler = get_console_handler()
        logger = logging.getLogger("Console")
        set_rotating_file_handler(
            logger, os.path.join(log_directory, self.LOG_CONSOLE_OUTPUT_FILE)
        )
        set_sys_exception_handler(logger)
        logger.setLevel(self.log_level)
        logger.addHandler(handler)

    def set_gui_log_directory(self, value: str):
        """
        Set gui log Directory.
        Try to create it, if it does not exist.
        :param str value: Gui log Directory path
        :raises DeviceError
        """
        log_directory = self.get_value(ATTR_LOG_DIRECTORY)
        if log_directory is None:
            raise DeviceError(
                "Cannot set gui log directory. Attribute 'Log directory' is not set."
            )
        log_directory = os.path.join(log_directory, value)

        self.logger.info(f"Setting gui log directory to: {log_directory}")
        if not os.path.exists(log_directory):
            self.logger.info(
                f"Directory {log_directory} does not exists, trying to create it."
            )
            os.makedirs(log_directory)

        handler = get_console_handler()
        logger = logging.getLogger("Gui")
        set_rotating_file_handler(
            logger, os.path.join(log_directory, self.LOG_GUI_OUTPUT_FILE)
        )
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

    def set_attribute_log_directory(self, value: str):
        """
        Set Attribute log Directory.
        Try to create it, if it does not exist.
        :param str value: Attribute log Directory path
        """
        log_directory = self.get_value(ATTR_LOG_DIRECTORY)
        if log_directory is None:
            raise DeviceError(
                "Cannot set Attribute log directory. Attribute 'Log directory' is not set."
            )
        log_directory = os.path.join(log_directory, value)

        self.logger.info("Setting device log directory to: {}".format(log_directory))
        if not os.path.exists(log_directory):
            self.logger.info(
                "Directory {} does not exists, trying to create it.".format(
                    log_directory
                )
            )
            os.makedirs(log_directory)

        logger = AttributeLogger(
            os.path.join(log_directory, self.LOG_ATTRIBUTES_OUTPUT_FILE),
            device_id="AttributeLogger",
        )
        self.attributes.update({"Attribute logger": logger.attributes})

    def set_device_log_directory(self, value):
        """
        Set device log Directory.
        Try to create it, if it does not exist.
        :param str value: Device log Directory path
        :raises DeviceError
        """
        log_directory = self.get_value(ATTR_LOG_DIRECTORY)
        if log_directory is None:
            raise DeviceError(
                "Cannot set device log directory. Attribute 'Log directory' is not set."
            )
        log_directory = os.path.join(log_directory, value)

        self.logger.info("Setting device log directory to: {}".format(log_directory))
        if not os.path.exists(log_directory):
            self.logger.info(
                "Directory {} does not exists, trying to create it.".format(
                    log_directory
                )
            )
            os.makedirs(log_directory)

        handler = get_console_handler()
        logger = logging.getLogger("Device")
        set_rotating_file_handler(
            logger, os.path.join(log_directory, self.LOG_DEVICE_OUTPUT_FILE)
        )
        logger.setLevel(self.log_level)
        logger.addHandler(handler)

    def set_macro_log_directory(self, value):
        """
        Set Macro log Directory.
        Try to create it, if it does not exist.
        :param str value: Macro log Directory path
        :raises DeviceError
        """
        log_directory = self.get_value(ATTR_LOG_DIRECTORY)
        if log_directory is None:
            raise DeviceError(
                "Cannot set macro log directory. Attribute 'Log directory' is not set."
            )
        log_directory = os.path.join(log_directory, value)

        self.logger.info(f"Setting gui log directory to: {log_directory}")
        if not os.path.exists(log_directory):
            self.logger.info(
                f"Directory {log_directory} does not exists, trying to create it."
            )
            os.makedirs(log_directory)

        handler = get_console_handler()
        logger = logging.getLogger("Macro")
        set_rotating_file_handler(
            logger, os.path.join(log_directory, self.LOG_MACRO_OUTPUT_FILE)
        )
        if self.get_value([GROUP_RC, ATTR_ALLOW_RC]):
            discussion_name = self.get_value([GROUP_RC, ATTR_RC_MACRO_DISCUSSION])
            if discussion_name is None:
                discussion_name = "{}-{}".format(self.device_id.lower(), "macro-log")
                self.set_value([GROUP_RC, ATTR_RC_MACRO_DISCUSSION], discussion_name)
            user_credentials, auth_token = self._get_rc_auth()
            set_rocket_chat_handler(
                logger,
                level=logging.MACRO_STATE,
                user_credentials=user_credentials,
                auth_token=auth_token,
                main_room=self.device_id.lower(),
                discussion=discussion_name,
            )
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

    def _get_rc_auth(self):
        """
        Helper method to get RocketChat credentials.
        :return tuple: ((RocketChat user, RocketChat password), RocketChat auth token)
        """
        rc_user = self.get_value([GROUP_RC, ATTR_USER_NAME])
        rc_pass = self.get_value([GROUP_RC, ATTR_PASSWORD])
        rc_auth_token = self.get_value([GROUP_RC, ATTR_AUTH_TOKEN])
        return (rc_user, rc_pass), rc_auth_token

    def start_control_loops(self):
        if not self.get_value(ATTR_LOOPS_RUNNING):
            self.start_asyncore_loop()
            self.start_device_connection_poller()
            self.start_device_poller_loop()
            self.start_port_read_loop()
            self.set_value(ATTR_LOOPS_RUNNING, True)

    def stop_control_loops(self):
        if self.get_value(ATTR_LOOPS_RUNNING):
            self.stop_asyncore_loop()
            self.stop_port_read_loop()
            self.stop_device_poller_loop()
            self.stop_device_connection_poller()
            self.set_value(ATTR_LOOPS_RUNNING, False)

        self.logger.info("Closing all control loops")
        # Here we try to join all control loops giving them 1 second timeout
        control_asyncore_loop.join(1)
        control_device_poller.join(1)
        control_port_read_loop.join(1)
        control_device_connection_poller.join(1)

        self.logger.info("Control loops closed")

    def stop(self):
        """Stop and disconnect all devices in Session."""
        self.stop_polling()
        if self.get_value(ATTR_ALLOW_ATTRIBUTE_LOG):
            logger = self.get_device("AttributeLogger", search_master=False)
            if logger is not None:
                assert isinstance(logger, AttributeLogger)
                logger.stop()

        if self.server is not None:
            self.server.stop()

        if self.publisher is not None:
            self.publisher.stop()

        self.session = None
        del self.devices[self.device_id]

        for device in list(self.devices.values()):
            device.disconnect()

        if self.get_value(ATTR_LOOPS_RUNNING):
            self.stop_control_loops()
            self.set_value(ATTR_LOOPS_RUNNING, False)

    @staticmethod
    def start_asyncore_loop():
        control_asyncore_loop.start()

    @staticmethod
    def stop_asyncore_loop():
        control_asyncore_loop.stop()

    @staticmethod
    def start_device_poller_loop():
        control_device_poller.start()

    @staticmethod
    def stop_device_poller_loop():
        control_device_poller.stop()

    @staticmethod
    def start_port_read_loop():
        control_port_read_loop.start()

    @staticmethod
    def stop_port_read_loop():
        control_port_read_loop.stop()

    @staticmethod
    def start_device_connection_poller():
        control_device_connection_poller.start()

    @staticmethod
    def stop_device_connection_poller():
        control_device_connection_poller.stop()

    def set_high_process_priority(self):
        """
        Set high process affinity.

        In Windows use win32process.REALTIME_PRIORITY_CLASS, for Linux change nice to -20.
        """
        if psutil.WINDOWS:
            try:
                import win32api
                import win32process
                import win32con
            except ImportError:
                self.logger.error("Package pypiwin32 is not installed")
            pid = win32api.GetCurrentProcessId()
            handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
            win32process.SetPriorityClass(handle, win32process.REALTIME_PRIORITY_CLASS)
            # win32process.SetThreadPriority(win32api.GetCurrentThread(), win32process.THREAD_PRIORITY_TIME_CRITICAL)
        else:
            try:
                process = psutil.Process(os.getpid())
                process.nice(-20)
            except psutil.AccessDenied:
                self.logger.error("Could not raise process priority")

    @expose_method()
    def clear_cache_folder(self):
        """Clear all files from current '.cache' folder."""
        folder = self.get_value(ATTR_CACHE_DIRECTORY)
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                self.logger.error(f"Failed to delete {file_path}: {e}")

    def measure_cpu_ram(self):
        self.set_raw_value(ATTR_CPU_USAGE, self.os_process.cpu_percent())
        self.set_raw_value(ATTR_MEMORY_USAGE, self.os_process.memory_info().rss)

    def start_polling(self):
        self.polling_timer.start()

    def stop_polling(self):
        self.polling_timer.stop()


def server_process(conf: str, stop_event: EventType) -> Process:
    """
    Here comes a short description of server_process.

    For the reason of having multiple Processes handling multiple devices, we can start
    each server in it's own Process. This function will start Server in new Process
    and return that Process. If stop event is set, then stop session.

    :param conf: path to the config file
    :param stop_event: event
    :return: Process
    """

    def _process(conf, stop_event):
        # I have no idea why this is reimported, but maybe it makes sense?
        # pylint: disable=redefined-outer-name,reimported
        import kamzik3

        # pylint: disable=redefined-outer-name
        import yaml
        from time import sleep

        # pylint: disable=unspecified-encoding
        with open(conf, "r") as configFile:
            yaml.load(configFile, Loader=yaml.Loader)

        # Start control loop for devices specified in configuration file
        kamzik3.session.set_config(conf)
        kamzik3.session.start_control_loops()
        while not stop_event.is_set():
            try:
                sleep(1)
            except KeyboardInterrupt:
                break
        kamzik3.session.stop()

    return Process(target=_process, args=(conf, stop_event))
