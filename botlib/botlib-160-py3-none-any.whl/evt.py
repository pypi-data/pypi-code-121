# This file is placed in the Public Domain.


"event"


import threading


from .obj import Object
from .hdl import Bus


def __dir__():
    return (
        "Event",
    )


class Event(Object):

    def __init__(self):
        super().__init__()
        self._exc = None
        self._ready = threading.Event()
        self._result = []
        self._thrs = []
        self.args = []
        self.channel = ""
        self.cmd = ""
        self.gets = Object()
        self.index = 0
        self.opts = Object()
        self.orig = ""
        self.rest = ""
        self.sets = Object()
        self.txt = ""
        self.type = "event"

    def bot(self):
        return Bus.byorig(self.orig)

    def parse(self, txt=None, orig=None):
        self.txt = txt or self.txt
        self.orig = orig or self.orig
        spl = self.txt.split()
        args = []
        _nr = -1
        for w in spl:
            _nr += 1
            if w.startswith("-"):
                try:
                    self.index = int(w[1:])
                except ValueError:
                    self.opts[w] = True
                continue
            if _nr == 0:
                self.cmd = w
                continue
            try:
                k, v = w.split("==")
                self.gets[k] = v
                continue
            except ValueError:
                pass
            try:
                k, v = w.split("=")
                self.sets[k] = v
                continue
            except ValueError:
                args.append(w)
        if args:
            self.args = args
            self.rest = " ".join(args)

    def ready(self):
        self._ready.set()

    def reply(self, txt):
        self._result.append(txt)

    def show(self):
        assert self.orig
        for txt in self._result:
            Bus.say(self.orig, self.channel, txt)

    def wait(self):
        self._ready.wait()
        for thr in self._thrs:
            thr.join()
        return self._result


class Command(Event):

    def __init__(self):
        Event.__init__(self)
        self.type = "command"
        