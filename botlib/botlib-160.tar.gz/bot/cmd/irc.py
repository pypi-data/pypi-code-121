# This file is placed in the Public Domain.


"irc commands"


import base64


from ..hdl import Commands
from ..obj import edit, format, last, save
from ..irc import Config


def cfg(event):
    c = Config()
    last(c)
    if not event.sets:
        event.reply(format(c, skip="realname,sleep,username"))
        return
    edit(c, event.sets)
    save(c)
    event.reply("ok")


Commands.add(cfg)


def mre(event):
    if not event.channel:
        event.reply("channel is not set.")
        return
    bot = event.bot()
    if "cache" not in dir(bot):
        event.reply("bot is missing cache")
        return
    if event.channel not in bot.cache:
        event.reply("no output in %s cache." % event.channel)
        return
    for _x in range(3):
        txt = bot.get(event.channel)
        if txt:
            bot.say(event.channel, txt)
    sz = bot.size(event.channel)
    event.reply("%s more in cache" % sz)


Commands.add(mre)


def pwd(event):
    if len(event.args) != 2:
        event.reply("pwd <nick> <password>")
        return
    m = "\x00%s\x00%s" % (event.args[0], event.args[1])
    mb = m.encode("ascii")
    bb = base64.b64encode(mb)
    bm = bb.decode("ascii")
    event.reply(bm)


Commands.add(pwd)
