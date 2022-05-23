# coding=utf-8
from __future__ import absolute_import, print_function

import zmq

from suanpan.device.base import BaseDevice


class ZMQDevice(BaseDevice):
    def __init__(self, *args, **kwargs):
        self._context = None
        self._socket = None
        super().__init__(*args, **kwargs)

    def connect(self):
        self._context = zmq.Context.instance()
        self._socket = self._context.socket(zmq.DEALER)  # pylint: disable=no-member
        self._socket.setsockopt(zmq.IDENTITY, self.name.encode())  # pylint: disable=no-member
        self._socket.connect(self.url)
        return self._socket

    def close(self):
        if self._context:
            self._context.term()
        if self._socket:
            self._socket.close()

    def _send(self, data, target):
        self._socket.send_multipart([data, target])

    def _recv(self):
        return self._socket.recv_multipart()
