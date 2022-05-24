import inspect
import sys
import traceback
import uuid
import warnings
from typing import Callable, Union

import paho.mqtt.client as mqtt

from .exceptions import ConnectionError
from .exceptions import PublishError
from .exceptions import SubscriptionError
from .logger import Logger


class MQTTClient:
    """Client base class for MQTT Publisher and Subscriber.

    Provides methods required for connecting to a MQTT-Broker.

    Attributes:
        instances: Static attribute of the class, containing all instances of the class.
            By using a unique identifier for each instance doubles can be avoided.
    """

    instances = {}

    def __init__(self, username: str = None, prefix: str = None,
                 logger: Logger = None, *args, **kwargs):
        """

        Args:
            username: Unique username used as identifier for the client to be created. If None is given, it is created automatically.
            prefix: Inserted to the beginning of each topic.
            logger: Logger for creating a log of activities to console/terminal and/or file.
            *args: Additional optional arguments for initializing the client as of the paho-mqtt package.
            **kwargs: Additional keyword-arguments for initializing the client as of the paho-mqtt package.

        Raises:
            IndexError: If there already exists a client with the given uuid.
        """

        self._logger = logger.get(
            'MQTTClient') if logger is not None else Logger().get('MQTTClient')

        if username in MQTTClient.instances:
            self._logger.error(
                "MQTT Client {} already exists!".format(username))
            raise IndexError("MQTT Client {} already exists!".format(username))

        MQTTClient.instances[username] = self
        self.name = username if username is not None else uuid.uuid4()
        self.prefix = prefix
        self._client = mqtt.Client(username, *args, **kwargs)
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect

        self._client.loop_start()

        self._connected = False

    @classmethod
    def get(cls, username: str) -> 'MQTTClient':
        """Returns the client with given username, if one exists.

        Args:
            username: The unique key identifier of the client to be returned.

        Returns: The client identified by the given key.

        """
        return cls.instances[username]

    @property
    def connected(self) -> bool:
        """ Returns the current connection status of the client

        Returns: True, if the client is connected to a broker, false otherwise.

        """
        return self._connected

    def connect(self, broker: str, username: str, password: str, vhost: str = '', port: Union[str, int] = 0,
                websocket: bool = False, ssl: bool = False, keep_alive: int = 60):
        """Opens a connection to an MQTT-broker under the given address and post.

        Args:
            broker: The address (URL) of the MQTT-broker to connect to.
            username: The username required for authentication at the broker.
            password: The password required for authentication at the broker.
            vhost: Virtual host to connect to at the MQTT-Broker.
            port: The port behind which the broker is running and accessible.
            websocket: If true MQTT messages are published/received over WebSockets. If false, the default transportation over raw TCP is used.
            ssl: If true a secured TLS connection is established.
            keep_alive: maximum period in seconds allowed between communications with the broker.
                If no other messages are being exchanged, this controls the rate at which the client will send ping messages to the broker.

            If not given explicitly given, the port automatically resolved from the values of "websocket" and "ssl".
        """
        try:
            address = broker

            if port == 0:
                if ssl:
                    port = 443 if websocket else 8883
                else:
                    port = 80 if websocket else 1883

            if ssl:
                self._client.tls_set()

            if websocket:
                self._client._transport = "websockets"
                fields = address.split("/")
                address = fields[0]
                path = "/".join(fields[1:])
                print(address, path)
                self._client.ws_set_options(path=f'/{path}')

            if vhost != '' and vhost != '/':
                self._client.username_pw_set(f'{vhost}:{username}', password)
            else:
                self._client.username_pw_set(username, password)

            self._client.connect(address, port, keep_alive)

        except Exception as exception:
            self._logger.error(
                "MQTT Client {} could not connect to {}:{} : {}".format(
                    self.name, broker, port, str(exception)))
            tb = sys.exc_info()[2]
            raise ConnectionError(str(exception)).with_traceback(tb)

    def disconnect(self):
        """Disconnects the client and closes the connection to the broker.

        """
        try:
            self._client.disconnect()
        except Exception as exception:
            self._logger.error(
                "MQTT Client {} could not disconnect: {}".format(self.name,
                                                                 str(exception)))
            tb = sys.exc_info()[2]
            raise ConnectionError(str(exception)).with_traceback(tb)

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._logger.info(
                "MQTT Client {} connect terminated with code {} ({}).".format(
                    self.name, rc, mqtt.error_string(rc)))
            self._connected = True
        else:
            self._logger.error(
                "MQTT Client {} connect terminated with code {} ({}).".format(
                    self.name, rc, mqtt.error_string(rc)))
            self._connected = False

    def _on_disconnect(self, client, userdata, rc):
        if rc == 1:
            self._logger.error(
                "MQTT Client {} disconnected with code {} ({}). \n \t There are various possible reasons for that: \n"
                "\t\t 1. You used port 8883 but did not set the 'ssl' flag (or used port 1883 and set the 'ssl' flag).\n"
                "\t\t 2. You may tried to use Publisher-Credentials for receiving messages or vise versa.\n"
                "\t\t 3. You tried to publish to or subscribe a topic which you are not allowed to do. \n"
                "\t\t 4. Something else, which has not been experienced by the developers of this library. Sorry!\n"
                .format(self.name, rc, mqtt.error_string(rc)))
        else:
            self._logger.info(
                "MQTT Client {} disconnected with code {} ({}).".format(
                    self.name, rc, mqtt.error_string(rc)))
        self._connected = False

    def __del__(self):
        try:
            self._client.loop_stop()
            MQTTClient.instances.pop(self.name)
        except:
            pass


