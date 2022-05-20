import logging
from typing import Callable
from paho.mqtt.client import Client, MQTT_ERR_SUCCESS

OnEventReceived=Callable[[str], None]

LOCAL_URL = "localhost"

class LocalMqtt():
    def __init__(self):
        self.mqttClient = Client("localmqtt")
        self.eventCallback = None
        self.subscribedTopic = None

    def set_on_event_received(self, callback):
        self.eventCallback = callback

    def on_message_received(self, client, userdata, message):
        payload = str(message.payload.decode("utf-8"))
        topic = message.topic
        logging.info(f"{__name__}: signalsdk: message received topic:{topic} payload:{payload}")
        try:
            self.eventCallback(payload)
        except TypeError:
            logging.info(f"{__name__}: signalsdk: on_message_received callback error")

    def on_disconnect(self, client, userdata, rc):
        logging.info(f"signalsdk::disconnecting reason: {str(rc)}")

    def on_connect(self, client, userdata, flags, rc):
        logging.info("signalsdk::Local MQTT connection established")

    def get_client(self):
        return self.mqttClient

    def connect(self):
        logging.info(f"signalsdk::{__name__}: signalsdk: connect...")

        self.mqttClient.on_message=self.on_message_received
        self.mqttClient.on_disconnect = self.on_disconnect
        self.mqttClient.on_connect = self.on_connect
        self.mqttClient.connect(LOCAL_URL)
        self.mqttClient.loop_start()

    def publish(self, topic, payload):
        self.mqttClient.publish(topic, payload)

    def subscribe(self, topic):
        if topic == self.subscribedTopic:
            logging.info(f"signalsdk::topic already subscribed, topic:{topic}")
        else:
            self.subscribedTopic = topic
            result, _ = self.mqttClient.subscribe(topic)
            if result != MQTT_ERR_SUCCESS:
                logging.error(f"signalsdk::Failed to subscribe topic: {topic}")

    def unsubscribe(self):
        logging.info(f"signalsdk::unsubscribing, topic:{self.subscribedTopic}")
        result, _ = self.mqttClient.unsubscribe(self.subscribedTopic)
        if result != MQTT_ERR_SUCCESS:
            print(f"signalsdk::Failed to unsubscribe topic: {self.subscribedTopic}")
        self.subscribedTopic = None

    def get_subscribed_topic(self):
        return self.subscribedTopic
