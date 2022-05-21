import time
import threading
from . import Cache


class MemoryCache(Cache):
    def __init__(self, autocleanup=True):
        self.cache = {}
        self.lock = threading.RLock()

        if autocleanup:
            def cleanup_loop():
                while True:
                    self.cleanup()
                    time.sleep(5)

            self.cleanup_thread = threading.Thread(target=cleanup_loop)
            self.cleanup_thread.start()

    def get(self, key):
        self.lock.acquire()
        value, ttl = self.cache.get(key, (None, None))
        self.lock.release()

        if ttl and ttl < int(time.time()):
            return None

        return value

    def set(self, key, value, ttl=None):
        exp = None

        if ttl is not None:
            exp = int(time.time()) + ttl

        self.lock.acquire()
        self.cache[key] = (value, exp)
        self.lock.release()

    def incr(self, key, amount=1):
        now = int(time.time())
        self.lock.acquire()

        if key in self.cache:
            self.cache[key] = (self.cache[key][0] + amount, self.cache[key][1])
        else:
            self.cache[key] = (amount, None)

        self.lock.release()

    def cleanup(self):
        now = int(time.time())

        self.lock.acquire()

        for key, (_, exp) in list(self.cache.items()):
            if exp and exp < now:
                del self.cache[key]

        self.lock.release()
