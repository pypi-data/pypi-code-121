# discord.ext.ipc - client
from websockets.client import WebSocketClientProtocol
from .errors import ConnectionError, AsyncError
from .items import ResponseItem
from inspect import iscoroutine
from websockets import connect
from discord import Client
from typing import Optional
import asyncio

try:
    from orjson import dumps, loads
except ImportError:
    from json import dumps, loads


class Client:
    """ipc client

    Args:
        client (discord.Client): Discord client
        secret_key (str): secret key
        loop (Optional[asyncio.AbstractEventLoop]): Event loop
        log (Optional[bool]): show log
    """

    def __init__(self, client: Client,
                 secret_key: str, *,
                 loop: Optional[asyncio.AbstractEventLoop] = None,
                 log: Optional[bool] = False):
        self.client = client
        self.secret_key = secret_key
        self.loop = loop
        self.log: bool = log
        self.ws: WebSocketClientProtocol = None
        self.events: list = []
        self.uri: str = None

    def print(self, content: str) -> None:
        """This can print like sanic

        Args:
            content (str): content
        """
        if self.log:
            print("[ipc.Client]: {}".format(content))

    async def __aenter__(self):
        if self.loop is None:
            self.loop = asyncio.get_running_loop()

    async def __aexit__(self, *args):
        try:
            await self.close()
        except Exception:
            pass

    async def connect(self, uri: str, *, reconnect: Optional[bool]=True) -> None:
        """Connect to ipc server

        Args:
            uri (str): URI
            reconnect (Optional[bool]): Reconnect when it was closed.

        Examples:
            await ipc_client.connect("ws://localhost/ipc")

        Raises:
            ConnectionError: If you already connect, it will be raise.
        """
        self.uri = uri
        if self.ws is not None:
            raise ConnectionError("Already connected")
        self.ws = await connect(uri)
        self.print("Connected")
        self.client.dispatch("ipc_connect")
        await self.login()
        while self.ws.open:
            await self.recv()
        if reconnect:
            await self.connect(uri, reconnect=reconnect)

    async def close(self, code: Optional[int] = 1000, message: Optional[str] = "Bye") -> None:
        """Close from ipc server
        
        Args:
            code (Optional[int]): Close code
            message (Optional[str]): Close message

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
                self.client.dispatch("ipc_close")
            self.ws = None
        else:
            raise ConnectionError("Already closed")

    async def reconnect(self) -> None:
        """Reconnect from ipc server

        Examples:
            await ipc_client.reconnect()
        """
        await self.close()
        await asyncio.sleep(0.5)
        await self.connect(self.uri)

    def login(self):
        """Login to ipc server

        Examples:
            await ipc_client.login()
        """
        return self.request("login", {"token": self.secret_key})

    async def request(self, eventtype: str, data: Optional[dict] = {}) -> None:
        """Send something to ipc server

        Args:
            eventtype (str): event type
            data (Optional[dict]): The data you want to send.

        Examples:
            await ipc_client.request("hello", {"message": "What your name"})
        """
        payload = {
            "type": eventtype,
            "data": data
        }
        await self.ws.send(dumps(payload))

    def listen(self, eventtype: str):
        """Catch data from ipc server

        Args:
            eventtype (str): Event type.
        """
        def decorator(func):
            if not iscoroutine(func):
                raise AsyncError("Function is not corotinue")
            if eventtype in self.events:
                self.events[eventtype].append(func)
            else:
                self.events[eventtype] = [func]
            return func
        return decorator

    def dispatch(self, eventtype: str, response: ResponseItem) -> None:
        """Run function
        
        Args:
            eventtype (str): Event type
            response (ResponseItem): response item
        """
        if eventtype in self.events:
            for coro in self.events[eventtype]:
                self.loop.create_task(coro())
        self.client.dispatch("ipc_{}".format(eventtype))

    async def recv(self) -> None:
        """Get data and dispatch
        """
        data = loads(await self.ws.recv())

        if data["type"] == "close":
            self.client.dispatch("ipc_close")

        self.dispatch(data["type"], data["data"])
