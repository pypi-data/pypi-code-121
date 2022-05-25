#!/usr/bin/env python
# encoding: utf-8
#
# disable.py



from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import click

from alertsActor.cmds import alerts_context

__all__ = ('disable')


@click.command()
@click.argument('alertkey', nargs=1, default=None, required=True)
@click.argument('severity', nargs=1, default='info',
                type=click.Choice(['ok', 'info', 'apogeediskwarn', 'warn', 'serious', 'critical']))
@alerts_context
def disable(actor, cmd, user, alertkey=None, severity='info'):
    """disable an alert"""

    # if isinstance(alertkey, unicode):
    #     alertkey = str(alertkey)

    keyword = actor.monitoring[alertkey]

    keyword.disable(user)

    actor.broadcastActive()
    actor.broadcastDisabled()
    actor.broadcastAll()

    cmd.setState(cmd.Done, 'disabled')

    return False
