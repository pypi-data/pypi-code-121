import queue
from threading import Lock
class Q:
    def __init__(self, maxSize=100):
        self._list = queue.Queue(maxSize)
        self._lock = Lock()

    def push(self, value):
        self._lock.acquire()
        if not self._list.full():
            self._list.put(value)
        self._lock.release()

    def pop(self):
        self._lock.acquire()
        if not self._list.empty():
            return self._list.get()
        self._lock.release()

    def getQSize(self):
        return self._list.qsize()
