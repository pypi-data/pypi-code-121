import os, sys

sys.path.append(os.path.dirname(os.path.pardir))

import msgpack
from tornado import tcpserver
from tornado.iostream import IOStream, StreamClosedError

import msgpackrpc.message
from msgpackrpc.error import RPCError, TransportError

from asyncio import Task

MAX_BYTES = 104857600
READ_CHUNK_SIZE = 65536


class BaseSocket(object):
    def __init__(self, stream):
        self._stream = stream
        self._packer = msgpack.Packer(default=lambda x: x.to_msgpack())
        self._unpacker = msgpack.Unpacker()

    def close(self):
        self._stream.close()

    def closed(self):
        return self._stream.closed()

    async def send_message(self, message):
        await self._stream.write(self._packer.pack(message))

    async def start_read(self, silent_errors=False):
        try:
            while True:
                data = await self._stream.read_bytes(MAX_BYTES, partial=True)
                await self.on_read(data)
        except StreamClosedError:
            if not silent_errors:
                raise RPCError("Stream is closed.")

    async def on_read(self, data):
        if data:
            self._unpacker.feed(data)
            for message in self._unpacker:
                await self.on_message(message)

    async def on_message(self, message):
        msgsize = len(message)
        if msgsize != 4 and msgsize != 3:
            raise RPCError(
                "Invalid MessagePack-RPC protocol: message = {0}".format(message)
            )

        msgtype = message[0]
        if msgtype == msgpackrpc.message.REQUEST:
            await self.on_request(message[1], message[2], message[3])
        elif msgtype == msgpackrpc.message.RESPONSE:
            self.on_response(message[1], message[2], message[3])
        elif msgtype == msgpackrpc.message.NOTIFY:
            await self.on_notify(message[1], message[2])
        else:
            raise RPCError("Unknown message type: type = {0}".format(msgtype))

    def on_request(self, msgid, method, param):
        raise NotImplementedError("on_request not implemented")

    def on_response(self, msgid, error, result):
        raise NotImplementedError("on_response not implemented")

    def on_notify(self, method, param):
        raise NotImplementedError("on_notify not implemented")


class ClientSocket(BaseSocket):
    def __init__(self, stream, transport):
        BaseSocket.__init__(self, stream)
        self._transport = transport
        self._stream.set_close_callback(self.on_close)

    async def connect(self):
        try:
            await self._stream.connect(self._transport._address.unpack())
            await self.on_connect()
        except Exception as e:
            await self.on_connect_failed()

    async def on_connect(self):
        await self._transport.on_connect(self)
        await self.start_read()

    async def on_connect_failed(self):
        await self._transport.on_connect_failed(self)

    async def on_close(self):
        await self._transport.on_close(self)

    def on_response(self, msgid, error, result):
        self._transport._session.on_response(msgid, error, result)


class ClientTransport(object):
    def __init__(self, session, address, reconnect_limit):
        self._session = session
        self._address = address
        self._reconnect_limit = reconnect_limit

        self._connecting = 0
        self._connecting_event = None
        self._pending = []
        self._sockets = []
        self._closed = False

    async def send_message(self, message):
        if len(self._sockets) == 0:
            self._pending.append(message)
            if self._connecting == 0:
                self._connecting = 1
                await self.connect()
        else:
            sock = self._sockets[0]
            await sock.send_message(message)

    async def connect(self):
        stream = IOStream(self._address.socket())
        socket = ClientSocket(stream, self)
        await socket.connect()

    def close(self):
        for sock in self._sockets:
            sock.close()

        self._connecting = 0
        self._pending = []
        self._sockets = []
        self._closed = True

    async def on_connect(self, sock):
        self._sockets.append(sock)
        for pending in self._pending:
            await sock.send_message(pending)
        self._pending = []

    async def on_connect_failed(self, sock):
        if self._connecting < self._reconnect_limit:
            self._connecting += 1
            await self.connect()
        else:
            self._connecting = 0
            self._pending = []
            self._session.on_connect_failed(
                TransportError("Retry connection over the limit")
            )

    async def on_close(self, sock):
        # Avoid calling self.on_connect_failed after self.close called.
        if self._closed:
            return

        if sock in self._sockets:
            self._sockets.remove(sock)
        else:
            # Tornado does not have on_connect_failed event.
            await self.on_connect_failed(sock)


class ServerSocket(BaseSocket):
    def __init__(self, stream, transport):
        BaseSocket.__init__(self, stream)
        self._transport = transport
        Task(self.start_read(silent_errors=True))

    def on_close(self):
        self._transport.on_close(self)

    async def on_request(self, msgid, method, param):
        await self._transport._server.on_request(self, msgid, method, param)

    async def on_notify(self, method, param):
        await self._transport._server.on_notify(method, param)


class MessagePackServer(tcpserver.TCPServer):
    def __init__(self, transport):
        self._transport = transport
        tcpserver.TCPServer.__init__(self)

    def handle_stream(self, stream, address):
        ServerSocket(stream, self._transport)


class ServerTransport(object):
    def __init__(self, address):
        self._address = address

    def listen(self, server):
        self._server = server
        self._mp_server = MessagePackServer(self)
        self._mp_server.listen(self._address.port)

    def close(self):
        self._mp_server.stop()
