#!/usr/bin/env python
# encoding: utf-8
#
# acknowledge.py
#


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import click

from alertsActor.cmds import alerts_context

__all__ = ('acknowledge')


@click.command()
@click.argument('id', nargs=1, default=None, required=True)
@click.argument('severity', nargs=1, default='info', 
                type=click.Choice(['ok', 'info', 'apogeediskwarn','warn', 'serious', 'critical']))
@click.option('-m', '--message', multiple=True, default=None, help='a short message to hang on to')
@alerts_context
def acknowledge(actor, cmd, user, id=None, severity='info', message=None):
    """acknowledge an alert"""

    # if isinstance(id, unicode):
    #     id = str(id)  # .decode("utf-8")

    keyword = actor.monitoring[id]
    
    if keyword.severity != severity:
        cmd.setState(cmd.Failed, "Severity does not match alert severity")
        return None

    # it seems messages can't be passed right. geez..
    if len(message) > 0:
        msg = "".join(("{} ".format(m) for m in message))
    else:
        msg = None

    keyword.acknowledge(msg=msg, acknowledgedBy=user)
    cmd.setState(cmd.Done, 'acknowledged')

    return False
