# -*- coding: utf-8 -*-
# Copyright (c) 2022 Salvador E. Tropea
# Copyright (c) 2022 Instituto Nacional de Tecnología Industrial
# License: GPL-3.0
# Project: KiBot (formerly KiPlot)
# Note about the size:
# A4 landscape 841.889764 x 595.275591 pt = 297 x 210 mm
# 1 pt = 4/3*px  1 px = 1"/96 => 1 pt = 4/3 * 1"/96 = 4"/288 = 1"/72 (72 dpi)
# 1" = 25.4 mm => 1 pt = 25.4/72 mm = 0.3527777778 mm
import re
from .. import log

logger = log.get_logger()


def patch_svg_file(file, remove_bkg=False):
    logger.debug('Patching SVG file `{}`'.format(file))
    with open(file, 'rt') as f:
        text = f.read()
    text = re.sub(r'<svg (.*) width="(.*)" height="(.*)" viewBox="(\S+) (\S+) (\S+) (\S+)"',
                  r'<svg \1 width="\3" height="\2" viewBox="\4 \5 \7 \6"', text)
    if remove_bkg:
        text = re.sub(r'<rect.*>', '', text)
    else:
        text = re.sub(r'<rect x="(\S+)" y="(\S+)" width="(\S+)" height="(\S+)"',
                      r'<rect x="\1" y="\2" width="\4" height="\3"', text)
    with open(file, 'wt') as f:
        f.write(text)
