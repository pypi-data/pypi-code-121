# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan import g
from suanpan.api import requests
from suanpan.api.hardware import app, suanpan
from suanpan.utils import functional


class Hardware(object):
    def __init__(self, host, tls=False):
        super().__init__()
        self.host = host
        self.request = Request(self.host, tls=tls)

    @functional.lazyproperty
    def suanpan(self):
        return suanpan.Interface(self.request)

    @functional.lazyproperty
    def apps(self):
        return app.Interface(self.request)


class Request(object):
    def __init__(self, host, tls=False):
        super().__init__()
        self.host = host
        self.tls = tls

    def getUrl(self, path):
        protocol = "https" if self.tls else "http"
        return f"{protocol}://{self.host}{path}"

    def get(self, path, *args, **kwargs):
        return requests.get(self.getUrl(path), *args, **kwargs)

    def post(self, path, *args, **kwargs):
        return requests.post(self.getUrl(path), *args, **kwargs)

    def put(self, path, *args, **kwargs):
        return requests.put(self.getUrl(path), *args, **kwargs)

    def delete(self, path, *args, **kwargs):
        return requests.delete(self.getUrl(path), *args, **kwargs)
