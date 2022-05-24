# -*- coding: utf-8 -*-
# Copyright (c) 2020-2022 Salvador E. Tropea
# Copyright (c) 2020-2022 Instituto Nacional de Tecnología Industrial
# License: GPL-3.0
# Project: KiBot (formerly KiPlot)
from .gs import GS
from .out_any_pcb_print import Any_PCB_PrintOptions, register_deps
from .error import KiPlotConfigurationError
from .macros import macros, document, output_class  # noqa: F401
from .layer import Layer
from . import log

logger = log.get_logger()
register_deps('pdf')


class PDF_PCB_PrintOptions(Any_PCB_PrintOptions):
    def __init__(self):
        with document:
            self.output = GS.def_global_output
            """ Filename for the output PDF (%i=layers, %x=pdf)"""
        super().__init__()
        self._expand_ext = 'pdf'


@output_class
class PDF_PCB_Print(BaseOutput):  # noqa: F821
    """ PDF PCB Print (Portable Document Format)
        Exports the PCB to the most common exchange format. Suitable for printing.
        This is the main format to document your PCB.
        This output is what you get from the 'File/Print' menu in pcbnew.
        The `pcb_print` is usually a better alternative. """
    def __init__(self):
        super().__init__()
        with document:
            self.options = PDF_PCB_PrintOptions
            """ [dict] Options for the `pdf_pcb_print` output """
            self.layers = Layer
            """ [list(dict)|list(string)|string] [all,selected,copper,technical,user]
                List of PCB layers to include in the PDF """

    def config(self, parent):
        super().config(parent)
        # We need layers
        if isinstance(self.layers, type):
            raise KiPlotConfigurationError("Missing `layers` list")
        self.options.set_layers(self.layers)
