#!/usr/bin/env python
# encoding: utf-8
#
# cmds.py
#
# Created by José Sánchez-Gallego on 17 Feb 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import click

from alertsActor.cmds.cheatSheet import cheatSheet
from alertsActor.cmds.ping import ping
from alertsActor.cmds.version import version
from alertsActor.cmds.status import status
from alertsActor.cmds.acknowledge import acknowledge
from alertsActor.cmds.unacknowledge import unacknowledge
from alertsActor.cmds.enable import enable
from alertsActor.cmds.disable import disable
from alertsActor.cmds.instrumentState import instrumentState


__all__ = ('alerts_parser')


@click.group()
@click.pass_context
def alerts_parser(ctx):
    pass


alerts_parser.add_command(cheatSheet)
alerts_parser.add_command(ping)
alerts_parser.add_command(version)
alerts_parser.add_command(status)
alerts_parser.add_command(acknowledge)
alerts_parser.add_command(unacknowledge)
alerts_parser.add_command(enable)
alerts_parser.add_command(disable)
alerts_parser.add_command(instrumentState)


if __name__ == '__main__':
    alerts_parser()
