# This file is placed in the Public Domain.


"enter txt"


from ..hdl import Commands
from ..obj import save
from ..log import Log


def log(event):
    if not event.rest:
        event.reply("log <txt>")
        return
    o = Log()
    o.txt = event.rest
    save(o)
    event.reply("ok")


Commands.add(log)
