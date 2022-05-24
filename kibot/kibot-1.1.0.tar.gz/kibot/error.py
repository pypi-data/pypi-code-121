# -*- coding: utf-8 -*-
# Copyright (c) 2020 Salvador E. Tropea
# Copyright (c) 2020 Instituto Nacional de Tecnología Industrial
# License: GPL-3.0
# Project: KiBot (formerly KiPlot)
"""
KiBot errors
"""
from sys import (exit, exc_info)
from traceback import print_tb
from .gs import GS
from .misc import (EXIT_BAD_CONFIG)
# Logger
from . import log

logger = log.get_logger()


class KiPlotError(Exception):
    pass


class PlotError(KiPlotError):
    pass


class KiPlotConfigurationError(KiPlotError):
    pass


def trace_dump():
    if GS.debug_enabled:
        logger.error('Trace stack:')
        (type, value, traceback) = exc_info()
        print_tb(traceback)


def config_error(msg):
    trace_dump()
    logger.error(msg)
    exit(EXIT_BAD_CONFIG)
