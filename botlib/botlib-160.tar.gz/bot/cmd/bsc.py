# This file is placed in the Public Domain


"commands"


import threading
import time


from ..hdl import Bus, Commands, starttime
from ..obj import Config, Db, Object, find, fntime, format, get, save, update
from ..thr import getname
from ..tmr import elapsed
from ..usr import User


def __dir__():
    return (
        "cmd",
        "dlt",
        "flt",
        "fnd",
        "met",
        "thr",
        "ver"
    )


def cmd(event):
    event.reply(",".join(sorted(Commands.cmd)))


Commands.add(cmd)


def dlt(event):
    if not event.args:
        event.reply("dlt <username>")
        return
    selector = {"user": event.args[0]}
    for _fn, o in find("user", selector):
        o._deleted = True
        save(o)
        event.reply("ok")
        break

Commands.add(dlt)


def flt(event):
    try:
        index = int(event.args[0])
        event.reply(Bus.objs[index])
        return
    except (KeyError, TypeError, IndexError, ValueError):
        pass
    event.reply(" | ".join([getname(o) for o in Bus.objs]))


Commands.add(flt)


def fnd(event):
    if not event.args:
        db = Db()
        res = ",".join(
            sorted({x.split(".")[-1].lower() for x in db.types()}))
        if res:
            event.reply(res)
        else:
            event.reply("no types yet.")
        return
    bot = event.bot()
    otype = event.args[0]
    res = list(find(otype))
    if bot.cache:
        if len(res) > 3:
            bot.extend(event.channel, [x[1].txt for x in res])
            bot.say(event.channel, "%s left in cache, use !mre to show more" % bot.cache.size())
            return
    nr = 0
    for _fn, o in res:
        txt = "%s %s %s" % (str(nr), format(o), elapsed(time.time()-fntime(_fn)))
        nr += 1
        event.reply(txt)
    if not nr:
        event.reply("no result")


Commands.add(fnd)


def met(event):
    if not event.args:
        event.reply("met <userhost>")
        return
    user = User()
    user.user = event.rest
    user.perms = ["USER"]
    save(user)
    event.reply("ok")


Commands.add(met)


def thr(event):
    result = []
    for t in sorted(threading.enumerate(), key=lambda x: x.getName()):
        if str(t).startswith("<_"):
            continue
        o = Object()
        update(o, vars(t))
        if get(o, "sleep", None):
            up = o.sleep - int(time.time() - o.state.latest)
        else:
            up = int(time.time() - starttime)
        result.append((up, t.getName()))
    res = []
    for up, txt in sorted(result, key=lambda x: x[0]):
        res.append("%s/%s" % (txt, elapsed(up)))
    if res:
        event.reply(" ".join(res))


Commands.add(thr)


def ver(event):
    event.reply("BOTLIB %s" % (Config.version or "1"))


Commands.add(ver)
