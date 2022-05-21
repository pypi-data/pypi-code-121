""" module:: dlt.stream
    :synopsis: Common class definitions for dlt stream handlers.
    moduleauthor:: Patrick Menschel (menschel.p@posteo.de)
    license:: CC-BY-NC
"""
import logging
from abc import ABC, abstractmethod
from io import DEFAULT_BUFFER_SIZE
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

from dlt.protocol import DLT_MAGIC_SERIAL, parse_dlt_record, DltRecordType, DltLogLevel, DltRecordIncomplete, \
    DltRecordInvalid

LOG_LEVEL_MAPPING = {DltLogLevel.FATAL: logging.FATAL,
                     DltLogLevel.ERROR: logging.ERROR,
                     DltLogLevel.WARN: logging.WARNING,
                     DltLogLevel.INFO: logging.INFO,
                     DltLogLevel.DEBUG: logging.DEBUG,
                     DltLogLevel.VERBOSE: logging.NOTSET}


class DltStreamLogAdapterABC(ABC):

    def __init__(self, *args, **kwargs):

        self.receiver = None
        self.init_receiver(*args, **kwargs)
        self.rx_handler = Thread(target=self.handle_rx)
        self.rx_handler.daemon = True
        self.rx_handler.start()

    def handle_rx(self) -> None:
        """
        The rx thread. It loops over the serial buffer and self.handle() to handle the received record.

        :return: Nothing.
        """
        buffer = bytearray()
        while True:
            data = self.recv()
            if data:
                buffer.extend(data)
                while DLT_MAGIC_SERIAL in buffer:
                    chunk, buffer = buffer.split(DLT_MAGIC_SERIAL, maxsplit=1)
                    try:
                        record = parse_dlt_record(chunk)
                    except (DltRecordInvalid,
                            NotImplementedError):
                        logging.getLogger(__name__).error(
                            "An Error occurred while parse_dlt_record {0}".format(chunk))
                    except DltRecordIncomplete:
                        break
                    else:
                        self.handle(record=record)

    @staticmethod
    def handle(record: dict) -> None:
        """
        Handle a record.

        :param record: A parsed dlt record.
        :return: Nothing.
        """
        # print(record)
        if record.get("record_type") == DltRecordType.LOG:
            name_contents = ["dlt", ]
            level = LOG_LEVEL_MAPPING.get(record.get("log_level"))
            if level is None:
                level = logging.INFO
            msg = record.get("payload_text").strip()
            if msg is not None:
                keys_for_name = ["ecuid", "sessionid", "applicationid", "contextid"]
                name_contents.extend(
                    [value for key, value in record.items() if (key in keys_for_name and value is not None)])
                name = ".".join(name_contents)
                keys_for_extra = ["timestamp", ]
                extra = {key: val for key, val in record.items() if key in keys_for_extra}
                logger = logging.getLogger(name=name)
                logger.log(level=level, msg=msg, extra=extra)

    @abstractmethod
    def recv(self) -> bytes:
        pass

    @abstractmethod
    def init_receiver(self, *args, **kwargs) -> None:
        pass


class SerialDltStreamLogAdapter(DltStreamLogAdapterABC):
    """
    A handler for a dlt stream on a serial port.
    """

    def recv(self) -> bytes:
        """
        Data receive function. Called from handle_rx.

        :return: The bytes received.
        """
        buffer = bytearray()
        data = self.receiver.read(1)
        if data:
            buffer.extend(data)
            buffer.extend(self.receiver.read(self.receiver.inWaiting()))
        return buffer

    def init_receiver(self, *args, **kwargs) -> None:
        ser = kwargs.get("ser")
        if ser is None:
            raise ValueError("Need ser keyword variable")
        self.receiver = ser


class SocketDltStreamLogAdapter(DltStreamLogAdapterABC):
    """
    A handler for a dlt stream on a socket.
    """

    def recv(self) -> bytes:
        """
        Data receive function. Called from handle_rx.

        :return: The bytes received.
        """
        return self.receiver.recv(DEFAULT_BUFFER_SIZE)

    def init_receiver(self, *args, **kwargs) -> None:
        """
        Initialize the receiver object.

        :return: Nothing.
        """
        host = kwargs.get("host")
        port = kwargs.get("port")
        if host is None:
            raise ValueError("Need host variable")
        if port is None:
            raise ValueError("Need port variable")
        self.receiver = socket(AF_INET, SOCK_STREAM)
        self.receiver.settimeout(1)
        self.receiver.connect((host, port))