class MQTTPublisher(MQTTClient):
    """Minimal, simple class for publishing MQTT messages.

    """

    def __init__(self, username: str = None, prefix: str = None,
                 logger: Logger = None, *args, **kwargs):
        """

        Args:
            username: Unique username used as identifier for the client to be created. If None is given, it is created automatically.
            prefix: Inserted to the beginning of each topic.
            logger: Logger for creating a log of activities to console/terminal and/or file.
            *args: Additional optional arguments for initializing the client as of the paho-mqtt package.
            **kwargs: Additional optional keyword-arguments for initializing the client as of the paho-mqtt package.
        """
        MQTTClient.__init__(self, username, prefix, logger, *args, **kwargs)
        self._client.on_publish = self._on_publish

    def publish(self, topic: str, message: str, qos: int = 0,
                retain: bool = False):
        """ Publish the given message under the given topic.

        Args:
            topic: The topic the message is published under.
            message: The message to be published. Ideally encoded as UTF-8 string.
            qos: Quality of service level, possible values are 0,1,2.
            retain: If set to True, the message will be set as the “last known good”/retained message for the topic.
        """
        try:
            if self.prefix is not None and self.prefix != "":
                self._client.publish(self.prefix + "/" + topic.strip("/"),
                                     message, qos, retain)
            else:
                self._client.publish(topic.strip("/"), message, qos, retain)
            self._logger.debug(
                "MQTT Client {} will publish the following messsage to {}: {}".format(
                    self.name, topic, message))
        except Exception as exception:
            self._logger.error(
                "MQTT Client {} could not publish to {}: {}".format(self.name,
                                                                    topic,
                                                                    str(exception)))
            tb = sys.exc_info()[2]
            raise PublishError(str(exception)).with_traceback(tb)

    def _on_publish(self, client, userdata, mid):
        self._logger.debug(
            "MQTT Client {} published message {}.".format(self.name, mid))

    # def __shortcut(self, topic, payload, root_topic, qos, retain):
    #     self._client.publish(root_topic + topic, payload, qos, retain)
    #
    # def shortcut(self, root_topic, qos, retain):
    #     return functools.partial(self.__shortcut, root_topic=root_topic.strip("/") + "/", qos=qos, retain=retain)


