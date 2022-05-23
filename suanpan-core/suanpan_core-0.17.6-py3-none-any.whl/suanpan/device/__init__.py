# coding=utf-8
from __future__ import absolute_import, print_function

import functools

from suanpan import g
from suanpan.proxy import Proxy


class Device(Proxy):
    MAPPING = {
        "zmq": "suanpan.device.zmq.ZMQDevice",
    }
