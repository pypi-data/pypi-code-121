import logging
import time
from collections import deque
from copy import copy
from math import inf
from threading import Thread
from typing import Any, Callable, Dict, Tuple, List, Optional, Union, TYPE_CHECKING

import numpy as np
import oyaml as yaml
from pint import Quantity, UndefinedUnitError, DimensionalityError
import serial
import warnings

import kamzik3
from kamzik3 import (
    CommandFormatException,
    DeviceError,
    DeviceUnitError,
    units,
    WriteException,
)
from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute, SetFunction
from kamzik3.devices.subject import Subject
from kamzik3.snippets.snippetDataAccess import get_from_dict, fullname, is_equal
from kamzik3.snippets.snippetsControlLoops import (
    control_device_poller,
    control_device_connection_poller,
)
from kamzik3.snippets.snippetsDecorators import expose_method
from kamzik3.snippets.snippetsGenerators import device_id_generator, token_generator
from kamzik3.snippets.snippetsUnits import convert_to_unit
from kamzik3.snippets.snippetsYaml import YamlSerializable

if TYPE_CHECKING:
    from kamzik3.devices.deviceSession import DeviceSession


class Device(Subject, YamlSerializable):
    """
    Device is a main parent class for any Device within Kamzik3.
    It provides methods to work with Attributes, Connection and Commands handling.
    If You inherit from Device, You must reimplement handle_configuration method.

    Connection is done in sequence:
        - connect()
        - handle_connect_event()
            - handle_connect()
            - handle_configuration_event()
                - handle_configuration()

    Connection error handling:
        - if connect() => error state
           - disconnect() if critical error
           - close(), reconnect() if not critical error
        - if connect() => connection timeout
            - handle_connection_error(), close()
        - if Device.connected and response timeout()
            - handle_response_error(), close_connection()

    Disconnection is done in sequence:
        - disconnect()
            - close() if not Device.connected
            - close_connection() if connected
                - close()

    General config setup in Yaml example:

    # List of devices
    devices:
        # Device_id_within_yml: Kamzik3 absolute path to Device class
        MyMotorX: !Device:kamzik3.devices.dummy.dummyMotor.DummyMotor
            device_id: MyMotorX
            Motor1_axis_0: &x !Device:kamzik3.devices.dummy.dummyMotor.DummyMotorChannel
            channel: 0
            config:
                attributes:
                    !!python/tuple [Velocity, Value]: 1mm/s
                    !!python/tuple [Position, Tolerance]: [100nm, 100nm]
        # Device 2 definition
        # Device 3 definition
        # ...
    """

    id_generator = device_id_generator()  # Device id generator
    connection_timeout = 4000  # in ms
    response_timeout = 4000  # in ms
    session: Optional["DeviceSession"] = None  # Holds current Session object
    push_commands_max = inf  # Max commands, that Device can handle at once
    push_buffer_size = 2**16  # Max number of characters per request
    command_encoding: Optional[str] = "utf8"  # Default command encoding

    def __init__(self, device_id=None, config=None):
        self.connecting_time = 0  # Counting time of connection
        self.request_timestamp = 0  # Timestamp of last request
        self.response_timestamp = 0  # Timestamp of last Device response to the request
        # Connection flags
        self.connected = False
        self.connecting = False
        self.closing = False
        self.closed = False
        # Connection error flags
        self.connection_error = False
        self.response_error = False
        self.latency_buffer = deque(
            maxlen=20
        )  # response - request time, calculate avg response latency
        self.init_time = time.time()  # Initiation time
        self.commands_buffer = deque()  # Holds requested commands
        Subject.__init__(self)

        self.device_id = device_id
        if device_id is None:
            # If no device_id was not specify, generate one
            self.device_id = next(Device.id_generator)
        self.config = config
        if self.config is None:
            # Config must be dictionary
            self.config = {}
        self.token_generator = token_generator()
        self.device_poller = control_device_poller  # Attach poller loop
        self.device_connection_poller = (
            control_device_connection_poller  # Attach connection loop
        )
        self.qualified_name = fullname(self)  # Get absolute path to the Device class
        if not hasattr(self, "logger"):
            # Attach Device log, if it does not exists
            self.logger = logging.getLogger("Device.{}".format(self.device_id))
        if "push_commands_max" in self.config:
            # Check and set push_commands_max from Config file
            self.push_commands_max = self.config["push_commands_max"]
        if "push_buffer_size" in self.config:
            # Check and set push_buffer_size from Config file
            self.push_buffer_size = self.config.get("push_buffer_size")
        # Filter for Attributes and Methods, which can be used within Macro
        # By Default use all attributes and methods
        self.macro_steps = {
            MACRO_SET_ATTRIBUTE_STEP: ["*"],
            MACRO_EXECUTE_METHOD_STEP: ["*"],
        }
        self.exposed_methods = []  # List of exposed methods
        self._expose_methods_to_clients()
        if not hasattr(self, "attributes"):
            # Check if attributes are already defined
            self.attributes = {}
            self.attributes_sharing_map = {}
            self.attribute_attach_map = {}
            self._init_attributes()

        if kamzik3.session is not None:
            # Check if device id is already registered in session
            # and remove it if it's not our current Device
            if (
                self.device_id in kamzik3.session.devices
                and self != kamzik3.session.devices[self.device_id]
            ):
                kamzik3.session.devices[self.device_id].close()
                kamzik3.session.devices[self.device_id] = None
                del kamzik3.session.devices[self.device_id]

            if self.device_id not in kamzik3.session.devices:
                # Check if device is not registered in session and set current session
                self.set_session(kamzik3.session)

    def __getitem__(self, key):
        """
        To get Device's Attribute we can use directly dict key notation.
        For examples self[(POSITION, VALUE)] gets POSITION Value.

        :param key: Get Attribute from Device.attributes dict
        :return: Attribute or Value
        """
        return self.attributes[key]

    def __setitem__(self, key, value):
        """
        To set Device's Attribute we can use directly dict key notation.
        For examples self[(POSITION, VALUE)] = 50nm

        Be careful not to use self[POSITION] = 50m, this would set Attribute to just
        50nm.

        :param key: Set Attribute Value
        :param value: mixed, based Attribute's TYPE
        """
        self.attributes[key] = value

    def _init_attributes(self):
        """
        Initiate Device's attributes.

        To call this method is mandatory.
        Overload this method for any other derived Device.
        Attributes;
            ATTR_ID: Unique Device ID
            ATTR_STATUS: Current Device status can be user defined, but it's overwritten
            by connection methods
            ATTR_DESCRIPTION: Attribute's description, it's displayed in GUI on
            MouseHover
            ATTR_ENABLED: Meta flag for GUI to Enable / Disable edit of Value
            ATTR_LATENCY: Average Device response time to request
            ATTR_BUFFERED_COMMANDS: Number of buffered commands. Higher number can
            indicates ERROR.
            ATTR_HANGING_COMMANDS: Number of commands sent to Device and waiting
            response. Higher number can indicates ERROR.
            ATTR_LAST_ERROR: Last occurred error
        """

        def set_status(key, value):
            """
            When status has changed, notify all Observers
            :param key: str
            :param value: str
            """
            if key == VALUE:
                self.notify(ATTR_STATUS, value)

        self.create_attribute(
            ATTR_ID,
            default_value=self.device_id,
            readonly=True,
            description="Unique device ID",
        )
        self.create_attribute(
            ATTR_STATUS,
            default_value=STATUS_DISCONNECTED,
            readonly=True,
            description="Current device status",
            min_broadcast_timeout=0,
        ).attach_callback(set_status)
        self.create_attribute(
            ATTR_DESCRIPTION, readonly=True, description="Device description"
        )
        self.create_attribute(
            ATTR_ENABLED,
            default_value=True,
            default_type=bool,
            description="Allow any external changes to device",
        )
        self.create_attribute(
            ATTR_LATENCY,
            default_value=0,
            default_type=np.uint16,
            description="Latency between sending command and receiving an answer",
            min_value=0,
            max_value=9999,
            unit="ms",
            readonly=True,
        )
        self.create_attribute(
            ATTR_BUFFERED_COMMANDS,
            default_value=0,
            default_type=np.uint32,
            description="Amount of commands waiting to be executed",
            min_value=0,
            readonly=True,
        )
        self.create_attribute(
            ATTR_HANGING_COMMANDS,
            default_value=0,
            default_type=np.uint32,
            description="Amount of commands waiting to be answered from device",
            min_value=0,
            readonly=True,
        )
        self.create_attribute(
            ATTR_LAST_ERROR,
            readonly=True,
            description="Last device error exception",
            min_broadcast_timeout=0,
        )

    def create_attribute(self, name, group=None, **kwargs) -> Attribute:
        """
        Use this function to create new attribute.
        !!! It's mandatory to use ONLY this method to create new Device's Attributes !!!
        :param str name: Name of the Attributes
        :param str group: Group of the Attribute
        :param mixed kwargs: Defined key:value pairs of the Attribute
        :return: Attribute
        """
        attribute_path = name
        if group is not None:
            attribute_path = "{}.{}".format(group, attribute_path)
        attribute_id = "{}.{}.{}".format(
            self.device_id, TOKEN_ATTRIBUTE, attribute_path
        )
        attribute = Attribute(attribute_id, **kwargs)

        if group is None:
            self.attributes[name] = attribute
        else:
            if group not in self.attributes:
                self.attributes[group] = {}
            self.attributes[group][name] = attribute
        if kamzik3.session is not None and kamzik3.session.publisher is not None:
            header = "{}.{}".format(attribute.attribute_id, TOKEN_ATTRIBUTE_REPLACE)
            kamzik3.session.publisher.push_message(header, attribute)
        return attribute

    def add_attribute(
        self, name: str, attribute: Attribute, group: Optional[str] = None
    ) -> Attribute:
        """
        Use this function to add existing attribute to Device.

        This is useful if Attribute from other Device has to be visible in this Device
        as well.

        Use only create_attribute when you need to add new Attribute to this Device.
        Set group parameter if You want attribute be in specific group.

        :param name: str
        :param attribute: Attribute
        :param group: str
        :return: Attribute
        """
        attribute_list = [name]
        if group is None:
            self.attributes[name] = attribute
        else:
            attribute_list.insert(0, group)
            if group not in self.attributes:
                self.attributes[group] = {}
            self.attributes[group][name] = attribute

        attribute_exists = attribute.attribute_id in self.attributes_sharing_map
        if attribute_exists:
            self.attributes_sharing_map[attribute.attribute_id].append(attribute_list)
        else:
            self.attributes_sharing_map[attribute.attribute_id] = [attribute_list]
        if (
            attribute_exists
            and kamzik3.session is not None
            and kamzik3.session.publisher is not None
        ):
            header = "{}.{}".format(attribute.attribute_id, TOKEN_ATTRIBUTE_REPLACE)
            kamzik3.session.publisher.push_message(header, attribute)
        if attribute.attribute_id is None:
            attribute_path = name
            if group is not None:
                attribute_path = "{}.{}".format(group, attribute_path)
            attribute.attribute_id = "{}.{}.{}".format(
                self.device_id, TOKEN_ATTRIBUTE, attribute_path
            )
        return attribute

    def delete_attribute(self, name: str, group: Optional[str] = None) -> None:
        """
        Delete specific attribute.

        :param name: Name of the Attribute
        :param group: Optional group of the Attribute
        """
        attribute_path = name
        if group is not None:
            attribute_path = "{}.{}".format(group, attribute_path)
        attribute_id = "{}.{}.{}".format(
            self.device_id, TOKEN_ATTRIBUTE, attribute_path
        )
        if group is not None:
            del self.attributes[group][name]
        else:
            del self.attributes[name]
        if kamzik3.session is not None and kamzik3.session.publisher is not None:
            header = "{}.{}".format(attribute_id, TOKEN_ATTRIBUTE_DELETE)
            kamzik3.session.publisher.push_message(header, attribute_path)

    def delete_attribute_group(self, group: str) -> None:
        """
        Delete all attributes including group.

        :param str group: Group of the Attribute
        """
        attribute_path = group
        attribute_id = "{}.{}.{}".format(
            self.device_id, TOKEN_ATTRIBUTE, attribute_path
        )
        del self.attributes[group]
        if kamzik3.session is not None and kamzik3.session.publisher is not None:
            header = "{}.{}".format(attribute_id, TOKEN_ATTRIBUTE_GROUP_DELETE)
            kamzik3.session.publisher.push_message(header, attribute_path)

    def share_group(
        self,
        source_device,
        source_group: Optional[str],
        target_group: str,
        attribute_name_mask: Optional[Dict[str, str]] = None,
    ):
        """
        Share all attributes in group.

        Filter by attribute_name_mask from source_device.

        :param source_device: Source Device object
        :param source_group: Name of the group to share
        :param str target_group: Target group on this Device
        :param attribute_name_mask: Use this, if You need to rename Attribute
        """
        if attribute_name_mask is None:
            attribute_name_mask = {}
        if source_group is not None:
            from_group = source_device.attributes[source_group]
        else:
            from_group = source_device.attributes

        for attribute_name, attribute in from_group.items():
            self.add_attribute(
                attribute_name_mask.get(attribute_name, attribute_name),
                attribute,
                target_group,
            )

    def share_exposed_method(
        self,
        source_device,
        source_method,
        shared_method_name=None,
        shared_method_attributes=None,
    ):
        """
        Share exposed method with source_device.

        This is handy method when you share attributes of other device and you want
        to also expose it's methods. Each new method will go under new name
        source_device.id_source_method.name. If You define shared_method_attributes
        they will overwrite default ones.

        :param Device source_device: Source Device object
        :param source_method: Name of source exposed method
        :param str shared_method_name: optional new name of the method
        :param shared_method_attributes: optional Dictionary of method attributes
        """
        for method_name, method_parameters in source_device.exposed_methods:
            if method_name == source_method:
                if shared_method_name is None:
                    shared_method_name = "{}_{}".format(
                        source_device.device_id, method_name
                    )
                if shared_method_attributes is None:
                    shared_method_attributes = method_parameters
                method = copy(getattr(source_device, method_name))
                # Check if method is meant to be exposed and remove
                # exposed_parameters to prevent double exposing
                if hasattr(method, "exposed_parameters"):
                    del method.__dict__["exposed_parameters"]
                setattr(self, shared_method_name, method)
                self.exposed_methods.append(
                    (shared_method_name, shared_method_attributes)
                )

    def set_session(self, session):
        """
        Set Device's Session.

        :param Session session: Global Session object
        """
        self.session = session
        session.add_device(self)

    def attach_attribute_callback(
        self,
        attribute: Union[List, Tuple, str],
        callback: Callable,
        max_update_rate: Optional[int] = None,
        key_filter: Optional[str] = None,
    ) -> None:
        """
        Attach callback to Attribute.
        By default all changes of every Attribute's key calls callback.
        It's good habit to set key_filter.
        Attach multiple callbacks for different filter.

        If max_update_rate is specified that callback will be called only after
        specified timeout.

        :param attribute: Attribute
        :param callback: callable function or method
        :param max_update_rate: millisecond(s)
        :param key_filter: Callback's filter ie. VALUE, TYPE, ...
        """
        assert callable(callback)
        try:
            attribute_object = self.get_attribute(attribute)
            if attribute_object is None:
                raise Exception(
                    f"couldn't find attribute {attribute}, cannot attach callback"
                )
            attribute_object.attach_callback(callback, max_update_rate, key_filter)

            try:
                self.attribute_attach_map[attribute_object.attribute_id].append(
                    (attribute, callback)
                )
            except KeyError:
                self.attribute_attach_map.update(
                    {attribute_object.attribute_id: [(attribute, callback)]}
                )

            if key_filter is not None:
                callback(attribute_object[key_filter])
            else:
                callback(VALUE, attribute_object[VALUE])
        except (KeyError, AttributeError):
            self.logger.exception("Attribute {} is not defined".format(attribute))

    def detach_attribute_callback(
        self, attribute: Union[List, Tuple, str], callback: Callable
    ) -> None:
        """
        Detach callback.

        :param attribute: Attribute
        :param callback: callable function or method
        """
        assert callable(callback)
        try:
            attribute_object = self.get_attribute(attribute)
            if attribute_object is None:
                raise Exception(
                    f"cannot find attribute {attribute}, cannot detach callback"
                )
            attribute_object.detach_callback(callback)

            try:
                if (attribute, callback) in self.attribute_attach_map[
                    attribute_object.attribute_id
                ]:
                    self.attribute_attach_map[attribute_object.attribute_id].remove(
                        (attribute, callback)
                    )
            except KeyError:
                pass  # Callback does not exists

        except (KeyError, AttributeError):
            if self.logger is not None:
                self.logger.exception("Attribute {} is not defined".format(attribute))

    def _get(self, attribute: Union[str, List, Tuple]) -> Any:
        """
        Private method to obtain attribute from the attributes dict.

        Use this function when You want to get attribute by tuple or list key.
        Example: Device._get((ATTR_STATUS, VALUE))
        Otherwise use faster method Device[ATTR_STATUS][VALUE]

        :param attribute: list
        :return: mixed
        """
        try:
            return get_from_dict(self.attributes, attribute)
        except KeyError:
            return None

    def get_attribute(self, attribute: Union[List, Tuple, str]) -> Any:
        """
        Get Attribute value.

        :param attribute: Attribute
        :return: the attribute if it exists
        """
        try:
            return self._get(Attribute.list_attribute(attribute))
        except KeyError:
            return None

    def get_value(self, attribute: Union[List, Tuple, str], key: str = VALUE) -> Any:
        """
        Get Attribute[key] value.

        :param attribute: Attribute
        :param key: optional key
        :return: mixed
        """
        try:
            return self.get_attribute(attribute)[key]
        except (KeyError, TypeError):
            return None

    def get_raw_value(
        self, attribute: Union[List, Tuple, str], key: str = VALUE
    ) -> Any:
        """
        Get attribute[key] value without offset or factor.

        Use returned value to feed into real hardware.

        :param attribute: Attribute
        :param key: optional key
        :return: mixed
        """
        try:
            attribute_object: Optional[Attribute] = self.get_attribute(attribute)
            if attribute_object is None:
                return None
            return attribute_object.remove_offset_factor(attribute_object[key])
        except (KeyError, TypeError):
            return None

    def _set(
        self,
        attribute: Union[List, Tuple],
        value: Any,
        callback: Optional[Callable] = None,
    ) -> int:
        """
        This sets Device attribute.

        Use this function when You want to set attribute by tuple or list key.
        Example: Device.set((ATTR_STATUS, VALUE), STATUS_IDLE)
        Attribute value is pushed into server if Device is connected listed on one.
        To reduce the amount of pushed attributes we check if value is different from
        the previous one.

        :param attribute: list
        :param value: Value of attribute
        :return: Set token
        """
        attribute_object: Attribute = get_from_dict(self.attributes, attribute[:-1])
        if not attribute_object.allow_broadcast():
            allow_broadcast = False
        elif attribute[-1] == VALUE and attribute_object.with_set_function:
            allow_broadcast = attribute_object.set_value_when_set_function
        else:
            allow_broadcast = True
        if allow_broadcast:
            attribute_object.last_broadcast_time = time.perf_counter_ns()

        current_value = attribute_object[attribute[-1]]
        attribute_object[attribute[-1]] = value

        set_token = attribute_object.read_and_reset_token()
        if not set_token and callable(callback):
            callback(attribute, value)

        if allow_broadcast and kamzik3.session is not None:
            value = attribute_object[attribute[-1]]
            if not is_equal(current_value, value):
                if self.session and attribute_object[SAVE_CHANGE]:
                    self.session.update_config(self.device_id, attribute, value)
                    self.config["attributes"][tuple(attribute)] = value
                if kamzik3.session.publisher is not None:
                    header = "{}.{}".format(
                        attribute_object.attribute_id, attribute[-1]
                    )
                    kamzik3.session.publisher.push_message(header, value)

        return set_token

    def set_attribute(
        self,
        attribute: Union[List, Tuple, str],
        value: Any,
        callback: Optional[Callable] = None,
    ) -> int:
        """
        This sets Device attribute.

        Re-implement it for client or any special use.

        :param attribute: tuple, list, str
        :param value: mixed
        :param callback: callable
        :return: token
        """
        list_attribute = Attribute.list_attribute(attribute)
        if list_attribute[-1] == VALUE:
            return self.set_value(list_attribute[:-1], value, callback)
        else:
            return self._set(list_attribute, value, callback)

    def set_value(
        self,
        attribute: Union[List, Tuple, str],
        value: Any,
        callback: Optional[Callable] = None,
        key: Any = VALUE,
    ) -> int:
        """
        Set attribute value.

        :param attribute: tuple, list, str
        :param value: mixed
        :param callback: callable
        :param key: Attribute's key
        :return: token
        """
        attribute_list = Attribute.list_attribute(attribute)
        attribute_object = self.get_attribute(attribute_list)
        with SetFunction(attribute_object, callback):
            return self._set(attribute_list + [key], value, callback)

    def set_offsetted_value(
        self,
        attribute: Union[List, Tuple, str],
        value: Any,
        callback: Optional[Callable] = None,
        key: Any = VALUE,
    ) -> None:
        """
        Apply the offset and factor to the attribute value obtained from Device, before
        the value is stored in the key VALUE.

        :param attribute: tuple, list, str
        :param value: mixed
        :param callback: callable
        :param key: Attribute's key
        """
        list_attribute = Attribute.list_attribute(attribute)
        attribute_object = self.get_attribute(list_attribute)
        if attribute_object is None:
            raise Exception(
                f"couldn't get attribute {attribute}, couldn't set offsetted value"
            )
        value = attribute_object.apply_offset_factor(value)
        self._set(list_attribute + [key], value, callback)

    def set_raw_value(
        self,
        attribute: Union[List, Tuple, str],
        value: Any,
        callback: Optional[Callable] = None,
        key: Any = VALUE,
    ) -> None:
        """
        Set attribute value obtained from Device.
        You want to call this to set Value obtained directly from Device.
        Apply offset and factor before value is stored in VALUE key.

        :param attribute: tuple, list, str
        :param value: mixed
        :param callback: callable
        :param key: Attribute's key
        """
        warnings.warn(
            "set_raw_value is deprecated, use set_offsetted_value instead",
            DeprecationWarning,
        )
        self.set_offsetted_value(
            attribute=attribute,
            value=value,
            callback=callback,
            key=key,
        )

    # pylint: disable=unused-argument
    def connect(self, *args):
        """
        Connect to Device via interface.
        This method should be re-implemented when using ETH or RS232, ...

        :param mixed args: connect attributes
        """
        try:
            self.connecting = True
            self.connected = False
            self.device_connection_poller.add_connecting_device(self)
            self.handle_connect_event()
        except DeviceError:
            self.logger.exception("Connection exception")

    def handle_readout_callback(
        self,
        callback: Optional[Callable],
        attribute: Union[List, Tuple, str],
        output: Any,
    ) -> None:
        """
        This method handle readout from Device.
        It's called when Device replies to Request.
        This method should be re-implemented when using ETH or RS232, ...

        :param callback: callable
        :param attribute: tuple, list, str
        :param output: Reply from Device
        """
        if callback is None:
            return
        else:
            assert callable(callback)
            callback(attribute, output)

    def handle_connect_event(self):
        """
        Handle connect event.
        It's called when Device is successfully connected.
        This method should be re-implemented when using ETH or RS232, ...
        """
        try:
            self.handle_connect()
            self.connected = True
            self.connecting = False
            self.handle_configuration_event()
        except DeviceError:
            self.logger.exception("Error during connection")

    def handle_connect(self):
        """
        Handle connection.
        Measure and write connection time and set request and response timestamps.
        When re-implementing, call this method at the beginning.
        """
        self.set_status(STATUS_CONNECTED)
        self.logger.info(
            "Device connection took {} sec.".format(time.time() - self.init_time)
        )
        self.request_timestamp = self.response_timestamp = time.time()

    def handle_configuration_event(self):
        """
        Handle configuration event.
        Device is connected, now we need to configure it.
        """
        try:
            self.set_status(STATUS_CONFIGURING)
            self.handle_configuration()
        except DeviceError:
            self.logger.exception("Error during configuration")

    def handle_configuration(self):
        """
        This is placeholder method for handle configuration.
        This method must be re-implemented as every Device has special configuration.
        Example of implementation:

            start_at = time.time()

            def _finish_configuration(*_, **__):
                self._config_commands()
                self._config_attributes()
                self.start_polling()
                self.set_status(STATUS_CONFIGURED)
                self.logger.info(
                    u"Device configuration took {} sec.".format(time.time() - start_at)
                )

            _finish_configuration()
        """
        raise NotImplementedError("Must be implemented in subclass")

    def handle_connection_error(self, message=None):
        """
        Method to handle Device's connection error.

        :param str message: cause of connection error
        """
        self.logger.error(message)
        self.connection_error = True
        self.close()

    def handle_response_error(self, message=None):
        """
        Method to handle Device's response error.

        :param str message: cause of response error
        """
        self.logger.error(message)
        self.response_error = True
        self.close_connection()

    def handle_command_error(self, readout_command, readout_output):
        """
        Method to handle Device's command error.

        :param str readout_command: original command
        :param str readout_output: error response from device
        """
        self.set_value(ATTR_LAST_ERROR, str(readout_output))
        self.logger.error(
            "Command error\nCommand: {!r}\nOutput: {!r}\nCommand buffer: {!r}".format(
                readout_command, readout_output, self.commands_buffer
            )
        )

    def handle_observer_attached(self, observer):
        """
        Callback on Observer Detached event.

        :param Observer observer: Observer
        """
        observer.subject_update(ATTR_STATUS, self.get_value(ATTR_STATUS), self)

    def handle_observer_detached(self, observer):
        """
        Callback on observer Attached event.

        :param Device observer: Observer
        """

    def handle_readout(self, readout_buffer) -> tuple:
        """
        We have data in readout_buffer.
        First pop from commands_buffer to get metadata of the command.
        Calculate command latency and push it to the buffer.

        :param str readout_buffer: Response to request from Device
        :return str: Attribute, Response, Callback, Token
        """
        self.response_timestamp = time.time()

        try:
            (
                attribute,
                token,
                callback,
                _returning,
            ), command_init_timestamp = self.commands_buffer.popleft()
            latency = (time.time() - command_init_timestamp) * 1000
            self.latency_buffer.append(latency)
            if len(self.latency_buffer) == self.latency_buffer.maxlen:
                self.set_attribute(
                    (ATTR_LATENCY, VALUE),
                    sum(self.latency_buffer) / self.latency_buffer.maxlen,
                )
                self.set_value(ATTR_HANGING_COMMANDS, len(self.commands_buffer))
                self.latency_buffer.clear()
        except IndexError:
            self.handle_response_error(
                "Trying to pop from empty command buffer. "
                "Content of readout buffer is: {}".format(readout_buffer)
            )
            return RESPONSE_ERROR, "", None, False

        if self.command_encoding is None:
            return attribute, readout_buffer, callback, token
        else:
            return attribute, "".join(readout_buffer), callback, token

    def disconnect(self) -> bool:
        """
        Call this function to cleanly close connection.

        :return bool: True if successful
        """
        if self.closing:
            return False
        elif self.connected:
            self.close_connection()
        elif self.connecting:
            self.close()
        return True

    def close_connection(self):
        """
        Call this function when closing connected Device.

        Stop polling and continue with close() method.
        """
        self.stop_polling()
        self.close()

    def close(self) -> bool:
        """
        When Device is close(), set all connection flags to False.
        Device is now Disconnected from Physical interface.
        Close socket, close port, etc...
        :return bool: True if successful
        """
        if self.closing:
            return False
        else:
            self.closing = True
            self.connected = False
            self.set_status(STATUS_DISCONNECTED)
            self.closing = False
            self.connected = False
            return True

    def reconnect(self) -> bool:
        """
        Reconnect devices.
        :return bool: True if successful
        """
        mapping = self.yaml_mapping()
        self.__init__(**mapping)  # type: ignore
        # rather than calling reconnect and re-initializing the class, it would be
        # better to re-instantiate the device
        return True

    def set_status(self, status):
        """
        Set attributes status value.
        There is no restriction for STATUS value.
        But to ensure Device is fully compatible it should be one of the following:
            STATUS_DISCONNECTED: Device is not connected (not ready)
            STATUS_CONNECTING: Device called connect() method (not ready)
            STATUS_CONNECTED: Device is connected (not ready)
            STATUS_CONFIGURING: Device is configuring (not ready)
            STATUS_CONFIGURED: Device is configured (ready)
            STATUS_IDLE: Device is IDLE (finished previous task - ready)
            STATUS_BUSY: Device is performing a task (not ready)
            STATUS_ERROR: Device is in ERROR state (not ready)
            STATUS_DISCONNECTING: Device is disconnecting (not ready)
        STATUS_IDLE and STATUS_CONFIGURED can be interchanged.
        But STATUS_CONFIGURED server as a metadata indicating, that it was configured at
        least once.

        :param str status: Status of Device
        """
        self.set_value(ATTR_STATUS, status)

    def is_status(self, status) -> bool:
        """
        Compare status and current Device status

        :param str status: Status to compare
        :return bool: True if equal
        """
        return bool(self.get_value(ATTR_STATUS) == status)

    def in_statuses(self, statuses: Union[List, Tuple]) -> bool:
        """
        Check list of statuses against current device status.

        :param statuses: List of statuses
        :return: True if current status is in statuses
        """
        return self.get_value(ATTR_STATUS) in statuses

    def start_polling(self):
        """
        This method should be re-implemented.
        Add all polled commands here.
        Call this method at the beginning to reset response and request timestamp.

        Example:
            self.devicePoller.add(devices, command, time in milliseconds)
            self.devicePoller.add(self, 'cmd0', 400)
        """
        self.response_timestamp = self.request_timestamp = time.time()

    def stop_polling(self):
        """Remove Device from device_poller loop."""
        self.device_poller.stop_polling(self)

    def push(self, data):
        """
        Send command to Device.
        This method should be reimplemented for specific interface.
        Use command() for sending commands from Client.

        :param str data: Request to Device
        """

    def command(
        self,
        command: str,
        callback: Optional[Callable] = None,
        with_token: bool = False,
        returning: bool = True,
    ) -> Optional[int]:
        """
        Check command for validity and push it to the poller loop.

        !!! Use only this function to send command to Device. !!!
        Commands are stored into buffer and are flushed on poller tick.
        Command will be executed on next poller tick.
        Attach token if with_token is True.
        Handle request ONLY when returning is True.
        !!! There are Devices, that silently executes command and in that case we are
        not waiting for response. !!!

        :param command: Request to Device
        :param callback: callback after Device replies to Command
        :param with_token: token
        :param returning: bool
        :return: token
        """
        if not self.valid_command_format(command):
            raise CommandFormatException("Command '{}' form is invalid".format(command))

        if self.connected or self.connecting:
            token = 0
            if with_token is True:
                token = next(self.token_generator)
            elif with_token >= 1:
                token = with_token
            self.device_poller.prepare_command(
                self, (command, token, callback, returning)
            )
            return token

        return None

    def remove(self):
        """Remove Device completely from Server and Session."""
        self.disconnect()

        if self.logger is not None:
            for handler in self.logger.handlers[:]:
                handler.close()

        self.logger = None
        if self.session is not None:
            self.session.remove_device(self)

        for cb_tuples in self.attribute_attach_map.values():
            for cb_tuple in cb_tuples:
                self.detach_attribute_callback(*cb_tuple)

        self.attribute_attach_map = None
        self.attributes = None
        self.exposed_methods = None
        self.token_generator = None
        self.connecting_time = None
        self.response_timestamp = None
        self.request_timestamp = None
        self.connected = None
        self.connecting = None
        self.closing = None
        self.closed = None
        self.connection_error = None
        self.response_error = None
        self.commands_buffer = None

    def valid_command_format(self, command) -> bool:
        """
        Check if command format is valid.

        Return False or optionally raise CommandFormatException.
        Re-implement this method for any other device.

        :param str command: Input command
        :return bool: True if has valid format
        """
        return command is not None

    def send_command(self, commands: List[Any]) -> List[Any]:
        """
        Send command using defined interface (TCP/IP, RS232, ...).
        !!! Make sure to call it directly when it's needed, for example for Connection
        handshake.!!! Unicode command is always .encode() into ASCII before it's send to
        the interface.

        :param list commands: list of commands to be send
        :return list: list of NOT sent commands
        """
        if not self.accepting_commands():
            return commands
        try:
            mark = time.time()
            if self.connected:
                command_data = b"" if self.command_encoding is None else ""
                commands_to_push_counter = 0
                while commands:
                    command = commands.pop(0)
                    commands_to_push_counter += 1
                    command_data += command[0]
                    if len(command_data) > self.push_buffer_size:
                        commands.insert(0, command)
                        command_data = command_data[: -len(command[0])]
                        break
                    if command[3]:  # If command is returning
                        self.commands_buffer.append((command, mark))
                    else:  # Command is not returning, simulate immediate execution
                        self.response_timestamp = mark
                    if commands_to_push_counter >= self.push_commands_max:
                        break
                if self.command_encoding is None:
                    # command_data is of type bytes
                    self.push(command_data)
                else:
                    if not isinstance(command_data, str) or not isinstance(
                        self.command_encoding, str
                    ):
                        raise TypeError(
                            "command_data and command_encoding should be strings"
                        )
                    self.push(command_data.encode(self.command_encoding))
            else:
                self.handle_response_error("Device is not connected")
        except IndexError:
            self.handle_connection_error(
                "Device {} buffer error".format(self.device_id)
            )
        except (WriteException, serial.SerialException):
            self.handle_response_error("Device {} writing error".format(self.device_id))
        finally:
            # pylint: disable=lost-exception
            return commands

    def accepting_commands(self) -> bool:
        """
        Check if device is ready to send another commands.

        :return: bool
        """
        self.request_timestamp = time.time()
        if not self.connected or len(self.commands_buffer) > 0:
            return False
        else:
            return True

    def poll_command(self, command, interval):
        """
        Add command to device poller loop to be polled in desired interval.

        :param str command: Request / Command
        :param int interval: interval in ms
        """
        self.device_poller.add(self, command, interval)

    def remove_poll_command(self, command, interval):
        """
        Remove command from device poller loop.

        :param str command: Command to remove
        :param interval: interval in ms
        """
        self.device_poller.remove(self, command, interval)

    def _config_attributes(self):
        """
        Set attributes to desired values found in config.
        Always call this from handle_configuration method.
        """
        if self.config:
            self.config_filtered_attributes(
                attributes=self.config.get("attributes", {})
            )

    def config_filtered_attributes(
        self, attributes: Dict[Tuple[str, str], Any]
    ) -> None:
        """
        Set attributes to desired values found in config.

        The concept is similar to _config_attributes, except that this time the config
        must be provided. This allows filtering some keys from the existing config and
        more tailored behaviour in handle_configuration.
        """
        for attribute, value in attributes.items():
            unit = self.get_attribute(attribute[:-1])[UNIT]
            if unit in (None, "") or attribute[-1] == UNIT:
                self.set_attribute(attribute, value)
            else:
                if isinstance(value, list):
                    set_value = []
                    for v in value:
                        try:
                            set_value.append(
                                self.to_device_unit(list(attribute[:-1]), v).m
                            )
                        except (UndefinedUnitError, DimensionalityError):
                            set_value.append(v)
                else:
                    try:
                        set_value = self.to_device_unit(list(attribute[:-1]), value).m
                    except (UndefinedUnitError, DimensionalityError):
                        set_value = value
                self.set_attribute(attribute, set_value)

    def _config_commands(self):
        """
        Execute required methods found in commands section of config
        Always call this from handle_configuration method.
        """
        if self.config:
            for command in self.config.get("commands", []):
                self.command(command)

    def _expose_methods_to_clients(self):
        """Expose all decorated methods with @expose_method to the Client."""
        for method in dir(self):
            method = getattr(self, method)
            if (
                callable(method)
                and hasattr(method, "exposed_parameters")
                and method.__name__ not in self.exposed_methods
            ):
                self.exposed_methods.append(
                    (method.__name__, method.exposed_parameters)
                )

    def wait_for_status(
        self,
        statuses: List,
        retry_timeout: int = 1000,
        throw_exception: bool = True,
        callback: Optional[Callable] = None,
    ) -> Union[bool, Thread]:
        """
        Wait until device change it's status in one defined in statuses.
        Method is non blocking, when callback is set.

        :param statuses: List of one or multiple statuses to check
        :param retry_timeout: Maximum time in ms to wait for status in ms
        :param throw_exception: Raise exception when True
        :param callback: Function to call after check is finished
        :return: True if device is in one of statuses
        """

        def _wait(_callback=None):
            success = self.in_statuses(statuses)
            retry_counter = 0
            while not success:
                if not self.connected:
                    break
                time.sleep(0.05)
                retry_counter += 50
                success = self.in_statuses(statuses)
                if retry_counter >= retry_timeout:
                    break
            if _callback is not None:
                _callback(success)
            elif throw_exception:
                if not success:
                    raise DeviceError(
                        "Status was not set to {} within timeout of {} ms".format(
                            statuses, retry_timeout
                        )
                    )
                else:
                    return True
            else:
                return success

        if callback is None:
            return bool(_wait())
        else:
            thread = Thread(target=_wait, args=[callback])
            thread.start()
            return thread

    def wait_until_value_set(
        self,
        attribute: Union[List, Tuple, str],
        value: Any,
        retry_timeout: int = 1000,
        throw_exception: bool = True,
        callback: Optional[Callable] = None,
    ) -> Union[bool, Thread]:
        """
        Trigger the callback or block until the attribute is set to the requested value.

        There is retry_timeout of 1000ms until DeviceError is raised.

        :param attribute: Attribute to check
        :param value: Value to check
        :param retry_timeout: Retry check timeout in ms
        :param throw_exception: Raise exception when True
        :param callback: Function to call after check is finished
        :return: True if Attribute's value is equal
        """

        def _wait(_callback=None):
            attribute_object = self.get_attribute(attribute)
            success = attribute_object[VALUE] == value
            retry_counter = 0
            while not success:
                if not self.connected:
                    break
                time.sleep(0.05)
                retry_counter += 50
                success = attribute_object[VALUE] == value
                if retry_counter >= retry_timeout:
                    break
            if _callback is not None:
                _callback(success)
            elif throw_exception:
                if not success:
                    raise DeviceError(
                        "Value of {} was not set to {} within timeout of {} ms".format(
                            attribute, value, retry_timeout
                        )
                    )
                else:
                    return True
            else:
                return success

        if callback is None:
            return bool(_wait())
        else:
            thread = Thread(target=_wait, args=[callback])
            thread.start()
            return thread

    def is_alive(self) -> bool:
        """
        Check if device is still connected.

        :return bool: True if Device is connected
        """
        if not self.connected or self.closing or self.response_error:
            return False
        time_diff = self.request_timestamp - self.response_timestamp
        if time_diff >= self.response_timeout * 1e-3:
            self.handle_response_error("Response timeout")
            return False
        return True

    def to_device_unit(
        self, attribute: Union[List, Tuple, str], value: Union[int, float, str]
    ) -> Quantity:
        """
        Convert a value to the unit of the corresponding attribute.

        :param attribute: the name of the attribute whose unit should be used for the
         conversion or a sequence [attribute_name, key_name] e.g. [ATTR_POSITION, UNIT]
        :param value: the value to convert
        :return: a pint Quantity with the unit of the attribute
        """
        value = str(value).replace("%", "percent")
        try:
            converted_value: Quantity = units.Quantity(value)
        except UndefinedUnitError as e:
            self.logger.error(f"can't convert {value} to a Quantity")
            raise DeviceUnitError(e)

        attr = self.get_attribute(attribute)
        if attr is None:
            self.logger.error(f"the attribute {attribute} does not exist")
            raise DeviceError(f"the attribute {attribute} does not exist")

        device_unit = attr[UNIT]
        result = convert_to_unit(unit=device_unit, value=converted_value)
        if result is None:
            message = (
                f"unit mismatch between value: '{converted_value}' "
                f"and the unit of the attribute {attribute}: '{device_unit}'"
            )
            self.logger.error(message)
            raise DeviceUnitError(message)
        return result

    @expose_method()
    def server_disconnect(self):
        """This function serves as a disconnect wrapper for Client"""
        self.disconnect()

    @expose_method()
    def server_reconnect(self):
        """This function serves as a reconnect wrapper for Client"""
        self.reconnect()

    @expose_method()
    def get_config(self) -> Any:
        """This function return Device configuration."""
        return yaml.dump(self.config, Dumper=yaml.Dumper)
