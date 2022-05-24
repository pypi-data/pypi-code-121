# -*- coding: utf-8 -*-
# Copyright (c) 2020-2022 Salvador E. Tropea
# Copyright (c) 2020-2022 Instituto Nacional de Tecnología Industrial
# Copyright (c) 2016-2020 Oliver Henry Walters (@SchrodingersGat)
# License: MIT
# Project: KiBot (formerly KiPlot)
# Adapted from: https://github.com/SchrodingersGat/KiBoM
"""
CSV Writer: Generates a CSV, TSV or TXT BoM file.
"""
import csv


def write_stats(writer, cfg):
    if len(cfg.aggregate) == 1:
        # Only one project
        if not cfg.csv.hide_pcb_info:
            prj = cfg.aggregate[0]
            writer.writerow(["Project info:"])
            writer.writerow(["Schematic:", prj.name])
            writer.writerow(["Variant:", cfg.variant.name])
            writer.writerow(["Revision:", prj.sch.revision])
            writer.writerow(["Date:", prj.sch.date])
            writer.writerow(["KiCad Version:", cfg.kicad_version])
        if not cfg.csv.hide_stats_info:
            writer.writerow(["Statistics:"])
            writer.writerow(["Component Groups:", cfg.n_groups])
            writer.writerow(["Component Count:", cfg.total_str])
            writer.writerow(["Fitted Components:", cfg.fitted_str])
            writer.writerow(["Number of PCBs:", cfg.number])
            writer.writerow(["Total Components:", cfg.n_build])
    else:
        # Multiple projects
        if not cfg.csv.hide_pcb_info:
            prj = cfg.aggregate[0]
            writer.writerow(["Project info:"])
            writer.writerow(["Variant:", cfg.variant.name])
            writer.writerow(["KiCad Version:", cfg.kicad_version])
        if not cfg.csv.hide_stats_info:
            writer.writerow(["Global statistics:"])
            writer.writerow(["Component Groups:", cfg.n_groups])
            writer.writerow(["Component Count:", cfg.total_str])
            writer.writerow(["Fitted Components:", cfg.fitted_str])
            writer.writerow(["Number of PCBs:", cfg.number])
            writer.writerow(["Total Components:", cfg.n_build])
        # Individual stats
        for prj in cfg.aggregate:
            if not cfg.csv.hide_pcb_info:
                writer.writerow(["Project info:", prj.sch.title])
                writer.writerow(["Schematic:", prj.name])
                writer.writerow(["Revision:", prj.sch.revision])
                writer.writerow(["Date:", prj.sch.date])
                if prj.sch.company:
                    writer.writerow(["Company:", prj.sch.company])
                if prj.ref_id:
                    writer.writerow(["ID", prj.ref_id])
            if not cfg.csv.hide_stats_info:
                writer.writerow(["Statistics:", prj.sch.title])
                writer.writerow(["Component Groups:", prj.comp_groups])
                writer.writerow(["Component Count:", prj.total_str])
                writer.writerow(["Fitted Components:", prj.fitted_str])
                writer.writerow(["Number of PCBs:", prj.number])
                writer.writerow(["Total Components:", prj.comp_build])


def write_csv(filename, ext, groups, headings, head_names, cfg):
    """
    Write BoM out to a CSV file
    filename = path to output file (must be a .csv, .txt or .tsv file)
    groups = [list of ComponentGroup groups]
    headings = [list of headings to search for data in the BoM file]
    head_names = [list of headings to display in the BoM file]
    cfg = BoMOptions object with all the configuration
    """
    # Delimiter is assumed from file extension
    # Override delimiter if separator specified
    if ext == "csv" and cfg.csv.separator:
        delimiter = cfg.csv.separator
    else:
        if ext == "csv":
            delimiter = ","
        elif ext == "tsv" or ext == "txt":
            delimiter = "\t"

    if cfg.csv.quote_all:
        quoting = csv.QUOTE_ALL
    else:
        quoting = csv.QUOTE_MINIMAL
    with open(filename, "wt") as f:
        writer = csv.writer(f, delimiter=delimiter, lineterminator="\n", quoting=quoting)
        # Headers
        if not cfg.csv.hide_header:
            writer.writerow(head_names)
        # Body
        for group in groups:
            if cfg.ignore_dnf and not group.is_fitted():
                continue
            row = group.get_row(headings)
            writer.writerow(row)
        # PCB info
        if not (cfg.csv.hide_pcb_info and cfg.csv.hide_stats_info):
            # Add some blank rows
            for _ in range(5):
                writer.writerow([])
            # The info
            write_stats(writer, cfg)

    return True
