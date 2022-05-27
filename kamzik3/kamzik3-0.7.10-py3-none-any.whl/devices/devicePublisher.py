import json
import logging
from threading import Thread

import numpy as np

from kamzik3.constants import MSG_JSON, MSG_ARRAY
from kamzik3.snippets.snippetsJson import JsonKamzikEncoder
from kamzik3.snippets.snippetsZmq import Publisher


class DevicePublisher(Publisher, Thread):
    def __init__(self, host, port, zmq_context=None):
        self.logger = logging.getLogger("Console.DeviceServer@{}:{}".format(host, port))
        Thread.__init__(self)
        Publisher.__init__(self, host, port, zmq_context)

    def _publish_message(self, header, message):
        try:
            if isinstance(message, np.ndarray):
                self.socket_publisher.send_multipart(
                    [
                        header.encode(),
                        MSG_ARRAY,
                        str(message.dtype.name).encode(),
                        json.dumps(message.shape).encode(),
                        message,
                    ],
                    copy=False,
                )
            else:
                json_message = json.dumps(
                    message, cls=JsonKamzikEncoder, ensure_ascii=True
                )
                self.socket_publisher.send_multipart(
                    [header.encode(), MSG_JSON, json_message.encode()], copy=False
                )
        except Exception as e:
            self.logger.error("{}, {}, {}".format(e, header, message))
