# -*- coding: utf-8 -*-
"""
Created on September 01, 2015

Copyright Alpes Lasers SA, Neuchatel, Switzerland, 2015

@author: chiesa
"""

import argparse
import logging

logger = logging.getLogger(__name__)

_version = 'undefined'

try:
    from phootonics_controller import pkg, version

    _version = '{} {}'.format(pkg, version)
except Exception as e:
    logger.debug(e, exc_info=1)


baseparser = argparse.ArgumentParser(add_help=False)
baseparser.add_argument("--show-version", help="Show the project version",
                        action="version", version="%s %s" % (pkg, version))
alparser = argparse.ArgumentParser(parents=[baseparser])


