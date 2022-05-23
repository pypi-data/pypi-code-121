#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2019-2021, INRIA
#
# This file is part of Openwind.
#
# Openwind is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Openwind is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openwind.  If not, see <https://www.gnu.org/licenses/>.
#
# For more informations about authors, see the CONTRIBUTORS file

import warnings

"""
Different methods to parse the files
"""

def interpret_data(data):
    """
    Interpret the input data as a list of data.

    It is a very general method.
    If the data is a string  it is supposed to be the name of the file
    containing the data, wich is read by the method ```_read_file```.
    If it is a list, it is return identically.

    Parameters
    ----------
    data : list or string
        List of data or a filename.

    Returns
    -------
    List
        List of raw of data.

    """
    if isinstance(data, list):  # We can chose to take real csv files as inputs
        return data, dict()             # or using directly lists
    else:
        return read_file(data)


def read_file(filename):
    """
    Read file and transcript it in a list of data raw.

    It is a very general method which only read the file, split the
    text w.r. to lines and whitespaces and organise it in a list of list.

    Parameters
    ----------
    filename : string
        The name of the file containing the data.

    Returns
    -------
    raw_parts : List
        List of raw data.

    """
    with open(filename) as file:
        lines = file.readlines()
    raw_parts = parse_lines(lines)
    geom_options = parse_options(lines)
    return raw_parts, geom_options


def parse_lines(lines):
    raw_parts = []
    for line in lines:
        contents = parse_line(line)
        if len(contents) > 0:
            raw_parts.append(contents)
    return raw_parts


def parse_line(line):
    """
    Interpret each line as a list of string.

    Split the lines according to whitespace.
    Anything after a '#' is considered to be a comment

    Parameters
    ----------
    line : string
        A line string.

    Returns
    -------
    List
        List of string obtained from the line.

    """
    # Anything after a '#' is considered to be a comment
    line = line.split('#')[0]

    # Any line starting with '!' is considered to be an option
    if line.startswith('!'):
        return ''
    else:
        # Split the lines according to whitespace
        return line.split()


def parse_opening_factor(s):
    """
    Interpret the opening factor in the fingering chart data.

    Each hole is:
        - open if 'o' or 'open'
        - closed if 'x' or 'closed'
        - semi-closed if '0.5' or '.5'

    Each valve is:
    - 'x' "depressed" or "press down"
    - 'o' "raised" or "open"
    - '0.5' semi-pressed (why not!)

    Parameters
    ----------
    s : string
        string containing the information about the opening

    Returns
    -------
    float
        The opening factor between 0 (entirely closed) and 1 (entirely
        opened)

    """
    opening_factor_from_str = {
            'open': 1, 'o': 1,
            'closed': 0, 'x': 0, 'c': 0,
            '0.5': 0.5, '.5': .5
            }

    if s.lower() in opening_factor_from_str:
        return opening_factor_from_str[s.lower()]

    try:
        # Legacy behavior: 1 is closed, 0 is open
        factor = 1 - float(s)
        warnings.warn("Please use 'o' or 'open' for open holes"
                      " and 'x' or 'closed' for closed")
        return factor
    except ValueError:
        raise ValueError("Invalid string for open/close: {}"
                         .format(s))


def parse_options(lines):
    # get options lines which start with "!"
    options_lines = [s.split('!')[1].split('=') for s in lines if s.startswith('!')]
    geom_options = dict()
    for opt in options_lines:
        if len(opt)<2:
            raise ValueError("The options (line starting with '!') "
                             "must have the format: '! option = value'")
        opt = [s.split()[0] for s in opt]
        geom_options[opt[0]] = opt[1]
    return geom_options
