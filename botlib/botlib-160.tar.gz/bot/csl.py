# This file is placed in the Public Domain.


"console"


import time


from .evt import Command
from .hdl import Handler


def __dir__():
    return (
        "CLI",
        "Console"
    )


class CLI(Handler):

    def announce(self, txt):
        self.raw(txt)

    def cmd(self, txt):
        c = Command()
        c.channel = ""
        c.orig = repr(self)
        c.txt = txt
        self.handle(c)
        c.wait()

    def raw(self, txt):
        pass

class Console(CLI):

    def handle(self, e):
        Handler.handle(self, e)
        e.wait()

    def poll(self):
        e = Command()
        e.channel = ""
        e.cmd = ""
        e.txt = input("> ")
        e.orig = repr(self)
        if e.txt:
            e.cmd = e.txt.split()[0]
        return e

    def forever(self):
        while 1:
            time.sleep(1.0)
