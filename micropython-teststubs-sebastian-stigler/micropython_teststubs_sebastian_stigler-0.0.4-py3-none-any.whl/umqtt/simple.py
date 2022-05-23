from re import T, U
from unittest.mock import Mock


class MQTTClient(Mock):
    def __init__(
        self,
        client_id,
        server,
        port=0,
        user=None,
        password=None,
        keepalive=0,
        ssl=False,
        ssl_params={},
    ):
        super().__init__()
        self._client_id = client_id
        self._server = server
        self._port = port
        self._user = user
        self._password = password
        self._keepalive = keepalive
        self._ssl = ssl
        self._ssl_params = ssl_params
        self._connect = False
        self._topic = None
        self._message = None

    def connect(self):
        self._connect = True

    def publish(self, topic, message):
        if isinstance(topic, bytes):
            topic = topic.decode()
        if isinstance(message, bytes):
            message = message.decode()
        self._topic = topic
        self._message = message
