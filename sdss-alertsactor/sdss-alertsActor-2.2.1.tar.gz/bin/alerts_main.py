#!/usr/bin/env python
# encoding: utf-8
#
# file.py
#
# Created by José Sánchez-Gallego on 17 Sep 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import logging

from twisted.internet import reactor

from alertsActor import config, __version__
# from alertsActor.logger import log
from alertsActor.alerts_main import alertsActor

import click



@click.command()
@click.option('-d', '--debug', is_flag=True, show_default=True,
              help='Debug mode.')
def alerts_cmd(debug=False):

    port = config['tron']['port']

    if debug:
        print("debug not treated specially at the moment. TODO?")
        # log.sh.setLevel(logging.DEBUG)
        # log.debug('alertsActor started in debug mode.')

    alertsActor(config, userPort=port, version=__version__)

    reactor.run()


if __name__ == '__main__':
    alerts_cmd()
