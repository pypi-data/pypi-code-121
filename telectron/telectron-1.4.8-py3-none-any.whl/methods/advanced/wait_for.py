import logging, asyncio, random

from telectron import filters
from telectron.scaffold import Scaffold

log = logging.getLogger(__name__)


class Waiting:
    def __init__(self, handler):
        self.handler = handler
        self.event = asyncio.Event()
        self.update = None
        self.lock = asyncio.Lock()


class WaitingResult:
    def __init__(self, id_, client):
        self.id = id_
        self.client = client

    def await_(self, timeout=10):
        return self.client.wait_for(self.id, timeout)


class WaitFor(Scaffold):
    async def register_waiting(
            self,
            handler
    ):
        for lock in self.dispatcher.locks_list:
            await lock.acquire()

        try:
            while True:
                waiting_id = random.randint(0, 65536)
                if waiting_id in self.dispatcher.waiting_events:
                    continue
                self.dispatcher.waiting_events[waiting_id] = Waiting(handler)
                break

        finally:
            for lock in self.dispatcher.locks_list:
                lock.release()

        return WaitingResult(waiting_id, self)

    async def wait_for(
        self,
        waiting_id,
        timeout=10
    ):
        try:
            await asyncio.wait_for(self.dispatcher.waiting_events[waiting_id].event.wait(), timeout)
            return self.dispatcher.waiting_events[waiting_id].update
        finally:
            for lock in self.dispatcher.locks_list:
                await lock.acquire()

            try:
                del self.dispatcher.waiting_events[waiting_id]

            finally:
                for lock in self.dispatcher.locks_list:
                    lock.release()
