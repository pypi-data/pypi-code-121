import asynchat
import socket
from threading import RLock
from typing import Optional

from kamzik3.constants import *
from kamzik3.devices.device import Device
from kamzik3.snippets.snippetsControlLoops import control_asyncore_loop


class DeviceSocket(asynchat.async_chat, Device):
    terminator: Optional[bytes] = b"\r\n"
    ac_in_buffer_size = 4096
    ac_out_buffer_size = 4096
    host = None
    port = None

    def __init__(self, host, port, device_id=None, config=None):
        Device.__init__(self, device_id, config)
        self.asyncore_loop = control_asyncore_loop
        self.host = host
        self.port = port
        self.send_lock = RLock()
        asynchat.async_chat.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(False)
        self.buffer = []
        self.connect((host, port))

    def connect(self, address):
        try:
            asynchat.async_chat.connect(self, address)
            self.device_connection_poller.add_connecting_device(self)
        except socket.error:
            # Socket could not be connected. Non fatal error.
            # We don't want to reconnect immediately but rather wait for connection timeout.
            # Set devices as connecting, add it to device poller and wait until connection timeout.
            self.logger.exception("Socket creation exception")
            self.connecting = True
            self.device_connection_poller.add_connecting_device(self)
            # FIXME: Why is this a duplicate? Is socket.error the same as OSError?
        except (OverflowError, TypeError, OSError):
            self.logger.exception("Socket creation exception")
            self.close()

    def initiate_send(self):
        try:
            with self.send_lock:
                asynchat.async_chat.initiate_send(self)
        except IndexError:
            # Sending queue is already empty
            # Ignore this error
            self.logger.error("Send buffer is already empty")

    def collect_incoming_data(self, data: bytes) -> None:
        self.buffer.append(data.decode("utf-8"))

    def found_terminator(self):
        self.handle_readout(self.buffer)
        self.buffer = []

    def handle_connect(self):
        Device.handle_connect(self)

    def handle_connect_event(self):
        try:
            asynchat.async_chat.handle_connect_event(self)
            self.handle_configuration_event()
        except socket.error:
            self.logger.exception("Socket creation exception")
            self.close()

    def close_connection(self):
        self.stop_polling()
        return self.close()

    def close(self):
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            asynchat.async_chat.close(self)
        except OSError:
            pass
        self.set_status(STATUS_DISCONNECTED)

    def handle_expt_event(self):
        self.logger.error("Socket error")
        self.connection_error = True
        asynchat.async_chat.handle_expt_event(self)

    def handle_error(self):
        self.logger.exception("Uncaught exception")
        self.handle_response_error()

    def handle_configuration(self):
        raise NotImplementedError("Must be implemented in subclass")