class MQTTSubscriber(MQTTClient):
    """Minimal, simple class for subscribing, receiving and processing MQTT messages.

    """

    def __init__(self, username: str = None, prefix: str = None,
                 logger: Logger = None, *args, **kwargs):
        """

        Args:
            username:Unique username used as identifier for the client to be created. If None is given, it is created automatically.
            prefix: Inserted to the beginning of each topic.
            logger: Logger for creating a log of activities to console/terminal and/or file.
            *args: Additional optional arguments of the internally used paho-mqtt client.
            **kwargs: Additional optional key word arguments of the internally used paho-mqtt client.
        """
        MQTTClient.__init__(self, username, prefix, logger, *args, **kwargs)
        self._client.on_message = self._on_message
        self._client.on_subscribe = self._on_subscribe
        self._client.on_unsubscribe = self._on_unsubscribe
        self._client.on_connect = self._on_connect

        self._subscriptions = []
        self._on_message_callbacks = {}

    def subscribe(self, topic: str, qos: int = 0):
        """Subscribes the given topic.

        Args:
            topic: The topic to be subscribed given as string.
            qos: Quality of service. Possible values are 0,1,2.

        Raises:
            SubscriptionError: If topic could not be subscribed successfully.
        """
        try:
            topic = f'{self.prefix}/{topic}' if self.prefix is not None and self.prefix != "" else topic
            for s in self._subscriptions:
                if s["topic"] == topic:
                    raise RuntimeError(
                        "Topic {} is already subscribed!".format(topic))
            self._subscriptions.append({"topic": topic, "qos": qos})
            if self.connected:
                self._client.subscribe(topic, qos)
        except Exception as exception:
            self._logger.error(
                "MQTT Client {} could not subscribe to {}: {}".format(self.name,
                                                                      topic,
                                                                      str(exception)))
            tb = sys.exc_info()[2]
            raise SubscriptionError(str(exception)).with_traceback(tb)

    def unsubscribe(self, topic: str):
        """Unsubscribes to updates of the given topic.

        Args:
            topic: The topic which should be unsubscribed given as string.

        Raises:
            SubscriptionError: If topic could not be unsubscribed successfully.
        """
        try:
            topic = self.prefix + "/" + topic if self.prefix is not None and self.prefix != "" else topic
            n = len(self._subscriptions)
            for i in range(n):
                if self._subscriptions[i]["topic"] == topic:
                    if self.connected:
                        self._client.unsubscribe(topic)
                    self._subscriptions.pop(i)
                    return
            raise RuntimeError("Topic {} is not subscribed!".format(topic))

        except Exception as exception:
            self._logger.error(
                "MQTT Client {} could not unsubscribe from {}: {}".format(
                    self.name, topic, str(exception)))
            tb = sys.exc_info()[2]
            raise SubscriptionError(str(exception)).with_traceback(tb)

    def set_callback(self, key: str, function: Callable):
        """Add a callback called at each received message.

        Args:
            key: Unique identifier of the callback.
            function: to be called when a message is received. The function must expect at two arguments.
                First argument is the topic and the second the received message.
        """
        if key in self._on_message_callbacks:
            self._logger.warning("Overwriting callback {}!".format(key))
            warnings.warn("Overwriting callback {}!".format(key),
                          RuntimeWarning)

        signature = inspect.signature(function)
        if len(signature.parameters) < 2:
            self._logger.warning(
                "Callback {} has insufficient parameters!".format(key))
            warnings.warn(
                "Callback {} has insufficient parameters!".format(key))

        self._on_message_callbacks[key] = function

    def remove_callback(self, key: str):
        """Removes the callback with the given key identifier.

        Args:
            key: The unique key identifier of the callback.
        """
        self._on_message_callbacks.pop(key)

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._logger.info(
                "MQTT Client {} connect terminated with code {} ({}).".format(
                    self.name, rc, mqtt.error_string(rc)))
            self._connected = True
            for s in self._subscriptions:
                self._client.subscribe(s["topic"], s["qos"])
        elif rc == 4:
            self._logger.info(
                "MQTT Client {} connect terminated with code {} ({})".format(
                    self.name, rc, mqtt.error_string(rc)))
        else:
            self._logger.error(
                "MQTT Client {} connect terminated with code {} ({}).".format(
                    self.name, rc, mqtt.error_string(rc)))
            self._connected = False

    def _on_subscribe(self, client, userdata, mid, granted_qos,
                      properties=None):
        self._logger.info(
            "MQTT Client {} subscribed with ID {}.".format(self.name, mid))

    def _on_unsubscribe(self, client, userdata, mid):
        self._logger.info(
            "MQTT Client {} unsubscribed with ID {}.".format(self.name, mid))

    def _on_message(self, client, userdata, message):
        for key in self._on_message_callbacks:
            try:
                self._on_message_callbacks[key](message.topic, message.payload)
            except Exception as exception:
                self._logger.error(traceback.format_exc())
                self._logger.error(
                    "Exception while processing callback for topic {}: {}".format(
                        message.topic, str(exception)))
