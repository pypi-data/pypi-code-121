# -*- coding: utf-8 -*-

import sys
import requests
import threading
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.packages import urllib3


timeout = 60


def get_session(*, retries):
    session = requests.Session()
    if urllib3.__version__ >= "1.26":
        allowed_methods = "allowed_methods"
    else:
        allowed_methods = "method_whitelist"
    retry_strategy = Retry(
        total=retries,
        status_forcelist=[413, 429, 500, 503, 504],
        backoff_factor=1,
        **{allowed_methods: ["HEAD", "OPTIONS", "GET", "POST"]},
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


__seen_warnings__ = set()
__warnings_lock__ = threading.Lock()


def print_tuxsuite_warnings(f):
    def wrapper(*args, **kwargs):
        response = f(*args, **kwargs)
        for header, warning in response.headers.items():
            if header.lower().startswith("x-tuxsuite-warning-"):
                if warning in __seen_warnings__:
                    continue
                with __warnings_lock__:
                    if warning not in __seen_warnings__:
                        print(f"WARNING: {warning}", file=sys.stderr)
                        __seen_warnings__.add(warning)
        return response

    return wrapper


@print_tuxsuite_warnings
def get(*args, **kwargs):
    session = get_session(retries=8)
    return session.get(*args, timeout=timeout, **kwargs)


@print_tuxsuite_warnings
def post(*args, **kwargs):
    session = get_session(retries=3)
    return session.post(*args, timeout=timeout, **kwargs)
