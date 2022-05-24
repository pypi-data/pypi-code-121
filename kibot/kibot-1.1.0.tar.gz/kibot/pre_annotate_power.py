# -*- coding: utf-8 -*-
# Copyright (c) 2022 Salvador E. Tropea
# Copyright (c) 2022 Instituto Nacional de Tecnología Industrial
# License: GPL-3.0
# Project: KiBot (formerly KiPlot)
from .error import KiPlotConfigurationError
from .gs import (GS)
from .kiplot import load_sch
from .misc import W_NOANNO
from .macros import macros, pre_class  # noqa: F401
from .log import get_logger

logger = get_logger(__name__)


@pre_class
class Annotate_Power(BasePreFlight):  # noqa: F821
    """ [boolean=false] Annotates all power components.
        This preflight modifies the schematic, use it only in revision control environments.
        Used to solve ERC problems when using filters that remove power reference numbers """
    def __init__(self, name, value):
        super().__init__(name, value)
        if not isinstance(value, bool):
            raise KiPlotConfigurationError('must be boolean')
        self._enabled = value
        self._sch_related = True

    def annotate_ki5(self):
        """ Annotate power components for KiCad 5 """
        comps = GS.sch.get_components(exclude_power=False)
        num = 1
        for c in comps:
            if c.is_power:
                # Force a new number
                c.ref = c.f_ref = c.ref_prefix+'{:02d}'.format(num)
                c.ref_suffix = str(num)
                num = num+1
                # Fix the ARs
                if c.ar:
                    first = True
                    for o in c.ar:
                        if first:
                            # Copy this to the first
                            o.ref = c.ref
                            first = False
                        else:
                            # Allocate new numbers for the rest
                            o.ref = c.ref_prefix+'{:02d}'.format(num)
                            num = num+1
                # Fix the reference field
                field = next(filter(lambda x: x.number == 0, c.fields), None)
                if field:
                    field.value = c.ref

    def annotate_ki6(self):
        """ Annotate power components for KiCad 6 """
        num = 1
        for ins in GS.sch.symbol_instances:
            c = ins.component
            if c.is_power:
                c.set_ref(c.ref_prefix+'{:02d}'.format(num))
                num = num+1

    def run(self):
        load_sch()
        if not GS.sch:
            return
        if not GS.sch.annotation_error:
            logger.warning(W_NOANNO+"No annotation problems, skipping power annotation")
            return
        if GS.ki5():
            self.annotate_ki5()
        else:
            self.annotate_ki6()
        GS.sch.save()
