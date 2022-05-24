# -*- coding: utf-8 -*-
# Copyright (c) 2020-2022 Salvador E. Tropea
# Copyright (c) 2020-2022 Instituto Nacional de Tecnología Industrial
# Copyright (c) 2020 @nerdyscout
# License: GPL-3.0
# Project: KiBot (formerly KiPlot)
from .gs import GS
from .out_any_sch_print import Any_SCH_PrintOptions, register_deps
from .misc import SVG_SCH_PRINT
from .macros import macros, document, output_class  # noqa: F401
from . import log

logger = log.get_logger()
register_deps('svg')


class SVG_SCH_PrintOptions(Any_SCH_PrintOptions):
    def __init__(self):
        with document:
            self.output = GS.def_global_output
            """ Filename for the output SVG (%i=schematic, %x=svg) """
        super().__init__()
        self._expand_ext = 'svg'
        self._exit_error = SVG_SCH_PRINT


@output_class
class SVG_SCH_Print(BaseOutput):  # noqa: F821
    """ SVG Schematic Print
        Exports the PCB. Suitable for printing.
        This is a format to document your schematic. """
    def __init__(self):
        super().__init__()
        with document:
            self.options = SVG_SCH_PrintOptions
            """ [dict] Options for the `svg_sch_print` output """
        self._sch_related = True

    @staticmethod
    def get_conf_examples(name, layers, templates):
        return BaseOutput.simple_conf_examples(name, 'Schematic in SVG format', 'Schematic')  # noqa: F821
