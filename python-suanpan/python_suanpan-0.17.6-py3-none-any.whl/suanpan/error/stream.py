# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.error import base


class StreamError(base.Error):
    MESSAGE = "Suanpan Stream Error: {}"


class StreamUnknownHandlerError(StreamError):
    MESSAGE = "Suanpan Stream Unknown Handler Error: {}"


class StreamUnknownHandlerClassError(StreamError):
    MESSAGE = "Suanpan Stream Unknown Handler Class Error: {}"


class StreamInvalidHandlerError(StreamError):
    MESSAGE = "Suanpan Stream Invalid Handler Error: {}"


class StreamHandlerExistsError(StreamError):
    MESSAGE = "Suanpan Stream Handler Exists Error: {}"


class StreamSIOError(StreamError):
    MESSAGE = "Suanpan Stream SIO Error: {}"
