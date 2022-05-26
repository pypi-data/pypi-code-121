import asyncio
import random
from collections import deque
from typing import Any, Iterator

import item as item
from naff import ActiveVoiceState
from naff.api.voice.audio import BaseAudio

__all__ = ("NaffQueue",)


class NaffQueue:
    voice_state: ActiveVoiceState
    """The voice state this queue is playing for."""
    _entries: deque
    """The queue's base data store"""
    _item_queued: asyncio.Event
    """An event to be fired whenever an item is queued."""

    def __init__(self, voice_state: ActiveVoiceState):
        self.voice_state = voice_state

        self._entries = deque()
        self._item_queued = asyncio.Event()

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self) -> Iterator[BaseAudio]:
        return iter(self._entries)

    def put(self, audio: BaseAudio) -> None:
        """
        Enqueue audio at the end of the queue.

        Args:
            audio: The audio to enqueue
        """
        self._entries.append(audio)
        self._item_queued.set()

    def put_first(self, audio: BaseAudio) -> None:
        """
        Enqueue Audio to be played next.

        Args:
            audio: The audio to enqueue
        """
        self._entries.appendleft(audio)
        self._item_queued.set()

    async def pop(self) -> BaseAudio:
        """
        Pop the next item from the queue.

        Will wait if there are no items in the queue.
        """
        if len(self) == 0:
            # wait for an item to be enqueued
            await self._item_queued.wait()
        item = self._entries.popleft()
        self._item_queued.clear()
        return item

    def pop_no_wait(self) -> BaseAudio:
        """Pop from the queue without waiting."""
        return self._entries.popleft()

    def shuffle(self) -> None:
        """Shuffle the queue."""
        random.shuffle(self._entries)

    def clear(self) -> None:
        """Clear the queue."""
        self._entries.clear()

    def peek(self, positions: int = 1) -> BaseAudio | None:
        """
        Peek ahead `position` in the queue.

        Args:
            positions: How many positions ahead to peek at.

        Returns:
            BaseAudio if anything at the given position
        """
        try:
            return self._entries[positions - 1]
        except IndexError:
            return None

    def peek_at_index(self, index: int) -> BaseAudio:
        """
        Peek at a specific Index

        Args:
            index: The index to peek at

        Returns:
            BaseAudio at given index
        """
        return self._entries[index]

    async def __playback_queue(self) -> None:
        """The queue task itself. While the vc is connected, it will play through the enqueued audio"""
        while self.voice_state.connected:
            if self.voice_state.playing:
                await self.voice_state.wait_for_stopped()
            audio = await self.pop()
            await self.voice_state.play(audio)

    async def __call__(self) -> None:
        await self.__playback_queue()

    def start(self) -> None:
        """Create a background Queue task"""
        asyncio.create_task(self())
