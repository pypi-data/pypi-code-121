# -*- coding: utf-8 -*-
# Copyright (c) 2020 Salvador E. Tropea
# Copyright (c) 2020 Instituto Nacional de Tecnología Industrial
# License: GPL-3.0
# Project: KiBot (formerly KiPlot)
from pcbnew import PLOT_FORMAT_HPGL, SKETCH, FILLED
from .misc import AUTO_SCALE
from .out_any_layer import AnyLayer
from .drill_marks import DrillMarks
from .macros import macros, document, output_class  # noqa: F401


class HPGLOptions(DrillMarks):
    def __init__(self):
        super().__init__()
        with document:
            self.mirror_plot = False
            """ Plot mirrored """
            self.sketch_plot = False
            """ Don't fill objects, just draw the outline """
            self.scaling = 0
            """ Scale factor (0 means autoscaling) """
            self.pen_number = 1
            """ [1,16] Pen number """
            self.pen_speed = 20
            """ [1,99] Pen speed """
            self.pen_width = 15
            """ [0,100] Pen diameter in MILS, useful to fill areas. However, it is in mm in HPGL files """
        self._plot_format = PLOT_FORMAT_HPGL

    def _configure_plot_ctrl(self, po, output_dir):
        super()._configure_plot_ctrl(po, output_dir)
        po.SetHPGLPenDiameter(self.pen_width)
        po.SetHPGLPenNum(self.pen_number)
        po.SetHPGLPenSpeed(self.pen_speed)
        po.SetPlotMode(SKETCH if self.sketch_plot else FILLED)
        po.SetMirror(self.mirror_plot)
        # Scaling/Autoscale
        if self.scaling == AUTO_SCALE:
            po.SetAutoScale(True)
            po.SetScale(1)
        else:
            po.SetAutoScale(False)
            po.SetScale(self.scaling)

    def read_vals_from_po(self, po):
        super().read_vals_from_po(po)
        self.pen_width = po.GetHPGLPenDiameter()
        self.pen_number = po.GetHPGLPenNum()
        self.pen_speed = po.GetHPGLPenSpeed()
        self.sketch_plot = po.GetPlotMode() == SKETCH
        self.mirror_plot = po.GetMirror()
        # scaleselection
        sel = po.GetScaleSelection()
        sel = sel if sel < 0 or sel > 4 else 4
        self.scaling = (AUTO_SCALE, 1.0, 1.5, 2.0, 3.0)[sel]


@output_class
class HPGL(AnyLayer):
    """ HPGL (Hewlett & Packard Graphics Language)
        Exports the PCB for plotters and laser printers.
        This output is what you get from the File/Plot menu in pcbnew. """
    def __init__(self):
        super().__init__()
        with document:
            self.options = HPGLOptions
            """ [dict] Options for the `hpgl` output """
