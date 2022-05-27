# This file is placed in the Public Domain.


"todo"


import time


from ..hdl import Commands
from ..obj import Object, find, fntime, save
from ..tdo import Todo
from ..tmr import elapsed


def dne(event):
    if not event.args:
        return
    selector = {"txt": event.args[0]}
    for _fn, o in find("todo", selector):
        o._deleted = True
        save(o)
        event.reply("ok")
        break


Commands.add(dne)


def tdo(event):
    if not event.rest:
        nr = 0
        for _fn, o in find("todo"):
            event.reply("%s %s %s" % (nr, o.txt, elapsed(time.time() - fntime(_fn))))
            nr += 1
        return
    o = Todo()
    o.txt = event.rest
    save(o)
    event.reply("ok")


Commands.add(tdo)
