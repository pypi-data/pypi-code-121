# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.error import base


class MStorageError(base.Error):
    MESSAGE = "Suanpan MStorage Error: {}"


class MStorageVarError(base.Error):
    MESSAGE = "Suanpan MStorage Var Error: {}"


class MStorageUnknownVarTypeError(base.Error):
    MESSAGE = "Suanpan MStorage Unknown Var Type: {}"


class MStorageUnregisterVarKeyError(base.Error):
    MESSAGE = "Suanpan MStorage Unregister Var Key: {}"


class MStorageVarHasRegisteredAsAnotherTypeError(base.Error):
    MESSAGE = "Suanpan MStorage Var Has Registered As Another Type: {}"
