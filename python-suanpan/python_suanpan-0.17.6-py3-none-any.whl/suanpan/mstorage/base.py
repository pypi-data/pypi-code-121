# coding=utf-8
from __future__ import absolute_import, print_function

import abc

from suanpan.mstorage.vars import Variables
from suanpan.objects import HasName


class MStorage(HasName):
    @abc.abstractmethod
    def get(self, name, *args, **kwargs):
        pass

    @abc.abstractmethod
    def set(self, name, value, *args, **kwargs):
        pass

    @abc.abstractmethod
    def mget(self, name, *args, **kwargs):
        pass

    @abc.abstractmethod
    def mset(self, name, mapping, *args, **kwargs):
        pass

    @property
    def vars(self):
        return Variables(self)
