# This file is placed in the Public Domain.


"configuration tests"


import unittest


from bot.evt import Event
from bot.obj import Object, edit, update


class Config(Object):

    pass


class Test_Config(unittest.TestCase):

    def test_parsegets(self):
        e = Event()
        e.parse("fnd object mod==irc")
        print(e.gets)
        self.assertEqual(e.gets.mod, "irc")

    def test_parsesets(self):
        e = Event()
        e.parse("cfg bla  mod=irc")
        print(e.sets)
        self.assertEqual(e.sets.mod, "irc")

    def test_edit(self):
        e = Event()
        o = Object()
        update(o, {"mod": "irc,rss"})
        print(o)
        edit(e, o)
        self.assertEqual(e.mod, "irc,rss")
