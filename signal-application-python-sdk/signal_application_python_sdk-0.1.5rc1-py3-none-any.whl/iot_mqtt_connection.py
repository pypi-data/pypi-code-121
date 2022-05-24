"""Mqtt Connection to AWS IoT service
 IoTMqttConnection class is used to create MQTT connection
 between signal application and aws IoT cloud service
"""

import logging
from typing import Callable
from awscrt.io import ClientBootstrap, EventLoopGroup, DefaultHostResolver
from awscrt.mqtt import QoS
from awscrt.exceptions import AwsCrtError
from awsiot import mqtt_connection_builder
from signalsdk.signal_exception import SignalAppIoTConError

OnConnectionSuccessful=Callable[[], None]

class IotMqttConnection:
    """
    A class used to represent Mqtt Connection to AWS IoT service
     IoTMqttConnection class is used to create MQTT connection
     between signal application and aws IoT cloud service
    """

    def __init__(self, app_id, app_config):
        """
        params:
        app_id application Id
        thing_config aws IoT thing configurations including:
        thing name, account Id, device certificate, private
        keys etc
        """

        self.is_connected = False
        self.thingName = app_config["thingName"]
        self.accountId = app_config["accountId"]
        self.appId = self.thingName + "-" + app_id
        self.on_connection_successful_callback = None

        event_loop_group = EventLoopGroup(1)
        client_bootstrap = ClientBootstrap(event_loop_group, DefaultHostResolver(event_loop_group))

        self.mqtt_connection = mqtt_connection_builder.mtls_from_bytes(
            endpoint=app_config["iotEndpoint"],
            cert_bytes=str.encode(app_config["cert"]),
            pri_key_bytes=str.encode(app_config["key"]),
            client_bootstrap=client_bootstrap,
            ca_bytes=str.encode(app_config["ca"]),
            client_id=self.appId,
            clean_session=False,
            keep_alive_secs=30,
            on_connection_interrupted=self.on_connection_interrupted,
            on_connection_resumed=self.on_connection_resumed
        )

    def on_connection_interrupted(self, connection, error, **kwargs):
        logging.warning(f"connection interrupted. error: {error}")

    def on_connection_resumed(self, connection, return_code, session_present, **kwargs):
        logging.warning("connection resumed.")

    def set_on_connection_successful(self, callback):
        self.on_connection_successful_callback  = callback

    def connect(self):
        """
        connect
        """
        logging.info("signalsdk::connecting IotMqtt...")
        if not self.is_connected:
            connected_future = self.mqtt_connection.connect()
            try:
                connected_future.result()
                self.is_connected = True
                logging.info("signalsdk::Connected!")
                self.on_connection_successful_callback()
            except AwsCrtError as err:
                raise SignalAppIoTConError from err

    def get_connection(self):
        return self.mqtt_connection

    def publish(self, topic, payload):
        logging.info(f"signalsdk: iotMqtt publish with: topic:{topic} payload:{payload}")
        publish_future, _ = self.mqtt_connection.publish(topic, payload, QoS.AT_LEAST_ONCE)
        publish_future.result()
