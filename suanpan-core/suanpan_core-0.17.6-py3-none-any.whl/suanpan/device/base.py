# coding=utf-8
from __future__ import absolute_import, print_function

import enum
import traceback

from suanpan import error, utils
from suanpan.log import logger
from suanpan.objects import Context
from suanpan.utils import json


@enum.unique
class SocketKeyword(enum.Enum):
    PING = "ping"
    PONG = "pong"


class BaseDevice(object):
    def __init__(self, name, url, **kwargs):
        self.name = name
        self.url = url
        self.current = Context(**kwargs)

        self.connect()

    def connect(self):
        raise NotImplementedError("Method not implemented!")

    def close(self):
        raise NotImplementedError("Method not implemented!")

    def send(self, data, target=None):
        target = target or self.current.message.get("from")
        if not target:
            raise error.DeviceError("No target specified")
        self._send(utils.encode(target), utils.encode(data))

    def sendBytes(self, data, target=None):
        self.send(data, target=target)

    def sendJson(self, data, target=None):
        self.send(json.dumps(data), target=target)

    def recv(self, decode=True):
        pongBytes = utils.encode(SocketKeyword.PONG)
        while True:
            _from, data = self._recv()
            if data == pongBytes:
                self.pong()
                continue

            _from = utils.decode(_from)
            if decode:
                data = data.decode()
            self.current.message = {"from": _from, "data": data}
            return data

    def recvBytes(self):
        return self.recv(decode=False)

    def recvJson(self):
        return json.loads(self.recv(decode=True))

    def request(self, data, target=None, decode=True):
        self.send(data, target)
        return self.recv(decode=decode)

    def requestBytes(self, data, target=None):
        self.sendBytes(data, target)
        return self.recvBytes()

    def requestJson(self, data, target=None):
        self.sendJson(data, target)
        return self.recvJson()

    def _subscribe(self, _recv, *args, **kwargs):
        while True:
            try:
                yield self.recv(*args, **kwargs)
            except Exception:  # pylint: disable=broad-except
                logger.warning("Error in subscribe messages:")
                logger.warning(traceback.format_exc())

    def subscribe(self, decode=True):
        yield from self._subscribe(self.recv, decode=decode)

    def subscribeBytes(self):
        yield from self._subscribe(self.recvBytes)

    def subscribeJson(self):
        yield from self._subscribe(self.recvJson)

    def ping(self, target):
        result = self.request(SocketKeyword.PING, target, decode=True)
        if result != SocketKeyword.PONG:
            raise error.DeviceError(f"Ping error: {result}")

    def pong(self):
        self.send(SocketKeyword.PONG)

    def _send(self, data, target):
        raise NotImplementedError("Method not implemented!")

    def _recv(self):
        raise NotImplementedError("Method not implemented!")
