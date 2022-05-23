# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.error import base


class ImportError(base.Error):
    MESSAGE = "Suanpan Import Error: {}"
