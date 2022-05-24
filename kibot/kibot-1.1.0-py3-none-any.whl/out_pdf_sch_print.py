# -*- coding: utf-8 -*-
# Copyright (c) 2020-2022 Salvador E. Tropea
# Copyright (c) 2020-2022 Instituto Nacional de Tecnología Industrial
# License: GPL-3.0
# Project: KiBot (formerly KiPlot)
from .gs import GS
from .out_any_sch_print import Any_SCH_PrintOptions, register_deps
from .misc import PDF_SCH_PRINT
from .macros import macros, document, output_class  # noqa: F401
from . import log

logger = log.get_logger()
register_deps('pdf')


class PDF_SCH_PrintOptions(Any_SCH_PrintOptions):
    def __init__(self):
        with document:
            self.output = GS.def_global_output
            """ Filename for the output PDF (%i=schematic, %x=pdf)"""
        super().__init__()
        self._expand_ext = 'pdf'
        self._exit_error = PDF_SCH_PRINT


@output_class
class PDF_SCH_Print(BaseOutput):  # noqa: F821
    """ PDF Schematic Print (Portable Document Format)
        Exports the PCB to the most common exchange format. Suitable for printing.
        This is the main format to document your schematic.
        This output is what you get from the 'File/Print' menu in eeschema. """
    def __init__(self):
        super().__init__()
        with document:
            self.options = PDF_SCH_PrintOptions
            """ [dict] Options for the `pdf_sch_print` output """
        self._sch_related = True

    @staticmethod
    def get_conf_examples(name, layers, templates):
        return BaseOutput.simple_conf_examples(name, 'Schematic in PDF format', 'Schematic')  # noqa: F821
