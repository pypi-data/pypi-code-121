"""Generic deframing decoder."""
import asyncio
from typing import Callable, cast, Generic, Iterable, Optional, TypeVar

from attrs import define, field

__author__ = "Masen Furer KF7HVM <kf7hvm@0x26.net>"
__copyright__ = "Copyright 2022 Masen Furer and Contributors"
__license__ = "Apache License, Version 2.0"


# indicates that no more frames will appear on this protocol
EOF = object()

_T = TypeVar("_T")


@define
class GenericDecoder(Generic[_T]):
    """Generic stateful decoder."""

    @staticmethod
    def decode_frames(frame: bytes) -> Iterable[_T]:
        """
        Decode a single deframed byte chunk.

        :param frame: should represent a single higher level frame to
            decode in some way.
        """
        yield cast(_T, frame)

    def update(self, new_data: bytes) -> Iterable[_T]:
        """
        Decode the next sequence of bytes from the stream.

        :param new_data: the next bytes from the stream
        :return: an iterable of decoded frames
        """
        yield cast(_T, new_data)

    def flush(self) -> Iterable[_T]:
        """Call when the stream is closing to decode any final buffered bytes."""
        if None:
            yield
        return


@define
class FrameDecodeProtocol(asyncio.Protocol, Generic[_T]):
    """Protocol which uses a GenericDecoder to split the stream into frames."""

    transport: Optional[asyncio.Transport] = field(default=None)
    decoder: GenericDecoder[_T] = field(factory=GenericDecoder)
    callback: Optional[Callable[[_T], None]] = field(default=None)
    frames: asyncio.Queue = field(factory=asyncio.Queue, init=False)
    connection_future: asyncio.Future = field(
        factory=asyncio.Future,
        init=False,
    )

    def _queue_frame(self, frame: _T) -> None:
        self.frames.put_nowait(frame)
        if self.callback is not None:
            self.callback(frame)
        self.frame_decoded(frame)

    def connection_made(self, transport: asyncio.Transport) -> None:
        """
        asyncio callback when connection is established.

        Because this protocol exposes higher-level read/write operations that
        require the transport, an awaitable `connection_future` is completed for consumers
        who depend on an active connection.
        """
        self.transport = transport
        self.connection_future.set_result(transport)

    def frame_decoded(self, frame: _T) -> None:
        """Subclasses may override this function to handle new frame."""
        pass

    def data_received(self, data: bytes) -> None:
        """Pass data off to decoder instance and put frames on the queue."""
        for frame in self.decoder.update(data):
            self._queue_frame(frame)

    def connection_lost(self, exc: Exception) -> None:
        """asyncio callback when connection is lost."""
        for frame in self.decoder.flush():
            self._queue_frame(frame)
        self.frames.put_nowait(EOF)

    async def read(self, n_frames=None) -> Iterable[_T]:
        """
        Iterate through decoded frames.

        If n_frames is specified, exit after yielding that number of frames.
        """
        if n_frames is None:
            n_frames = -1
        transport = await self.connection_future
        while (not transport.is_closing() or not self.frames.empty()) and n_frames:
            frame = await self.frames.get()
            if frame is EOF:
                break
            yield frame
            n_frames -= 1

    def read_frames(
        self,
        n_frames: Optional[int],
        loop: Optional[asyncio.BaseEventLoop] = None,
    ) -> Iterable[_T]:
        """Blocking read of the given number of frames."""
        if loop is None:
            loop = asyncio.get_event_loop()

        if n_frames is not None and n_frames < 0:
            n_frames = self.frames.qsize()

        async def _():
            return [f async for f in self.read(n_frames)]

        return loop.run_until_complete(_())
