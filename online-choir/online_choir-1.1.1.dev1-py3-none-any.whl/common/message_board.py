from threading import Event
from typing import Any, Tuple, Dict, Iterator


class MessageBoard:
    def __init__(self):
        self._event = Event()
        self._board = {}
        self._active = True

    def post_message(self, topic, content):
        self._board[topic] = content
        self._event.set()

    def post_messages(self, update: Dict):
        self._board.update(update)
        self._event.set()

    def close(self):
        self._active = False
        self._event.set()

    def _retrieve_message(self) -> Tuple[Any, Any]:
        topic, *_ = self._board
        content = self._board.pop(topic)
        return topic, content

    def get_message(self, timeout=None) -> Tuple[Any, Any]:
        while True:
            if self._board:
                return self._retrieve_message()
            ok = self._event.wait(timeout)
            if not ok:
                raise TimeoutError()
            self._event.clear()

    def messages(self, timeout=None) -> Iterator[Tuple[Any, Any]]:
        while self._active:
            while self._board:
                yield self._retrieve_message()
            ok = self._event.wait(timeout)
            if not ok:
                raise TimeoutError()
            self._event.clear()

    def flush_topic(self, topic):
        self._board.pop(topic, None)
