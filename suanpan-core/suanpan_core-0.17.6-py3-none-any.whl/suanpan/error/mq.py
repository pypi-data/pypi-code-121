# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.error import base


class MQError(base.Error):
    MESSAGE = "Suanpan MQ Error: {}"
