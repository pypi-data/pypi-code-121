import msgpack

from msgpackrpc.compat import force_str
from msgpackrpc import error
from msgpackrpc import Loop
from msgpackrpc import message
from msgpackrpc import session
from msgpackrpc.transport import tcp


class Server(session.Session):
    """\
    Server is useful for MessagePack RPC Server.
    """

    def __init__(self, dispatcher, loop=None, builder=tcp, *args, **kwargs):
        self._loop = loop or Loop()
        self._builder = builder
        self._listeners = []
        self._dispatcher = dispatcher

    def listen(self, address):
        listener = self._builder.ServerTransport(address)
        listener.listen(self)
        self._listeners.append(listener)

    def start(self):
        self._loop.start()

    def stop(self):
        self._loop.stop()

    def close(self):
        for listener in self._listeners:
            listener.close()

    async def on_request(self, sendable, msgid, method, param):
        await self.dispatch(method, param, _Responder(sendable, msgid))

    async def on_notify(self, method, param):
        await self.dispatch(method, param, _NullResponder())

    async def dispatch(self, method, param, responder):
        try:
            method = force_str(method)
            if not hasattr(self._dispatcher, method):
                raise error.NoMethodError("'{0}' method not found".format(method))

            result = getattr(self._dispatcher, method)(*param)
            if isinstance(result, AsyncResult):
                await result.set_responder(responder)
            else:
                await responder.set_result(result)
        except Exception as e:
            await responder.set_error(str(e))


class AsyncResult:
    def __init__(self):
        self._responder = None
        self._result = None

    async def set_result(self, value, error=None):
        if self._responder is not None:
            await self._responder.set_result(value, error)
        else:
            self._result = [value, error]

    async def set_error(self, error, value=None):
        await self.set_result(value, error)

    async def set_responder(self, responder):
        self._responder = responder
        if self._result is not None:
            await self._responder.set_result(*self._result)
            self._result = None


class _Responder:
    def __init__(self, sendable, msgid):
        self._sendable = sendable
        self._msgid = msgid
        self._sent = False

    async def set_result(self, value, error=None):
        if not self._sent:
            await self._sendable.send_message(
                [message.RESPONSE, self._msgid, error, value]
            )
            self._sent = True

    async def set_error(self, error, value=None):
        await self.set_result(value, error)


class _NullResponder:
    def set_result(self, value, error=None):
        pass

    def set_error(self, error, value=None):
        pass
