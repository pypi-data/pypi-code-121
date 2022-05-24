import logging

from coreauth.Authenticator import Authenticator
from websockets import connect


# todo: need to handle re-connect
class DataWebSocket:

    def __init__(self, url, ping_interval, authenticator: Authenticator):
        self.log = logging.getLogger(__name__)
        self.log.info(f'Web socket INITIALIZED with url:[{url}]')
        self.url = url
        self.ping_interval = ping_interval
        self.authenticator = authenticator
        self.shutdown_callback = None

    async def __aenter__(self):
        if self.authenticator is not None:
            await self.authenticator.authenticate()
            await self.update_url_after_authentication()
        self.log.info(f'Web socket CONNECTING to url:[{self.url}]')
        self._conn = connect(self.url, ping_interval=self.ping_interval)
        self.websocket = await self._conn.__aenter__()
        return self

    async def update_url_after_authentication(self):
        if self.authenticator.should_update_url():
            self.url = self.authenticator.update_url(self.url)

    async def __aexit__(self, *args, **kwargs):
        if self.authenticator is not None:
            await self.authenticator.terminate()
        self.log.info(f'Web socket DISCONNECTING from url:[{self.url}]')
        await self._conn.__aexit__(*args, **kwargs)

    def __aiter__(self):
        return self

    async def __anext__(self):
        payload = await self.receive()
        if payload:
            return payload
        else:
            raise StopAsyncIteration

    async def receive(self):
        # todo: design re-connect
        return await self.websocket.recv()
