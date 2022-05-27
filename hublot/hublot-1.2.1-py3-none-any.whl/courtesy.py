#!/usr/bin/env python3

# standards
from contextlib import contextmanager
from datetime import timedelta
from time import sleep, time
from typing import Dict, Optional
from urllib.parse import urlparse

# 3rd parties
from requests import PreparedRequest

# hublot
from .logs import LogEntry


class CourtesySleep:

    def __init__(self, courtesy_sleep: Optional[timedelta]):
        if courtesy_sleep is None:
            courtesy_sleep = timedelta(0)
        self.courtesy_sleep = courtesy_sleep
        self.last_request_per_host: Dict[str, float] = {}

    @contextmanager
    def __call__(self, preq: PreparedRequest, log: LogEntry, courtesy_sleep: Optional[timedelta] = None):
        if courtesy_sleep is None:
            courtesy_sleep = self.courtesy_sleep
        host = str(urlparse(preq.url).hostname)
        last_request = self.last_request_per_host.get(host, 0)
        delay_seconds = (last_request + courtesy_sleep.total_seconds()) - time()
        if delay_seconds > 0:
            log.courtesy_seconds = delay_seconds
            sleep(delay_seconds)
        try:
            yield
        finally:
            # NB we store the time after the request is complete
            self.last_request_per_host[host] = time()
