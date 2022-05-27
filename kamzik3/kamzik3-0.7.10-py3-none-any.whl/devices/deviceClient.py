""" Example of yaml configuration
DeviceClient0: &DeviceClient0 !Device:kamzik3.devices.deviceClient.DeviceClient
    host: &Server 127.0.0.1
    port: &Port 60000
    device_id: DeviceIdOnServer
"""
import json
import pickle
import time
from threading import Thread, Event, RLock
from typing import Any, Callable, Optional, Tuple, Union

import numpy as np
import zmq
from zmq.utils.monitor import recv_monitor_message

import kamzik3
from kamzik3 import DeviceClientError
from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.devices.device import Device
from kamzik3.snippets.snippetDataAccess import get_from_dict, set_in_dict, is_equal
from kamzik3.snippets.snippetsJson import JsonKamzikEncoder, JsonKamzikHook


class DeviceClient(Device):
    """
    Here comes a short description of the class DeviceClient.

    - connect()
    - handle_connect_event()
        - handle_connect()
        - handle_configuration_event()
            - handle_configuration()
    """

    initial_status = STATUS_DISCONNECTED

    def __init__(self, host, port, device_id=None, config=None):
        self.subscription_thread = None
        Device.__init__(self, device_id, config)
        self.client_comm_lock = RLock()
        self.host = host
        self.port = port
        self.removing = False
        self.subscriber_port = None
        self.socket = None
        self.subscriber_socket = None
        self.monitor_socket = None
        self.monitor_thread = None
        self.callbacks = {}
        self.stopped = Event()
        self.subscribe_starts_with_list = []
        self.connect()

    # pylint: disable=unused-argument
    def connect(self, *args):
        """
        Here we want to connect first to ZMQ main server.

        We have to verify connection and do it in non blocking fashion.
        We just push devices in a pool and verify it in device_poller Thread.
        """
        self.logger.info(
            "Initiating connection to the server {}:{}".format(self.host, self.port)
        )
        self.connecting = True
        self.connected = False
        self.set_status(STATUS_CONNECTING)
        # Get REQ type of socket
        self.socket = zmq.Context.instance().socket(zmq.REQ)
        # Set initial receive timeout to 20000 ms
        self.socket.setsockopt(zmq.RCVTIMEO, 20000)
        # This is VERY IMPORTANT not to set to anything but 0
        self.monitor_socket = self.socket.get_monitor_socket()
        self.monitor_thread = Thread(target=self.connect_monitor_thread)
        self.monitor_thread.start()
        try:
            self.socket.connect("tcp://{}:{}".format(self.host, self.port))
        except zmq.ZMQError:
            self.handle_connection_error("Fatal connection error")
            return

    def set_status(self, status):
        self._set((ATTR_STATUS, VALUE), status)

    def connect_monitor_thread(self):
        """
        In order to monitor connect event we are using monitor socket.

        This socket is also used to catch disconnection from server.
        """
        while not self.stopped.is_set():
            if self.monitor_socket.poll(timeout=500):
                message = recv_monitor_message(self.monitor_socket)
                if message["event"] == zmq.EVENT_CONNECTED:
                    try:
                        self.handle_connect_event()
                    except DeviceClientError:
                        # Server is ready, but device not yet configured
                        if not self.stopped.wait(5):
                            self.close()
                            self.reconnect()
                    return

    def handle_connect_event(self):
        """
        This method is called after we verified connection with main server.

        We continue with init method to subscribe to devices publisher.
        """
        if self.init():
            self.connected = True
            self.connecting = False
            self.handle_configuration_event()
            self.set_status(self.get_attribute([ATTR_STATUS, VALUE]))
            # Subscribe for all attribute changes
            token = self.get_token(TOKEN_ATTRIBUTE)
            self._subscribe(token)
            self.subscribe_starts_with_list = token
            # Check for attribute sharing and subscribe to them
            for attribute_id in self.attributes_sharing_map:
                self._subscribe(attribute_id)

    def _init_subscriber_thread(self, host, port):
        """
        We are connected to the main server.

        Now we want to connect to the devices publisher.
        """
        self.logger.info(
            "Initializing {} client subscriber thread".format(self.device_id)
        )
        # Get SUB type of socket
        self.subscriber_socket = zmq.Context.instance().socket(zmq.SUB)
        # Set receive timeout to 100 ms
        self.subscriber_socket.setsockopt(zmq.RCVTIMEO, 100)
        # Don't let socket linger after close
        # This is VERY IMPORTANT not to set to anything but 0
        self.subscriber_socket.setsockopt(zmq.LINGER, 0)
        self.subscriber_socket.connect("tcp://{}:{}".format(host, port))
        # Start separate Thread to read data from publisher
        self.subscription_thread = Thread(target=self._subscriber_thread)
        self.subscription_thread.start()

    def _subscriber_thread(self):
        """
        Continuously collect data from publisher.

        Interrupt every zmq.RCVTIMEO and check if client is connected.
        """
        # Check for published messages until client is connected
        while not self.stopped.is_set():
            if self.subscriber_socket.poll(timeout=100):
                # Try to read any message from publisher
                reply = self.subscriber_socket.recv_multipart()
                token, stype = reply[:2]
                data: Optional[Any] = None
                if stype == MSG_JSON:
                    data = json.loads(reply[2].decode(), object_hook=JsonKamzikHook)
                elif stype == MSG_ARRAY:
                    dtype, shape = reply[2:4]
                    reply[4] = np.frombuffer(reply[4], dtype=dtype.decode())
                    data = np.reshape(reply[4], json.loads(shape.decode()))
                elif stype == MSG_PICKLE:
                    data = pickle.loads(reply[2])
                # Better solution: raise an exception if we get data of unknown type
                if data is None:
                    raise Exception(f"unknown data packet type {stype}")
                self.handle_readout(token.decode(), data)
            elif self.monitor_socket.poll(timeout=0):
                # Check if there is any message to read from monitor socket
                message = recv_monitor_message(self.monitor_socket)
                if message["event"] == zmq.EVENT_DISCONNECTED:
                    self.handle_response_error("Socket disconnected")
                    break

        # Client was disconnected for any reason, finish cleaning up and possibly reconnect
        self.handle_disconnect()

    def _subscribe(self, topic):
        """
        Subscribe for Topic.

        :param topic: string
        """
        self.subscriber_socket.setsockopt_string(zmq.SUBSCRIBE, topic)

    def _unsubscribe(self, topic):
        """
        Unsubscribe Topic.

        :param topic: string
        """
        self.subscriber_socket.setsockopt_string(zmq.UNSUBSCRIBE, topic)

    def set_callback(self, token, callback):
        """
        Set callback when token is received from publisher.

        If remove_after is set, remove callback from buffer and don't repeat it again.
        Callback has to be callable function.

        :param token: string
        :param callback: function(devices, data)
        :return: bool
        """
        assert callable(callback)

        if token not in self.callbacks:
            self.callbacks[token] = []

        callback_data = callback

        if callback_data not in self.callbacks[token]:
            self.callbacks[token].append(callback_data)
            self._subscribe(token)
            self.logger.debug("Set callback for token {}".format(token))
            return token
        else:
            self.logger.warning("Callback is already set")
            return False

    # pylint: disable=arguments-differ
    def handle_readout_callback(self, token, callback_data):
        """
        Handle callback for token.

        :param token: string
        :param callback_data: mixed
        """
        self._unsubscribe(token)
        while len(self.callbacks.get(token)) > 0:
            callback = self.callbacks.get(token).pop()
            callback(*callback_data)

        if len(self.callbacks[token]) == 0:
            del self.callbacks[token]

    # pylint: disable=arguments-differ
    def handle_readout(self, token, data):
        """
        Handle subscribed data.

        The most important meta is token which holds information
        what to do with received data.
        First check if token is within callback hooks.
        If not then parse token an update Device's attribute.

        :param token: "." separated mete info
        :type token: str
        :param data: Dict holding data items
        :type data: dict
        """
        if token in self.callbacks:
            # Check if there is handle hook for given token
            self.handle_readout_callback(token, data)
        else:
            attribute_parts = token.split(".")
            attribute_id = ".".join(attribute_parts[:-1])
            if attribute_parts[1] == TOKEN_ATTRIBUTE:
                if attribute_parts[-1] == TOKEN_ATTRIBUTE_REPLACE:
                    attribute_path = attribute_parts[2:-1]
                    attribute_path = self.attributes_sharing_map.get(
                        attribute_id, attribute_path
                    )

                    sync_tree = self.attributes
                    for part in attribute_path:
                        if part not in sync_tree:
                            sync_tree[part] = {}
                        sync_tree = sync_tree[part]
                    self._set(attribute_path, Attribute.from_dict(data))
                elif attribute_parts[-1] == TOKEN_ATTRIBUTE_DELETE:
                    attribute_path = attribute_parts[2:-1]
                    attribute_path = self.attributes_sharing_map.get(
                        attribute_id, attribute_path
                    )
                    sync_tree = self.attributes[attribute_path[:-1]]
                    del sync_tree[attribute_path[-1]]
                elif attribute_parts[-1] == TOKEN_ATTRIBUTE_GROUP_DELETE:
                    attribute_path = attribute_parts[2:-1]
                    del self.attributes[attribute_path[0]]
                else:
                    attribute_path = attribute_parts[2:]

                    if attribute_id in self.attributes_sharing_map:
                        for shared_attribute in self.attributes_sharing_map[
                            attribute_id
                        ]:
                            self._set(shared_attribute + [attribute_parts[-1]], data)
                    if token.startswith(self.subscribe_starts_with_list):
                        self._set(attribute_path, data)

                # If publisher is defined, forward data to it
                if kamzik3.session.publisher is not None:
                    kamzik3.session.publisher.push_message(token, data)

    def init(self):
        """
        Initiate device connection.

        Get publisher port and devices attributes.
        :return: bool
        """
        try:
            with self.client_comm_lock:
                self.socket.send_multipart(
                    [INSTRUCTION_INIT, self.device_id.encode()], copy=False
                )
                status, _token, response = self.handle_server_response()
            if status == RESPONSE_OK:
                allow_proxy = self.config.get("allow_proxy", True)
                (
                    attributes,
                    self.attributes_sharing_map,
                    self.exposed_methods,
                    self.qualified_name,
                    device_proxy,
                    device_publisher,
                ) = json.loads(response, object_hook=JsonKamzikHook)
                if device_proxy is not False and allow_proxy:
                    self.host, self.port = device_proxy
                    self.close()
                    self.reconnect()
                    return False
                self.initial_status = attributes[ATTR_STATUS][VALUE]
                self._sync_attributes(attributes, self.attributes)
                for method_name, attributes in self.exposed_methods[:]:
                    setattr(
                        self,
                        method_name,
                        lambda method_name=method_name, **kwargs: self.method(
                            method_name, kwargs
                        ),
                    )
                self._init_subscriber_thread(*device_publisher)
                # We synced all attributes, now we want to decrease receive timeout
                self.socket.setsockopt(zmq.RCVTIMEO, 5000)
                return True
            else:
                raise DeviceClientError("Failed to initialize device")

        except (zmq.Again, zmq.ZMQError):
            self.handle_response_error("Init error")
            self.reconnect()
            return False

    def _sync_attributes(self, synced_attributes, parent_attribute):
        """
        synchronize new attributes with already existing attributes.

        This is important to prevent creating new attribute objects.
        We can just create new attributes, but we would lost all callbacks and all
        references will become invalid.

        :param synced_attributes: dict
        """
        # Walk through all items of dictionary
        for key, attribute in synced_attributes.items():
            self._sync_attribute(key, attribute, parent_attribute)

    def _sync_attribute(self, key, attribute, parent_attribute):
        """
        synchronize one attribute from new dict to existing self.attributes.

        :param key: string
        :param attribute: dict
        """
        if key in parent_attribute:
            if Attribute.is_attribute(attribute):
                if key == ATTR_STATUS and parent_attribute == self.attributes:
                    return
                # Key exists in self.attributes
                # Prevent attribute changes when syncing with new values
                for attr_key in attribute.keys():
                    if not is_equal(
                        parent_attribute[key][attr_key], attribute[attr_key]
                    ):
                        parent_attribute[key][attr_key] = attribute[attr_key]
            else:
                # Attribute is only sub group, continue syncing deeper
                self._sync_attributes(attribute, parent_attribute[key])
        else:
            # Key des not exists in self.attributes
            if Attribute.is_attribute(attribute):
                # Create completely new Attribute under specified Key
                parent_attribute[key] = Attribute.from_dict(attribute)
            else:
                # Attribute is only sub group, continue syncing deeper
                parent_attribute[key] = Attribute.from_dict(attribute)

    def get_token(self, topic, device_id=None):
        """
        Just a helper function to generate token for specific topic.

        :param topic: topic meta
        :type topic: str
        :param device_id: ID of device, use this device ID if it's None
        :type device_id: str
        :return:
        :rtype:
        """
        return "{}.{}".format(self.device_id if device_id is None else device_id, topic)

    def set_attribute(self, attribute, value, callback=None):
        """
        Set attribute on devices server.

        :param attribute:
        :param value:
        :param callback:
        :return:
        """
        if not self.connected or self.closing:
            raise DeviceClientError(
                f"Failed to set remote device {self.device_id} {attribute} to {value}.\r\nDevice client is not connected"
            )
        try:
            attribute_value = json.dumps((attribute, value), ensure_ascii=True)
            with self.client_comm_lock:
                self.socket.send_multipart(
                    [
                        INSTRUCTION_SET,
                        self.device_id.encode(),
                        attribute_value.encode(),
                    ],
                    copy=False,
                )
                status, token, response = self.handle_server_response()
            if status == RESPONSE_OK:
                if callback is not None:
                    if token:
                        self.set_callback(self.get_token(token), callback)
                    else:
                        callback(attribute, value)
            else:
                raise DeviceClientError(
                    f"Failed to set remote device {self.device_id} {attribute} to {value} {self.get_attribute(attribute[:-1]).unit()}.\r\n{response}"
                )

            return response

        except (zmq.Again, zmq.ZMQError):
            self.handle_response_error("Set error")
            return False

    # pylint: disable=arguments-differ
    def set_value(self, attribute, value, callback=None):
        """
        Set attribute value.

        :param attribute: list, dict, str
        :param value: mixed
        :return:
        """
        attribute_list = Attribute.list_attribute(attribute)
        return self.set_attribute(attribute_list + [VALUE], value, callback)

    def set_raw_value(self, attribute, value):
        """
        Set attribute value obtained from device.

        Apply offset and factor before value is set.

        :param attribute: list, dict, str
        :param value: mixed
        """
        raise DeviceClientError(
            "Set raw value is not implemented on Client."
            "Use set_value or set_attribute instead."
        )

    def _set(self, attribute, value, callback=None):
        """
        This sets Device attribute.

        Use this function when You want to set attribute by tuple or list key.
        Example: Device.set((ATTR_STATUS, VALUE), STATUS_IDLE)

        :param attribute: tuple, list, str
        :param value: mixed
        """
        current_value = get_from_dict(self.attributes, attribute)
        if not is_equal(value, current_value):
            set_in_dict(self.attributes, attribute, value)

    # pylint: disable=arguments-differ
    def command(  # type: ignore
        self, command: str, callback: Optional[Callable] = None, returning: bool = False
    ) -> Union[bool, str]:
        """
        Execute raw command directly on devices.

        :param command: string
        :param callback: function(devices, outputOfCommand)
        :return:
        """
        if not self.connected or self.closing:
            raise DeviceClientError(
                "Remote command {0!r} execution failed. Client is not connected".format(
                    command
                )
            )

        try:
            with self.client_comm_lock:
                self.socket.send_multipart(
                    [
                        INSTRUCTION_COMMAND,
                        self.device_id.encode(),
                        command.encode(),
                        b"1" if callback else b"0",
                    ],
                    copy=False,
                )
                server_response = self.handle_server_response()
                if server_response is None:
                    status = RESPONSE_ERROR
                else:
                    status, token, response = server_response

            if status == RESPONSE_OK:
                if token and callback is not None:
                    self.set_callback(self.get_token(token), callback)
            else:
                raise DeviceClientError(
                    "Failed to execute remote command '{}'\n{}".format(
                        command, response
                    )
                )
            return response
        except (zmq.Again, zmq.ZMQError) as e:
            self.handle_response_error("Command error: {}".format(e))
            return False

    def method(self, method, attributes=None):
        """
        Execute devices method with associated attributes.

        :param method: string
        :param attributes: json formatted string
        :return:
        """
        if not self.connected or self.closing:
            raise DeviceClientError(
                "Method {} remote execution failed. Client is not connected".format(
                    method
                )
            )

        try:
            dumped_attributes = json.dumps(
                attributes, ensure_ascii=True, cls=JsonKamzikEncoder
            )
            with self.client_comm_lock:
                self.socket.send_multipart(
                    [
                        INSTRUCTION_METHOD,
                        self.device_id.encode(),
                        str(method).encode(),
                        dumped_attributes.encode(),
                    ],
                    copy=False,
                )
                status, _token, response = self.handle_server_response()
            if status == RESPONSE_OK:
                return json.loads(response, object_hook=JsonKamzikHook)
            else:
                raise DeviceClientError(
                    "Failed to execute remote method '{}'\n{}".format(method, response)
                )

        except (zmq.Again, zmq.ZMQError) as e:
            self.handle_response_error("Method error: {}".format(e))
            return False

    def handle_server_response(self) -> Optional[Tuple[str, str, str]]:
        """
        This is crucial moment here.

        If server takes more then RCVTIMEO time, then we get zmq error.
        In that case modify server response time or increase RCVTIMEO time.
        """
        message = self.socket.recv_multipart()
        status, token, msg_type = message[:3]
        if msg_type == MSG_JSON or msg_type == MSG_FILE:
            return status.decode(), token.decode(), message[3].decode()
        else:
            return None

    def handle_configuration(self):
        start_at = time.time()
        self._config_attributes()
        self._config_commands()
        self.set_status(STATUS_CONFIGURED)
        self.set_status(self.initial_status)
        self.logger.info(
            "Device configuration took {} sec.".format(time.time() - start_at)
        )

    def handle_response_error(self, message=None):
        if self.logger is not None:
            self.logger.warning(message)
            self.response_error = True
            self.close()

    def handle_connection_error(self, message=None):
        self.logger.error(message)
        self.connection_error = True
        self.disconnect()

    def handle_command_error(self, readout_command, readout_output):
        self.logger.error(
            "Command error\nCommand: {}\nOutput: {}".format(
                readout_command, readout_output
            )
        )

    def disconnect(self):
        self.close()

    def close(self):
        if self.logger is not None:
            self.logger.info("Closing client")
        self.closing = True
        if self.socket is not None:
            self.socket.disable_monitor()
        self.set_status(STATUS_DISCONNECTING)
        self.stopped.set()

    def handle_disconnect(self):
        if self.logger is not None:
            self.logger.info("Client closed")
        if not self.removing:
            self.closing = False
            self.connected = False
            self.set_status(STATUS_DISCONNECTED)
            if self.response_error or self.connection_error:
                self.reconnect()

    def remove(self):
        self.removing = True
        Device.remove(self)
