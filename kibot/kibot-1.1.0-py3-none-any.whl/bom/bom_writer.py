# -*- coding: utf-8 -*-
# Copyright (c) 2020 Salvador E. Tropea
# Copyright (c) 2020 Instituto Nacional de Tecnología Industrial
# Copyright (c) 2016-2020 Oliver Henry Walters (@SchrodingersGat)
# License: MIT
# Project: KiBot (formerly KiPlot)
# Adapted from: https://github.com/SchrodingersGat/KiBoM
"""
BoM Writer.

This is just a hub that calls the real BoM writer:
- csv_writer.py
- html_writer.py
- xml_writer.py
- xlsx_writer.py
"""
from .csv_writer import write_csv
from .html_writer import write_html
from .xml_writer import write_xml
from .xlsx_writer import write_xlsx
from .. import log

logger = log.get_logger()


def write_bom(filename, ext, groups, headings, cfg):
    """
    Write BoM to file
    filename = output file path (absolute)
    groups = [list of ComponentGroup groups]
    headings = [list of fields to use as columns]
    cfg = configuration data
    """
    # Allow renaming the columns
    head_names = [h if h.lower() not in cfg.column_rename else cfg.column_rename[h.lower()] for h in headings]
    headings = [h.lower() for h in headings]
    result = False
    # CSV file writing
    if ext in ["csv", "tsv", "txt"]:
        result = write_csv(filename, ext, groups, headings, head_names, cfg)
    elif ext in ["htm", "html"]:
        result = write_html(filename, groups, headings, head_names, cfg)
    elif ext in ["xml"]:
        result = write_xml(filename, groups, headings, head_names, cfg)
    elif ext in ["xlsx"]:
        result = write_xlsx(filename, groups, headings, head_names, cfg)

    if result:
        logger.debug("{} Output -> {}".format(ext.upper(), filename))
    else:
        logger.error("writing {} output".format(ext.upper()))

    return result
