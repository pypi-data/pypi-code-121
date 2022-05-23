import socket
from datetime import datetime

from logging.handlers import SocketHandler

from .serializer import serialize_message


def format_timestamp(time):
    tstamp = datetime.utcfromtimestamp(time)
    return tstamp.strftime("%Y-%m-%dT%H:%M:%S") + ".%03d" % (tstamp.microsecond / 1000) + "Z"


class TCPLogstashHandler(SocketHandler):
    """
    Python logging handler for Logstash. Sends events over TCP.
    :param host: The host of the logstash server.
    :param port: The port of the logstash server (default 5959).
    """

    def __init__(self, host, port=5959):
        super().__init__(host, port)
        self._host = socket.gethostname()

    def makePickle(self, record):
        return serialize_message(
            self.formatter.format(record),
            {
                'logger': {
                    'host': self._host,
                    'path': record.pathname,
                    'timestamp': format_timestamp(record.created),
                    'level': record.levelname,
                    'logger_name': record.name,
                },
                **getattr(record, 'metadata', {}),
            }
        )
