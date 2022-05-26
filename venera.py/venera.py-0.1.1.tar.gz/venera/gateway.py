import asyncio
import json

import aiohttp
from typing import TYPE_CHECKING

from .message import Message
from .channel import BaseChannel, TextChannel, Category

if TYPE_CHECKING:
    from .client import Client

class Gateway:
    def __init__(self, token: str, intents: int, client: "Client"):
        self._token = token
        self._client = client
        self._intents = intents

    async def start(self):
        self._session = aiohttp.ClientSession()

        self._ws = await self._session.ws_connect('wss://gateway.concord.chat')

        await self._ws.send_str(json.dumps({
            'token': self._token,
            'intents': self._intents
        }))
        loop = asyncio.get_running_loop()
        loop.create_task(self.recv())

    async def recv(self):
        async for msg in self._ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                data: dict = json.loads(msg.data)
                if data.get('t'):
                    await self.handle_event(data['t'], data)
            if msg.type == aiohttp.WSMsgType.CLOSE:
                # TODO: Handle
                ...

    async def handle_event(self, t: str, data: dict):
        d: dict = data['d']

        if t.startswith('MESSAGE'):
            channel = self._client._cache.messages.get(int(d['channel']['id']))

            if channel is None:
                channel = self._client._cache.messages[int(d['channel']['id'])] = {}

            if d['channel']['type'] == 1:
                d['channel'] = TextChannel(self._client, **d['channel'])

        if t == 'MESSAGE_CREATE':
            msg = Message(self._client, **d)
            channel[msg.id] = {int(d['id']): msg}
            await self._client._dispatch('MESSAGE_CREATE', msg)

        elif t == 'MESSAGE_EDIT':
            channel[int(d['id'])] = Message(self._client, **d)
            await self._client._dispatch('MESSAGE_EDIT', channel[int(d['id'])])

        elif t == 'MESSAGE_DELETE':
            channel.pop(int(d['id']))
            await self._client._dispatch('MESSAGE_DELETE')

        elif t == 'CHANNEL_CREATE':
            if d['type'] == 0:
                channel = Category(self._client, **d)
            if d['type'] == 1:
                channel = TextChannel(self._client, **d)
            else:
                channel = BaseChannel(self._client, **d)

            self._client._cache.channels[channel.id] = channel
