#!/usr/bin/env python
# encoding: utf-8
#
# status.py


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import yaml

import click

from alertsActor.cmds import alerts_context

__all__ = ('status')


@click.command()
@alerts_context
def status(actor, cmd, user):
    """returns actor status"""

    # print("current model: ")
    # for k, v in actor.hubModel.items():
    #     print(k, v)
    #     print("\n \n")

    actor.broadcastActive()
    actor.broadcastDisabled()
    actor.broadcastAll()
    actor.broadcastInstruments()

    cmd.setState(cmd.Done, "Now you know all I know")

    try:
        dontClutterSDSSUser = os.getlogin()
    except OSError:
        # when run as a daemon, getlogin will fail
        dontClutterSDSSUser = "sdss5"
    if "sdss" in dontClutterSDSSUser:
        with open("/data/logs/actors/alerts/alerts.hubModel.yaml", "w") as dump:
            print(yaml.dump(actor.hubModel), file=dump)

    # otherwise we can clutter the home directory a bit
    # write a log of the hubModel for posterity
    else:
        with open("alerts.hubModel.yaml", "w") as dump:
            print(yaml.dump(actor.hubModel), file=dump)


    return False
