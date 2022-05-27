"""A python module for very basic APIs of the free dweet service.

- Author: Quan Lin
- License: MIT
"""

__version__ = "0.1.0"
__all__ = ["BasicDweetError", "dweet_for", "get_latest_dweet_for", "get_dweets_for"]

import json

try:
    import urequests as requests
except ImportError:
    import requests

BASE_URL = "https://dweet.io"


class BasicDweetError(Exception):
    pass


def _request(method, url, **kwargs):
    url = BASE_URL + url

    request_func = getattr(requests, method)
    response = request_func(url, **kwargs)
    if not (200 <= response.status_code < 300):
        raise BasicDweetError(f"HTTP {response.status_code} response")
    response_json = response.json()
    if response_json["this"] == "failed":
        raise BasicDweetError(response_json["because"])
    return response_json["with"]


def dweet_for(thing_name, payload):
    """The `dweet for` API.

    Parameters
    ----------
    thing_name : str
        The name of the thing to dweet.
    payload : dict
        The content of the thing to dweet.
        It is passed to `json.dumps`. So a dict fits it the best.

    Returns
    -------
    dict
        The dweet transaction dict returned from dweet service.
        It should include the keys of 'thing', 'content', 'created' and 'transaction'.
    """
    data = json.dumps(payload)
    headers = {"Content-type": "application/json"}
    return _request(
        "post",
        f"/dweet/for/{thing_name}",
        data=data,
        headers=headers,
    )


def get_latest_dweet_for(thing_name):
    """The `get latest dweet for` API.

    Parameters
    ----------
    thing_name : str
        The name of the thing to dweet.

    Returns
    -------
    list
        The list of dweet transaction dicts.
        There is only the latest transaction dict in it.
    """
    return _request("get", f"/get/latest/dweet/for/{thing_name}")


def get_dweets_for(thing_name):
    """The `get dweets for` API.

    Parameters
    ----------
    thing_name : str
        The name of the thing to dweet.

    Returns
    -------
    list
        The list of dweet transaction dicts.
        There are at most 5 latest transaction dicts in it.
    """
    return _request("get", f"/get/dweets/for/{thing_name}")
