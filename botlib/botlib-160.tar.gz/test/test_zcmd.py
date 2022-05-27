# This file is placed in the Public Domain.


"command tests"


import random
import unittest


from bot.evt import Command
from bot.obj import Object, get
from bot.hdl import Commands


events = []


param = Object()
param.cmd = [""]
param.cfg = ["nick=opbot", "server=localhost", "port=6699"]
param.fnd = ["log", "log txt==test", "config", "config name=botd", "config server==localhost"]
param.flt = ["0", ""]
param.log = ["test1", "test2"]
param.mre = [""]
param.thr = [""]


def getmain(name):
    main = __import__("__main__")
    return getattr(main, name, None)


def consume(events):
    fixed = []
    res = []
    for e in events:
        e.wait()
        fixed.append(e)
    for f in fixed:
        try:
            events.remove(f)
        except ValueError:
            continue
    return res


class Test_Commands(unittest.TestCase):

    def test_commands(self):
        c = getmain("c")
        cmds = sorted(Commands.cmd)
        random.shuffle(cmds)
        for cmd in cmds:
            for ex in get(param, cmd, ""):
                e = Command()
                e.channel = "#botd"
                e.orig = repr(c)
                txt = cmd + " " + ex
                e.txt = txt.strip()
                c.put(e)
                events.append(e)
        consume(events)
        self.assertTrue(not events)
