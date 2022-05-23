from .producer_manager import ProducerManager
from ..utils.helpers import Helpers

import datetime
import urllib.request
import socket
import time


class HeartbeatManager:
    def __init__(self, kafka_heartbeat_producer: ProducerManager, heartbeat_interval, client_id):
        self.heartbeat_interval = heartbeat_interval
        self.client_id = client_id
        self.kafka_heartbeat_producer = kafka_heartbeat_producer
        self.helper = Helpers()
        self.interval_thread = {}

    def start_heartbeat_async(self):
        self.interval_thread = self.helper.set_interval(self.send_heartbeat_message, self.heartbeat_interval)

    def send_heartbeat_message(self):
        date = datetime.datetime.utcnow()
        date_ms = int(time.mktime(date.timetuple())) * 1000

        # Get data for origin stringified json
        hostName = str(socket.gethostname())
        hostIP = str(socket.gethostbyname(hostName))
        try:
            externalIP = str(urllib.request.urlopen("http://ipv4bot.whatismyipaddress.com").read().decode("utf-8"))
        except urllib.error.URLError as e:
            externalIP = "unknown"

        message_json = {"id": self.client_id, "alive": date_ms,
                        "origin": "{hostname: %s, localIP: %s, externalIP: %s}" % (hostName, hostIP, externalIP)}

        messages = [{"message": message_json}]
        self.kafka_heartbeat_producer.send_messages(messages)

    def stop(self):
        self.interval_thread()
