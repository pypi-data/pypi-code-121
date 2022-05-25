# -*- coding: utf-8 -*-
# vim: set ts=4
#
# Copyright 2021-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from requests.adapters import HTTPAdapter
from requests.packages import urllib3
from requests.packages.urllib3.util.retry import Retry

import requests


timeout = 60


def get_session(*, retries):
    session = requests.Session()
    if urllib3.__version__ >= "1.26":
        allowed_methods = "allowed_methods"
    else:
        allowed_methods = "method_whitelist"  # pragma: no cover
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


def requests_get(*args, **kwargs):
    session = get_session(retries=8)
    return session.get(*args, timeout=timeout, **kwargs)
