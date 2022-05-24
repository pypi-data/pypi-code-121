import time
import functools
from collections import abc
from fake_useragent import FakeUserAgent

from .exceptions import RetryMaxCountDone


def set_user_agent(header, user_agent_name):
    header = header or {}
    fagent = FakeUserAgent()
    header['User-Agent'] = getattr(fagent, user_agent_name)
    return header


def retry(func):
    @functools.wraps(func)
    def wrapper(self, url, **kwargs):
        if isinstance(self.RETRY_INTERVAL_SECONDS, abc.Iterable):
            retry_seconds = list(self.RETRY_INTERVAL_SECONDS)
        elif isinstance(self.RETRY_INTERVAL_SECONDS, (int, float,)):
            retry_seconds = [self.RETRY_INTERVAL_SECONDS]
        elif not hasattr(self, 'RETRY_INTERVAL_SECONDS'):
            retry_seconds = []
        else:
            raise ValueError(f'RETRY_INTERVAL_SECONDS must be integer float or iterables not {self.RETRY_INTERVAL_SECONDS}')

        retry_proxies = list(self.proxies_list) or [None]

        for i, sec in enumerate(retry_seconds):
            for proxies in retry_proxies:
                try:
                    r = func(self, url, **kwargs)
                except Exception as e: 
                    print(f"Exception: {e.__class__.__name__}")
                    print(f" - {e.args[0]}")
                    if proxies:
                        if (next_proxies := self.rotate_proxies()) != proxies:
                            print(f" - The requests by pass proxy server {proxies} has failed. Trying to next proxy server {next_proxies}")
                            time.sleep(1)
                else:
                    return r
            print(f" - Request {url} Failed, retry after {sec}sec(trys: {i+1})")
            time.sleep(sec)
        else:
            raise RetryMaxCountDone(f'Request {url} Failed!')
    return wrapper
