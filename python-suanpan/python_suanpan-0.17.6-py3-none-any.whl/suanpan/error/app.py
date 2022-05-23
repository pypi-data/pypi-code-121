# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.error import base


class AppError(base.Error):
    MESSAGE = "Suanpan APP Error: {}"


class AppModuleError(AppError):
    MESSAGE = "Suanpan APP Module Error: {}"


class AppStorageModuleError(AppError):
    MESSAGE = "Suanpan APP Storage Module Error: {}"
