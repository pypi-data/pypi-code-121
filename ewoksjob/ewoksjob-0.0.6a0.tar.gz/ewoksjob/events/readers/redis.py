import os
import json
import socket
from typing import Iterable
import redis
from .base import EwoksEventReader, EventType


class RedisEwoksEventReader(EwoksEventReader):
    def __init__(self, url: str):
        client_name = f"ewoks:reader:{socket.gethostname()}:{os.getpid()}"
        self._proxy = redis.Redis.from_url(url, client_name=client_name)

    def wait_events(self, **kwargs) -> Iterable[EventType]:
        yield from self.poll_events(**kwargs)

    def get_events(self, job_id=None, **filters) -> Iterable[EventType]:
        direct_filter, indirect_filter = self.split_filter(**filters)

        if job_id:
            pattern = f"ewoks:{job_id}:*"
        else:
            pattern = "ewoks:*"
        keys = sorted(
            self._proxy.scan_iter(pattern), key=lambda x: int(x.decode().split(":")[-1])
        )
        for key in keys:
            event = self._proxy.hgetall(key)
            event = {k.decode(): json.loads(v) for k, v in event.items()}
            if not self.match_indirect_filter(event, **indirect_filter) or any(
                event[k] != v for k, v in direct_filter.items()
            ):
                continue
            yield event
