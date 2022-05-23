# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.proxy import Proxy


class ProxyArg(Proxy):
    TYPE_KEY = "argtype"


class AutoArg(ProxyArg):
    DEFAULT_TYPE = "params"
