import asyncio
from typing import Dict

from ..common.audio_codecs import StereoDecoder, StereoEncoder
from ..common.constants import KEEPALIVE_INTERVAL, FrameType
from ..common.utils import my_assert


class AudioBroadcaster:
    def __init__(self):
        self.clients: Dict[str, asyncio.Queue] = {}
        self.last_sent = -1

    def register_client(self, client_id: str) -> int:
        my_assert(client_id not in self.clients, f"client {client_id} already registered")
        self.clients[client_id] = asyncio.Queue()
        return self.last_sent

    def unregister_client(self, client_id: str):
        del self.clients[client_id]

    def reset(self):
        for queue in self.clients.values():
            while not queue.empty():
                queue.get_nowait()
        self.last_sent = -1

    def add_input_frame(self, frame: bytes):
        for client_id, queue in self.clients.items():
            queue.put_nowait(frame)
        idx = StereoDecoder.peek_frame_index(frame)
        my_assert(idx == -1 or idx == self.last_sent + 1, "unexpected frame idx")
        self.last_sent = idx

    async def get_frame(self, client_id: str):
        """Gets the next frame to send. This is possibly a keepalive frame."""
        queue = self.clients[client_id]
        try:
            frame = await asyncio.wait_for(queue.get(), timeout=KEEPALIVE_INTERVAL)
        except asyncio.TimeoutError:
            frame = StereoEncoder.silence_frame(FrameType.KEEPALIVE)
        return frame
