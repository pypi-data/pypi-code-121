# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.mstorage import vars


class Variables(vars.Variables):
    VARS_EXPIRE = 60

    def __init__(self, context, mstorage):
        super().__init__(mstorage)
        self.context = context

    def _getFullKey(self, key):
        return f"{self.context.message['id']}.{key}"

    def _getOriginKey(self, fullKey):
        prefixLen = len(self.context.message["id"]) + 1
        return fullKey[prefixLen:]

    def _getRegisterKey(self):
        return f"{self.context.message['id']}.vars"
