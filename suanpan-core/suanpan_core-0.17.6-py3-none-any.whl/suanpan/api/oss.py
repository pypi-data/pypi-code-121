# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.api.requests import affinity


def getAccessKey():
    return affinity.get("/oss/ak")


def getToken():
    return affinity.get("/oss/token")
