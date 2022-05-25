#!/usr/bin/env python

import monexec

import datetime
import sys
import yaml

# Factory
factory=monexec.MoneaterFactory(description='Send file contents to InfluxDB')
factory.parser.add_argument('file',
                            help='File contents to monitor.')
factory.parser.add_argument('eater',
                            help='Class responsible for eating data.')
factory.parser.add_argument('--spec', '-s',action='store_true',
                            help='Treat eater as a spec YAML file.')

factory.parse()

#
# Client
db = factory.database()

#
# Executor
exe=None
if factory.args.spec:
    # Monitor files as specified by spec file
    moneaters=[]
    with open(factory.args.eater) as fh:
        spec=yaml.safe_load(fh)
        for monitor in spec['monitor']:
            eater = monexec.get_eater(monitor['eater'])
            fh = open(monitor['file'].replace('{logdir}',factory.args.file))
            myexe = monexec.Moneater(fh, eater, monitor['table'], db, monitor.get('tags',{}))
            moneaters.append(myexe)
    exe=monexec.Moneaters(moneaters)
else:
    # Monitor a single file
    fh = open(factory.args.file)
    eater = monexec.get_eater(factory.args.eater)
    exe = monexec.Moneater(fh, eater, factory.args.table, db)

#
# The big loop
while True:
    exe.run_line()
