import threading

from six.moves.queue import Queue, Empty

from rook.com_ws.eventfd.eventfd import Semaphore as SemaphoreEventFD


MAX_QUEUE_SIZE = 2048


class SelectableQueue(object):
    """
    Uses a eventfd as a semaphore for reading and writing to the internal queue.
    This way, this queue can be used as a parameter to select() or poll().
    Maximum queue size is MAX_QUEUE_SIZE.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self._queue = Queue(maxsize=MAX_QUEUE_SIZE)
        self._event_fd = SemaphoreEventFD(blocking=False)

    def __del__(self):
        self._event_fd.close()

    def put(self, item):
        with self._lock:
            if self._queue.full():
                return

            self._event_fd.signal()

            self._queue.put_nowait(item)

    def get(self):
        if not self._event_fd.wait():
            raise Empty()

        with self._lock:
            return self._queue.get_nowait()

    def fileno(self):
        return self._event_fd.fileno()

    def qsize(self):
        return self._queue.qsize()
