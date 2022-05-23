# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan import objects
from suanpan.mstorage import mstorage
from suanpan.stream import vars


class Context(objects.Context):
    @property
    def vars(self):
        return vars.Variables(self, mstorage)
