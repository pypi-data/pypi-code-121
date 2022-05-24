# -*- coding: utf-8 -*-
# Copyright (c) 2022 Salvador E. Tropea
# Copyright (c) 2022 Instituto Nacional de Tecnología Industrial
# License: GPL-3.0
# Project: KiBot (formerly KiPlot)
"""
KiCad v5/6 PCB format.
Currently used only for the paper size
"""
from .sexpdata import load, SExpData
from .v6_sch import _check_str, _check_symbol, _check_is_symbol_list, _check_float
PAGE_SIZE = {'A0': (841, 1189),
             'A1': (594, 841),
             'A2': (420, 594),
             'A3': (297, 420),
             'A4': (210, 297),
             'A5': (148, 210),
             'A': (215.9, 279.4),
             'B': (279.4, 431.8),
             'C': (431.8, 558.8),
             'D': (558.8, 863.6),
             'E': (863.6, 1117.6),
             'USLetter': (215.9, 279.4),
             'USLegal': (215.9, 355.6),
             'USLedger': (279.4, 431.8)}


class PCBError(Exception):
    pass


class PCB(object):
    def __init__(self):
        super().__init__()
        self.paper = 'A4'
        self.paper_portrait = False
        self.paper_w = self.paper_h = 0

    @staticmethod
    def load(file):
        with open(file, 'rt') as fh:
            error = None
            try:
                pcb = load(fh)[0]
            except SExpData as e:
                error = str(e)
            if error:
                raise PCBError(error)
        if not isinstance(pcb, list) or pcb[0].value() != 'kicad_pcb':
            raise PCBError('No kicad_pcb signature')
        o = PCB()
        for e in pcb[1:]:
            e_type = _check_is_symbol_list(e)
            if e_type == 'paper' or e_type == 'page':
                o.paper = _check_str(e, 1, e_type) if e_type == 'paper' else _check_symbol(e, 1, e_type)
                if o.paper == 'User':
                    o.paper_w = _check_float(e, 2, e_type)
                    o.paper_h = _check_float(e, 3, e_type)
                else:
                    if o.paper not in PAGE_SIZE:
                        raise PCBError('Unknown paper size selected {}'.format(o.paper))
                    size = PAGE_SIZE[o.paper]
                    if len(e) > 2 and _check_symbol(e, 2, e_type) == 'portrait':
                        o.paper_portrait = True
                        o.paper_w = size[0]
                        o.paper_h = size[1]
                    else:
                        o.paper_w = size[1]
                        o.paper_h = size[0]
                break
        return o
