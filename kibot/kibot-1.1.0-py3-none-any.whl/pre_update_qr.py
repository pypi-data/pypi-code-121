# -*- coding: utf-8 -*-
# Copyright (c) 2020-2022 Salvador E. Tropea
# Copyright (c) 2020-2022 Instituto Nacional de Tecnología Industrial
# License: GPL-3.0
# Project: KiBot (formerly KiPlot)
from .macros import macros, pre_class  # noqa: F401
from .error import KiPlotConfigurationError
from .registrable import RegOutput
from .log import get_logger

logger = get_logger(__name__)


@pre_class
class Update_QR(BasePreFlight):  # noqa: F821
    """ [boolean=false] Update the QR codes.
        Complements the `qr_lib` output.
        The KiCad 6 files and the KiCad 5 PCB needs manual update, generating a new library isn't enough """
    def __init__(self, name, value):
        super().__init__(name, value)
        if not isinstance(value, bool):
            raise KiPlotConfigurationError('must be boolean')
        self._enabled = value
        self._sch_related = True
        self._pcb_related = True

    def run(self):
        for o in list(RegOutput.get_outputs()):  # We convert it to a list because we will mutate the dict
            if o.type == 'qr_lib':
                RegOutput.make_prioritary(o.name)
                o._update_mode = True
                logger.debug('Making {} prioritary'.format(o))
