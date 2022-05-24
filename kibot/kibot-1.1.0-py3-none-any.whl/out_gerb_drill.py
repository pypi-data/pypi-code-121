# -*- coding: utf-8 -*-
# Copyright (c) 2020-2021 Salvador E. Tropea
# Copyright (c) 2020-2021 Instituto Nacional de Tecnología Industrial
# License: GPL-3.0
# Project: KiBot (formerly KiPlot)
from pcbnew import GERBER_WRITER
from .out_any_drill import AnyDrill
from .macros import macros, document, output_class  # noqa: F401


class Gerb_DrillOptions(AnyDrill):
    def __init__(self):
        super().__init__()
        self._ext = 'gbr'

    def _configure_writer(self, board, offset):
        drill_writer = GERBER_WRITER(board)
        # hard coded in UI?
        drill_writer.SetFormat(5)
        drill_writer.SetOptions(offset)
        return drill_writer


@output_class
class Gerb_Drill(BaseOutput):  # noqa: F821
    """ Gerber drill format
        This is the information for the drilling machine in gerber format.
        You can create a map file for documentation purposes.
        This output is what you get from the 'File/Fabrication output/Drill Files' menu in pcbnew. """
    def __init__(self):
        super().__init__()
        with document:
            self.options = Gerb_DrillOptions
            """ [dict] Options for the `gerb_drill` output """

    @staticmethod
    def get_conf_examples(name, layers, templates):
        gb = {}
        outs = [gb]
        name_u = name.upper()
        gb['name'] = 'basic_'+name
        gb['comment'] = 'Drill files in '+name_u+' format'
        gb['type'] = name
        gb['dir'] = 'Gerbers_and_Drill'
        gb['options'] = {'map': 'gerber'}
        return outs
