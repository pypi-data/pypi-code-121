import asyncio
import signal

from coreauth.Authenticator import Authenticator

from data.payload.DataPayloadProcessor import DataPayloadProcessor
from data.websocket.DataWebSocket import DataWebSocket


class WebSocketRunner:

    def __init__(self, url, payload_processor: DataPayloadProcessor, ping_interval=20, authenticator: Authenticator = None):
        self.kill_now = False
        self.url = url
        self.payload_processor = payload_processor
        self.web_socket = DataWebSocket(self.url, ping_interval, authenticator)
        self.loop = asyncio.get_event_loop()
        self.running_loop = asyncio.get_running_loop()
        self.running_loop.add_signal_handler(signal.SIGTERM, self.terminate_gracefully)
        self.stopped_callback = None
        self.running_callback = None

    def fetch_single_payload(self):
        return self.loop.run_until_complete(self.__receive_single_payload())

    async def __receive_single_payload(self):
        async with self.web_socket as ws:
            return await ws.receive()

    def set_stopped_callback(self, stopped_callback):
        self.stopped_callback = stopped_callback

    def set_running_callback(self, running_callback):
        self.running_callback = running_callback

    def receive_data(self):
        asyncio.run(self.__receive_data())

    async def __receive_data(self):
        async with self.web_socket as ws:
            async for payload in ws:
                if self.kill_now is False:
                    self.payload_processor.process_payload(payload)
                    if self.running_callback is not None:
                        self.running_callback()

    def terminate_gracefully(self):
        self.kill_now = True
        self.running_loop.stop()
        if self.stopped_callback is not None:
            self.stopped_callback()
