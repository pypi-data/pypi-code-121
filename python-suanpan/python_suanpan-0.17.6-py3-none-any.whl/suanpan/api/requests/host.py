# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan import error, g
from suanpan.api import requests


def getHostUrl(path, tls=g.hostTls):
    if not g.host:
        raise error.ApiError("host not set")
    protocol = "https" if tls else "http"
    return f"{protocol}://{g.host}{path}"


def getApiHostUrl(appId, apiName, tls=g.hostApiTls):
    if not g.apiHost:
        raise error.ApiError("ApiHost not set")
    protocol = "https" if tls else "http"
    return f"{protocol}://{g.apiHost}/{appId}/{apiName}"


def get(path, *args, **kwargs):
    return requests.get(getHostUrl(path), *args, **kwargs)


def post(path, *args, **kwargs):
    return requests.post(getHostUrl(path), *args, **kwargs)


def put(path, *args, **kwargs):
    return requests.put(getHostUrl(path), *args, **kwargs)


def delete(path, *args, **kwargs):
    return requests.delete(getHostUrl(path), *args, **kwargs)


def call(appId, apiName, data, *args, **kwargs):
    kwargs.setdefault("auth", False)
    debug = kwargs.pop("debug", False)
    return requests.post(
        getApiHostUrl(appId, apiName),
        json={"data": data, "debug": debug},
        *args,
        **kwargs,
    )
