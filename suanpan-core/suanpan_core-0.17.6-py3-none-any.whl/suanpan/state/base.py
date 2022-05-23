# coding=utf-8
from __future__ import absolute_import, print_function

from datetime import datetime

from suanpan.objects import Context, HasName


class StateBase(HasName):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self._args = args
        self._kwargs = kwargs
        self.init(*self._args, **self._kwargs)

    def init(self, *args, **kwargs):
        self.current = Context(*args, **kwargs)

    def updateCurrent(self, *args, **kwargs):
        raise NotImplementedError("Method not implemented!")

    def update(self, *args, **kwargs):
        raise NotImplementedError("Method not implemented!")

    def clean(self, *args, **kwargs):
        raise NotImplementedError("Method not implemented!")

    def reset(self, *args, **kwargs):
        self.clean(*args, **kwargs)
        self.init(*self._args, **self._kwargs)


class Loader(StateBase):
    def load(self, *args, **kwargs):
        self.updateCurrent()
        return self.update(*args, **kwargs)


class IndexLoader(Loader):
    def __init__(self, index=0, **kwargs):
        super().__init__(index=index, **kwargs)

    def updateCurrent(self, index=None):
        self.current.index = index or self.current.index + 1
        return self.current


class Saver(StateBase):
    def save(self, *args, **kwargs):
        self.updateCurrent()
        return self.update(*args, **kwargs)


class IndexSaver(Saver):
    def __init__(self, index=0, **kwargs):
        super().__init__(index=index, **kwargs)

    def updateCurrent(self, index=None):
        self.current.index = index or self.current.index + 1
        return self.current


class TimeSaver(Saver):
    def __init__(self, time=None, **kwargs):
        time = time or datetime.now()
        super().__init__(time=time, **kwargs)

    def updateCurrent(self, time=None):
        self.current.time = time or datetime.now()
        return self.current
