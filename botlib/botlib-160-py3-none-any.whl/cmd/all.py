# This file is placed in the Public Domain.


import bot.cmd.bsc as bsc
import bot.cmd.irc as irc
import bot.cmd.log as log
import bot.cmd.rss as rss
import bot.cmd.tdo as tdo


from bot.tbl import Table


Table.add(bsc)
Table.add(irc)
Table.add(log)
Table.add(rss)
Table.add(tdo)
