# This file is placed in the Public Domain


"rss commands"


from ..hdl import Commands
from ..obj import Class, Db, edit, find, save
from ..rss import Fetcher, Rss


def dpl(event):
    if len(event.args) < 2:
        event.reply("dpl <stringinurl> <item1,item2>")
        return
    db = Db()
    setter = {"display_list": event.args[1]}
    names = Class.full("rss")
    if names:
        _fn, o = db.lastmatch(names[0], {"rss": event.args[0]})
        if o:
            edit(o, setter)
            save(o)
            event.reply("ok")


Commands.add(dpl)


def ftc(event):
    res = []
    thrs = []
    fetcher = Fetcher()
    fetcher.start(False)
    thrs = fetcher.run()
    for t in thrs:
        res.append(t.join())
    if res:
        event.reply(",".join([str(x) for x in res]))
        return


Commands.add(ftc)


def nme(event):
    if len(event.args) != 2:
        event.reply("name <stringinurl> <name>")
        return
    selector = {"rss": event.args[0]}
    nr = 0
    got = []
    for _fn, o in find("rss", selector):
        nr += 1
        o.name = event.args[1]
        got.append(o)
    for o in got:
        save(o)
    event.reply("ok")


Commands.add(nme)


def rem(event):
    if not event.args:
        event.reply("rem <stringinurl>")
        return
    selector = {"rss": event.args[0]}
    nr = 0
    got = []
    for _fn, o in find("rss", selector):
        nr += 1
        o._deleted = True
        got.append(o)
    for o in got:
        save(o)
    event.reply("ok")


Commands.add(rem)


def rss(event):
    if not event.args:
        event.reply("rss <url>")
        return
    url = event.args[0]
    if "http" not in url:
        event.reply("i need an url")
        return
    res = list(find("rss", {"rss": url}))
    if res:
        return
    o = Rss()
    o.rss = event.args[0]
    save(o)
    event.reply("ok")


Commands.add(rss)
