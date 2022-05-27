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
