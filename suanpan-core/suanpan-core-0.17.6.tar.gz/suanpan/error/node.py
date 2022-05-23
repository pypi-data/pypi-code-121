# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.error import base


class NodeError(base.Error):
    MESSAGE = "Suanpan Node Error: {}"


class NodeAutoLoadError(NodeError):
    MESSAGE = "Suanpan Node Auto Load Error: {}"


class NodeAutoLoadUnsupportedDataSubtypeError(NodeError):
    MESSAGE = "Suanpan Node Auto Load Unsupported Data Subtype: {}"


class NodeAutoLoadUnsupportedParamTypeError(NodeError):
    MESSAGE = "Suanpan Node Auto Load Unsupported Param Type: {}"
