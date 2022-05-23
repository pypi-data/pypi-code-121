# coding=utf-8
from __future__ import absolute_import, print_function

import requests

from suanpan import error
from suanpan.api import auth as apiauth


def session(auth=True):
    sess = requests.Session()
    if auth:
        sess.headers.update(apiauth.defaultHeaders())
    return sess


def request(method, url, *args, **kwargs):
    sess = session(auth=kwargs.get("auth", True))
    func = getattr(sess, method)
    rep = func(url, *args, **kwargs)
    rep.raise_for_status()
    result = rep.json()
    if not result.get("success", True):
        raise error.ApiError(f"Request failed {result}")
    return result


def get(url, *args, **kwargs):
    return request("get", url, *args, **kwargs)


def post(url, *args, **kwargs):
    return request("post", url, *args, **kwargs)


def put(url, *args, **kwargs):
    return request("put", url, *args, **kwargs)


def delete(url, *args, **kwargs):
    return request("delete", url, *args, **kwargs)
