import asyncio
import time


class Limiter():
    def __init__(self, min_time_ms, max_concurrent):
        self.min_time_ms = min_time_ms
        self.max_concurrent = max_concurrent
        self.last_request = 0
        self.open = 0


    async def acquire(self):
        while True:
            now = time.perf_counter()

            if ((now - self.last_request) >= (self.min_time_ms / 1000) and (self.open < self.max_concurrent)):
                self.last_request = now
                self.open += 1
                break

            await asyncio.sleep(0.01)

    def release(self):
        self.open -= 1
