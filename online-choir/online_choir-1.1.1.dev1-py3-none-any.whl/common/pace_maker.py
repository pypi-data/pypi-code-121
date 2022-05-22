import asyncio
import time


class PaceMaker:
    def __init__(self, interval: float, init_burst: int = 0):
        self.interval = interval
        self.burst = init_burst
        self._last = 0

    def pace(self):
        if self.burst:
            self.burst -= 1
            return
        cur = time.time()
        delta = cur - self._last
        if delta < self.interval:
            time.sleep(self.interval - delta)
        self._last = max(cur, self._last + self.interval)

    async def apace(self):
        if self.burst:
            self.burst -= 1
            return
        cur = time.time()
        delta = cur - self._last
        if delta < self.interval:
            await asyncio.sleep(self.interval - delta)
        self._last = max(cur, self._last + self.interval)
