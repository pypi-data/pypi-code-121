# This file is placed in the Public Domain.


"thread"


import queue
import threading
import types


def __dir__():
    return (
        "Thread",
        "getname",
        "launch"
    )


class Thread(threading.Thread):

    def __init__(self, func, name, *args, daemon=True):
        super().__init__(None, self.run, name, (), {}, daemon=daemon)
        self._exc = None
        self._evt = None
        self.name = name
        self.queue = queue.Queue()
        self.queue.put_nowait((func, args))
        self._result = None

    def __iter__(self):
        return self

    def __next__(self):
        for k in dir(self):
            yield k

    def join(self, timeout=None):
        super().join(timeout)
        return self._result

    def run(self):
        func, args = self.queue.get()
        if args:
            self._evt = args[0]
        self.setName(self.name)
        self._result = func(*args)
        return self._result


def getname(o):
    t = type(o)
    if isinstance(t, types.ModuleType):
        return o.__name__
    if "__self__" in dir(o):
        return "%s.%s" % (o.__self__.__class__.__name__, o.__name__)
    if "__class__" in dir(o) and "__name__" in dir(o):
        return "%s.%s" % (o.__class__.__name__, o.__name__)
    if "__class__" in dir(o):
        return o.__class__.__name__
    if "__name__" in dir(o):
        return o.__name__
    return None


def launch(func, *args, **kwargs):
    name = kwargs.get("name", getname(func))
    t = Thread(func, name, *args)
    t.start()
    return t
