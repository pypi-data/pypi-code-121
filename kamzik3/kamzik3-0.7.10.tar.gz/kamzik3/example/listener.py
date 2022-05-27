import json
import pickle
import re
from threading import Event, Thread

import numpy as np
import zmq

from kamzik3.constants import *
from kamzik3.snippets.snippetsJson import JsonKamzikHook


class Listener:
    """
    Simple listener for Kamzik3 broadcast.

    :param host: host of broadcaster
    :param port: port of broadcaster
    :param topics: list of topics subscribe
    :param token_filter: regexp for token filtering
    """

    def __init__(self, host, port, topics=None, token_filter=None):
        self.host = host
        self.port = port
        self.topics = topics
        self.stopped = Event()
        self.token_filter = re.compile(".") if token_filter is None else token_filter
        self.socket = zmq.Context.instance().socket(zmq.SUB)
        self.connect()

    def connect(self):
        """Connect to broadcaster."""
        # Set receive timeout to 100 ms
        self.socket.setsockopt(zmq.RCVTIMEO, 100)
        # Don't let socket linger after close
        # This is VERY IMPORTANT not to set to anything but 0
        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.connect(f"tcp://{self.host}:{self.port}")
        # Subscribe to topics of interest
        for topic in self.topics:
            self.socket.setsockopt_string(zmq.SUBSCRIBE, topic)

    def listen(self, blocking=True):
        """
        Start listening to broadcast in blocking or non blocking way.

        :param blocking: bool flag
        """
        if blocking:
            self._listen()
        else:
            Thread(target=self._listen).start()

    def _listen(self):
        """
        Collect and handle broadcast message until stopped flag is set.

        Kamzik3 is broadcasting many attributes and it's values.
        Format is:

            DeviceId.(type of token).(token header)

        Usually You are interested in Attribute which it token type: A!
        Token header for attribute is in format (Attribute name).(Value | Type | Min | Max | ...)
        For Your application You need only Value.
        Some attributes can have attribute group.
        In that case Attribute name has two levels (Attribute Group.Attribute Name)
        """
        while not self.stopped.isSet():
            if self.socket.poll(timeout=100):
                # Try to read any message from publisher
                reply = self.socket.recv_multipart()
                token, stype = reply[:2]
                # Deserialize data based on type received
                if stype == MSG_JSON:
                    data = json.loads(reply[2].decode(), object_hook=JsonKamzikHook)
                elif stype == MSG_ARRAY:
                    dtype, shape = reply[2:4]
                    reply[4] = np.frombuffer(reply[4], dtype=dtype.decode())
                    data = np.reshape(reply[4], json.loads(shape.decode()))
                elif stype == MSG_PICKLE:
                    data = pickle.loads(reply[2])
                self.handle_readout(token.decode(), data)

    def handle_readout(self, token, data):
        """Override this function to do some action upon received message."""
        if self.token_filter.search(token):
            print(token, data)

    def close(self):
        """Set closing flag and stop listener."""
        self.stopped.set()


if __name__ == "__main__":
    token_filter = re.compile(".Status\.Value|.Header\.Value|.Chain link output\.Value")
    kamzik_listener = Listener("127.0.0.1", 50010, ["Scan_"], token_filter)
    kamzik_listener.listen(blocking=False)
