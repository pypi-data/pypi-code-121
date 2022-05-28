# discord.ext.ipc - server
from websockets.server import WebSocketServerProtocol
from inspect import iscoroutine

try:
    from orjson import loads, dumps
except ImportError:
    from json import loads, dumps
    
    
class AsyncError(Exception):
    pass


def listen(name: str):
    def decorator(function):
        if iscoroutine(function):
            raise AsyncError("This function is not async")
        function._listen = name
        return function
    return decorator


class WebsocketMeta(type):
    def __new__(cls, name, base, dct, **kwargs):
        for name, func in dct.items():
            if hasattr(dct, "_listen"):
                dct["events"].append(func)
        return super().__new__(cls, name, base, dct)


class Websocket(metaclass=WebsocketMeta):
    events: list
    ws: WebSocketServerProtocol

    def print(self, content: str) -> None:
        """This can print like sanic

        Args:
            content (str): content
        """
        print("[ipc.Server]: {}".format(content))

    def __new__(cls, ws: WebSocketServerProtocol):
        self = super().__new__(cls)
        self.ws = ws
        self.print("Connected")
        return self.recv(ws)

    def dispatch(self, eventname: str, *args):
        if eventname in self.events:
            for coro in self.events[eventname]:
                self.loop.create_task(coro(*args))

    async def close(self, code: int = 1000, message: str = "Bye") -> None:
        """Close from ipc client

        Raises:
            ConnectionError: If you already close, it will be raise.

        Examples:
            await ipc_client.close()
        """
        if self.ws is not None:
            if not self.ws.closed:
                await self.ws.close(code=code, message=dumps({"type": "close", "message": message}))
                await self.ws.wait_closed()
                self.print("close")
            self.ws = None
        else:
            raise ConnectionError("Already closed")

    async def request(self, eventname: str, data: dict):
        """Send something to ipc client

        Args:
            eventtype (str): event type
            data (dict): The data you want to send.

        Examples:
            await ipc_client.request("hello", {"message": "What your name"})
        """
        payload = {
            "type": eventname,
            "data": data
        }
        await self.ws.send(dumps(payload))

    async def recv(self, ws: WebSocketServerProtocol):
        while ws.open:
            data = loads(await ws.recv())
            self.dispatch(data["type"], data["data"])
