# coding=utf-8
from __future__ import absolute_import, print_function

import abc
import datetime
from gevent.event import Event


from suanpan import interfaces, objects


class Timer(object):
    def __init__(self, delta):
        self.delta = delta
        self.reset()

    def set(self, delta):
        self.delta = delta
        return self

    def reset(self):
        self.current = datetime.datetime.utcnow()
        return self

    @property
    def next(self):
        return self.current + self.delta


class Loop(objects.HasName, interfaces.HasLoopHooks):
    __metaclass__ = abc.ABCMeta

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.options = {"disabled": False, **kwargs}
        self._cache = None

    def __call__(self):
        for x in self.loop():
            if not self.disabled:
                yield x
            if self._cache:
                self._set(**self._cache)

    def beforeLoop(self):
        if self._cache:
            self._set(**self._cache)

    def afterLoop(self):
        if self._cache:
            self._set(**self._cache)

    def before(self, hook):
        self.addBeforeLoopHooks(hook)
        return hook

    def after(self, hook):
        self.addAfterLoopHooks(hook)
        return hook

    @property
    def disabled(self):
        return self.options["disabled"]

    @disabled.setter
    def disabled(self, value):
        self.set(disabled=value)

    def disable(self):
        self.disabled = False
        return self

    def enable(self):
        self.disabled = True
        return self

    def _set(self, **kwargs):
        self.options.update(kwargs)
        self._cache = None
        return self

    def set(self, **kwargs):
        self._cache = kwargs
        return self

    @abc.abstractmethod
    def loop(self):
        pass

    def json(self):
        return {**self.options}


class Interval(Loop):
    def __init__(self, seconds, pre=False):
        super().__init__(seconds=seconds, pre=pre)
        self.timer = Timer(datetime.timedelta(seconds=seconds))
        self.n = 0
        self._stop_event = Event()
        self._stop_event.clear()

    @property
    def seconds(self):
        return self.options["seconds"]

    @seconds.setter
    def seconds(self, value):
        self.set(seconds=value)

    @property
    def pre(self):
        return self.options["pre"]

    @pre.setter
    def pre(self, value):
        self.set(pre=value)

    def _set(self, **kwargs):
        super()._set(**kwargs)
        self.timer.set(datetime.timedelta(seconds=self.seconds))
        return self

    def _loop(self):
        while True:
            self.timer.reset()
            self.callBeforeLoopHooks()
            if self.pre:
                self._stop_event.wait(self.seconds)
            yield
            if not self.pre:
                self._stop_event.wait(self.seconds)
            self.callAfterLoopHooks()

            if self._stop_event.is_set():
                break

    def loop(self):
        for i, _ in enumerate(self._loop()):
            self.n = i
            yield

    def close(self):
        self._stop_event.set()

    @property
    def next(self):
        return self.timer.next

    def json(self):
        return {**super().json(), "next": self.next}


class IntervalIndex(Interval):
    def loop(self):
        for _ in super().loop():
            yield self.n
