import asyncio
import numpy as np
import queue
import sounddevice as sd
from typing import AsyncIterable, Tuple, Optional

from ..common.audio_devices import get_device_index
from ..common.constants import SAMPLING_RATE, FRAME_SIZE, SLAVE_PLAYBACK_BUFFER_SIZE, FrameType
from ..common.log import logger
from ..common.utils import iterate_queue, flush_queue, my_assert

DEFAULT_ERROR_BUDGET = 5  # number of sounddevice errors to forgive


class AudioIOStream:
    def __init__(self):
        self._input_queue = queue.Queue()
        self._output_queue = asyncio.Queue()
        self._loop = asyncio.get_event_loop()
        self.playing = False
        self._buffer_ready = asyncio.Event()
        self._failed = False
        self._errors_budget = 0

    def _callback(self, indata: np.ndarray, outdata: np.ndarray, frames: int, _, status):
        my_assert(frames == FRAME_SIZE, "wrong frame size")
        if status.output_underflow or status.output_overflow or status.input_overflow:
            logger.error(f"Audio callback error {status} (budget is {self._errors_budget})")
            self._errors_budget -= 1
        try:
            idx, next_chunk = self._input_queue.get_nowait()
        except queue.Empty:
            logger.debug("playback queue empty")
            idx, next_chunk = -2, 0
        outdata[:, :] = next_chunk
        if idx == -1:  # got poison pill
            raise sd.CallbackStop
        if not self._failed:  # record only if not failed
            if self._errors_budget == 0 or idx == -2:
                logger.warning(f"stop recording idx={idx} error budget={self._errors_budget}")
                self._failed = True
                self._put_item_to_output_queue((FrameType.ABORT, None))
                return
            self._put_item_to_output_queue((idx, indata[:, 0].copy()))

    def _finished_callback(self):
        self._put_item_to_output_queue(None)
        logger.debug("Finished callback")

    def _put_item_to_output_queue(self, item):
        self._loop.call_soon_threadsafe(self._output_queue.put_nowait, item)

    async def buffer_ready(self):
        await self._buffer_ready.wait()

    async def play_and_record(self, in_device: str, out_device: str, poll_interval_s: Optional[float] = None) \
            -> AsyncIterable[Tuple[int, np.array]]:
        """
        Plays the content of the input queue (containing data frames as numpy arrays, terminated by a None) as
        returns the corresponding recorded frames. The recorded frames have the same number as the input frames
        (excluding the termination None)
        """
        stream = sd.Stream(device=(get_device_index(in_device, False), get_device_index(out_device, True)),
                           samplerate=SAMPLING_RATE,
                           blocksize=FRAME_SIZE,
                           channels=(1, 2),
                           dtype="float32",
                           callback=self._callback,
                           finished_callback=self._finished_callback,
                           latency='high')
        flush_queue(self._output_queue)
        self._errors_budget = DEFAULT_ERROR_BUDGET
        self._failed = False
        self.playing = True
        with stream:
            async for item in iterate_queue(self._output_queue, poll_interval_s=poll_interval_s):
                if item is None:  # poll interval elapsed, send keep-alive packet
                    yield FrameType.KEEPALIVE, None
                else:
                    yield item
        self.playing = False

    def add_input_chunk(self, idx: int, chunk: np.array):
        assert chunk.shape == (FRAME_SIZE, 2)
        my_assert(idx >= 0, f"Got bad idx={idx}")
        self._input_queue.put_nowait((idx, chunk))
        if not self.playing and self._input_queue.qsize() >= SLAVE_PLAYBACK_BUFFER_SIZE:
            self._buffer_ready.set()

    def add_end_marker(self):
        self._input_queue.put_nowait((-1, None))
        self._buffer_ready.set()  # buffer is ready whenever the audio input is complete

    def flush_input(self):
        my_assert(not self.playing, "flushing while stream is on")
        flush_queue(self._input_queue)
        self._buffer_ready.clear()

    def backlog_size(self) -> int:
        return self._output_queue.qsize()
