#!/usr/bin/env python
# encoding: utf-8
#
# ping.py
#
# Created by José Sánchez-Gallego on 19 Mar 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import click

from alertsActor.cmds import alerts_context


__all__ = ('ping')


@click.command()
@alerts_context
def ping(actor, cmd, user):
    """Pings the actor."""

    # for k, a in actor.monitoring.items():
    #     print(k, a.keyword)

    cmd.setState(cmd.Done, "I'm not dead yet!")
    # print("monitoring heartbeats for :", actor.heartbeats.keys())

    return False
