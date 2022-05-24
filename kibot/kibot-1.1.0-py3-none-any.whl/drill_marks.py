# -*- coding: utf-8 -*-
# Copyright (c) 2020 Salvador E. Tropea
# Copyright (c) 2020 Instituto Nacional de Tecnología Industrial
# License: GPL-3.0
# Project: KiBot (formerly KiPlot)
from pcbnew import (PCB_PLOT_PARAMS)
from .error import KiPlotConfigurationError
from .out_any_layer import AnyLayerOptions
from .macros import macros, document  # noqa: F401
from . import log

logger = log.get_logger()


class DrillMarks(AnyLayerOptions):
    """ This class provides the drill_marks attribute.
        Used by DXF, HPGL, PDF, PS and SVG formats. """
    # Mappings to KiCad values
    _drill_marks_map = {
                        'none': PCB_PLOT_PARAMS.NO_DRILL_SHAPE,
                        'small': PCB_PLOT_PARAMS.SMALL_DRILL_SHAPE,
                        'full': PCB_PLOT_PARAMS.FULL_DRILL_SHAPE,
                       }
    _drill_marks_rev_map = {
                            PCB_PLOT_PARAMS.NO_DRILL_SHAPE: 'none',
                            PCB_PLOT_PARAMS.SMALL_DRILL_SHAPE: 'small',
                            PCB_PLOT_PARAMS.FULL_DRILL_SHAPE: 'full',
                           }

    def __init__(self):
        super().__init__()
        with document:
            self._drill_marks = 'full'
            """ what to use to indicate the drill places, can be none, small or full (for real scale) """

    @property
    def drill_marks(self):
        return self._drill_marks

    @drill_marks.setter
    def drill_marks(self, val):
        if val not in self._drill_marks_map:
            raise KiPlotConfigurationError("Unknown drill mark type: {}".format(val))
        self._drill_marks = val

    def config(self, parent):
        super().config(parent)
        self._drill_marks = DrillMarks._drill_marks_map[self._drill_marks]

    def _configure_plot_ctrl(self, po, output_dir):
        super()._configure_plot_ctrl(po, output_dir)
        # How we draw drill marks
        po.SetDrillMarksType(self._drill_marks)

    def read_vals_from_po(self, po):
        super().read_vals_from_po(po)
        self._drill_marks = DrillMarks._drill_marks_rev_map[po.GetDrillMarksType()]
