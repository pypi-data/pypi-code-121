import socket

import rook.com_ws.socketpair_compat  # do not remove - adds socket.socketpair on Windows lgtm[py/unused-import]
from rook.com_ws import poll_select
from threading import Event


class SelectableEvent(object):
    """
    Uses a socketpair to signal when the event is ready. This way, it can be used in a select.
    """
    def __init__(self):
        self._event = Event()
        self._readsocket, self._writesocket = socket.socketpair()
        self._readwaiter = poll_select.Waiter([self._readsocket], [], [])

    def close(self):
        self._readsocket.close()
        self._writesocket.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def fileno(self):
        return self._readsocket.fileno()

    def is_set(self):
        return self._event.is_set()

    def set(self):
        if not self.is_set():
            self._event.set()
            self._writesocket.send(b'1')

    def wait(self, timeout=None):
        if self._event.is_set():
            return True
        rfds, _, _ = self._readwaiter.wait(timeout)
        if len(rfds) != 0 and self._event.is_set():
            return True

        return False
