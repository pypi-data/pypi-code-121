# -*- coding: utf-8 -*-
# Copyright (c) 2022 Salvador E. Tropea
# Copyright (c) 2022 Instituto Nacional de Tecnología Industrial
# License: GPL-3.0
# Project: KiBot (formerly KiPlot)
import pcbnew
from .error import KiPlotConfigurationError
from .gs import GS
from .kiplot import load_board
from .macros import macros, pre_class  # noqa: F401


@pre_class
class Fill_Zones(BasePreFlight):  # noqa: F821
    """ [boolean=false] Fill all zones again and save the PCB """
    def __init__(self, name, value):
        super().__init__(name, value)
        if not isinstance(value, bool):
            raise KiPlotConfigurationError('must be boolean')
        self._enabled = value
        self._pcb_related = True

    def apply(self):
        load_board()
        pcbnew.ZONE_FILLER(GS.board).Fill(GS.board.Zones())
        GS.make_bkp(GS.pcb_file)
        GS.board.Save(GS.pcb_file)
