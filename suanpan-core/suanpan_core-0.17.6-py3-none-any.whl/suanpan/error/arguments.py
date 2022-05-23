# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.error import base


class ArgumentError(base.Error):
    MESSAGE = "Argument Error: {}"


class ArgumentRequiredError(ArgumentError):
    MESSAGE = "Argument Required Error: {}"


class ArgumentTypeError(ArgumentError):
    MESSAGE = "Argument Type Error: {}"
