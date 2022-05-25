#!python

import monexec

import importlib
import datetime
import sys

# Factory
factory=monexec.MoneaterFactory(description='Send cin to InfluxDB')
factory.parser.add_argument('eater', help='Class responsible for eating data.')
factory.parser.add_argument('--table','-t',default='measurement', help='Measurement name')

factory.parse()

#
# Eater
eater=monexec.get_eater(factory.args.eater)

#
# Client
db = factory.database()

#
# Executor
exe = monexec.Moneater(sys.stdin, eater, factory.args.table, db)

#
# The big loop
while True:
    exe.run_line()
