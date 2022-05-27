# This file is placed in the Public Domain.


"object programming tests"


import unittest


from bot.tbl import Table


import bot.cmd.all


Table.add(bot.cmd.bsc)


class Test_Table(unittest.TestCase):

    def test_mod(self):
        self.assertTrue("bot.cmd.bsc" in Table.mod)
