# -*- coding: utf-8 -*-
# Copyright (c) 2022 Salvador E. Tropea
# Copyright (c) 2022 Instituto Nacional de Tecnología Industrial
# License: GPL-3.0
# Project: KiBot (formerly KiPlot)
"""
KiCad 6 color theme loader
"""
import os
import json
from pcbnew import BOARD, PCBNEW_LAYER_ID_START, PCB_LAYER_ID_COUNT
from ..gs import GS
from ..misc import W_COLORTHEME, W_WRONGCOLOR
from .config import KiConf
from .. import log

logger = log.get_logger()
BUILT_IN = {'_builtin_classic', '_builtin_default'}
KI6_KI5 = {'b_adhesive': 'b_adhes',
           'f_adhesive': 'f_adhes',
           'b_silkscreen': 'b_silks',
           'f_silkscreen': 'f_silks',
           'user_drawings': 'dwgs_user',
           'user_comments': 'cmts_user',
           'user_eco1': 'eco1_user',
           'user_eco2': 'eco2_user',
           'b_courtyard': 'b_crtyd',
           'f_courtyard': 'f_crtyd'}
BOARD_COLORS = {'worksheet': 'pcb_frame',
                'pad_through_hole': 'pad_through_hole',
                'via_through': 'via_through',
                'via_blind_buried': 'via_blind_buried',
                'via_micro': 'via_micro'}
CACHE = {}


class KiCadColors(object):
    def __init__(self):
        self.layer_id2color = {}
        self.pcb_frame = "#480000"
        self.pad_through_hole = "#C2C200"
        self.via_through = "#C2C2C2"


def parse_color(val):
    if val.startswith('rgb('):
        vals = val[4:-1].split(',')
    elif val.startswith('rgba('):
        vals = val[5:-1].split(',')
    else:
        logger.warning(W_WRONGCOLOR+"Wrong KiCad color: {}".format(val))
        return "#000000"
    res = '#'
    for c, v in enumerate(vals):
        res += '%02X' % (int(v) if c < 3 else int(float(v)*255))
    return res


def load_color_theme(name):
    logger.debug('Looking for color theme `{}`'.format(name))
    is_built_in = name in BUILT_IN
    if not is_built_in and GS.ki5():
        logger.warning(W_COLORTHEME, "KiCad 5 doesn't support color themes ({})".format(name))
        return None
    if is_built_in:
        fn = os.path.join(os.path.dirname(__file__), '..', 'kicad_colors', name+'.json')
    else:
        KiConf.init(GS.pcb_file)
        fn = os.path.join(KiConf.config_dir, 'colors', name+'.json')
    fn = os.path.abspath(fn)
    global CACHE
    if fn in CACHE:
        return CACHE[fn]
    if not os.path.isfile(fn):
        logger.warning(W_COLORTHEME, "Missing color theme: {}".format(fn))
        return None
    with open(fn, 'rt') as f:
        text = f.read()
    data = json.loads(text)
    c = KiCadColors()
    cl = c.layer_id2color
    board = data['board']
    copper = board['copper']
    extra_debug = GS.debug_level >= 3
    for id in range(PCBNEW_LAYER_ID_START, PCBNEW_LAYER_ID_START+PCB_LAYER_ID_COUNT):
        c_name = c_name_ori = BOARD.GetStandardLayerName(id)
        c_name = c_name.lower()
        if c_name == 'rescue':
            continue
        if c_name.endswith('.cu'):
            c_name = c_name[:-3]
            if c_name in copper:
                cl[id] = parse_color(copper[c_name])
            else:
                logger.warning(W_WRONGCOLOR+"The `{}` theme doesn't define a color for the {} layer".format(name, c_name_ori))
        else:
            c_name = c_name.replace('.', '_')
            c_name = KI6_KI5.get(c_name, c_name)
            if c_name in board:
                cl[id] = parse_color(board[c_name])
            else:
                logger.warning(W_WRONGCOLOR+"The `{}` theme doesn't define a color for the {} layer".format(name, c_name_ori))
        if extra_debug:
            logger.debug('- Color for layer {} ({}): {}'.format(c_name_ori, id, cl[id]))
    # Other colors (Title block and frame color, vias, etc.)
    for color, member in BOARD_COLORS.items():
        if color in board:
            setattr(c, member, parse_color(board[color]))
    CACHE[fn] = c
    return c
