# This file is placed in the Public Domain.


"handler"


import queue
import threading
import time
import _thread


from .obj import Config, Object, get, register
from .thr import launch


def __dir__():
    return (
        "Callbacks",
        "Commands",
        "Handler",
    )


execlock = _thread.allocate_lock()
starttime = time.time()


def dispatch(e):
    e.parse()
    f = Commands.get(e.cmd)
    if f:
        f(e)
        e.show()
    e.ready()


class NotImplemented(Exception):

    pass


class Bus(Object):

    objs = []

    @staticmethod
    def add(o):
        if repr(o) not in [repr(x) for x in Bus.objs]:
            Bus.objs.append(o)

    @staticmethod
    def announce(txt):
        for o in Bus.objs:
            o.announce(txt)

    @staticmethod
    def byorig(orig):
        for o in Bus.objs:
            if repr(o) == orig:
                return o

    @staticmethod
    def say(orig, channel, txt):
        o = Bus.byorig(orig)
        if o:
            o.say(channel, txt)


class Callbacks(Object):

    cbs = Object()
    errors = []
    threaded = True

    @staticmethod
    def add(name, cb):
        register(Callbacks.cbs, name, cb)

    @staticmethod
    def callback(e):
        f = Callbacks.get(e.type)
        if not f:
            e.ready()
            return
        try:
            f(e)
        except Exception as ex:
            if Callbacks.threaded:
                Callbacks.errors.append(ex)
                e._exc = ex
                e.ready()
            else:
                raise

    @staticmethod
    def get(cmd):
        return get(Callbacks.cbs, cmd)

    @staticmethod
    def dispatch(e):
        if Callbacks.threaded:
            e._thrs.append(launch(Callbacks.callback, e, name=e.txt))
            return
        Callbacks.callback(e)



class Commands(Object):

    cmd = Object()

    @staticmethod
    def add(command):
        register(Commands.cmd, command.__name__, command)

    @staticmethod
    def get(command):
        f =  get(Commands.cmd, command)
        return f


class Handler(Object):

    def __init__(self):
        Object.__init__(self)
        self.cache = Object()
        self.cfg = Config()
        self.queue = queue.Queue()
        self.stopped = threading.Event()
        self.threaded = False
        Bus.add(self)

    def announce(self, txt):
        self.raw(txt)

    def forever(self):
        while 1:
            time.sleep(1.0)

    def handle(self, e):
        Callbacks.dispatch(e)

    def loop(self):
        while not self.stopped.isSet():
            self.handle(self.poll())

    def poll(self):
        return self.queue.get()

    def put(self, e):
        self.queue.put_nowait(e)

    def raw(self, txt):
        pass

    def register(self, typ, cb):
        Callbacks.add(typ, cb)

    def restart(self):
        self.stop()
        self.start()

    def say(self, channel, txt):
        self.raw(txt)

    def start(self):
        self.stopped.clear()
        launch(self.loop)

    def stop(self):
        self.stopped.set()
