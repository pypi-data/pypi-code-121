#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" """
# import pandas as pd
import string
import numpy as np
from copy import deepcopy
#import datetime

def screen(row, col, maxwell, **kwargs):
    """
    Create a screen with global parameters

    Parameters
    ----------
    row : string
        Parameter encoded by the row letter
    col : string
        Parameter encoded by the column number
    maxwell : string
        Name of the well in the bottom-right corner of each tray, e.g. 'H6'
    **kwargs : any type
        Any named arguments become global parameters to be applied to all wells in all trays in the screen

    Returns
    -------
    screen : dict
        A dictionary containing the screen

    """
    # make sure maxwell is properly formatted
    if len(maxwell) != 2:
        raise ValueError(f'maxwell must have length 2, supplied {maxwell} has length {len(maxwell)}')
    elif not maxwell[0].isalpha():
        raise ValueError(f'first character of maxwell must be a letter, supplied {maxwell} has first character {maxwell[0]}')
    elif not maxwell[1].isdigit():
        raise ValueError(f'second character of maxwell must be a number, supplied {maxwell} has second character {maxwell[1]}')


    screen = {"row": row, "col": col, "maxwell": maxwell}

    screen["statics"] = {}

    for key, value in kwargs.items():
        screen["statics"][key] = value

    return screen


def tray(screen=None, rows=None, cols=None, ss=None, **kwargs):
    """
    Create a tray, based on a screen and row/column specifications

    Parameters
    ----------
    screen : dict
        Screen from which the tray inherits global parameters
    rows : list or float
        Value(s) to be used as row specifications. Must be a single number, a list of two numbers, or a list of length matchng the number of rows.
    cols : list or float
        Value(s) to be used as column specifications. Must be a single number, a list of two numbers, or a list of length matching the number of columns.
    **kwargs : any type
        Set any named parameters to apply them to all wells in the tray

    Returns
    -------
    tray : dict
        Dictionary to be passed to well() for logging hits from this tray

    """

    tray = deepcopy(screen)

    tray["statics"].update(kwargs)

    tray = setrows(tray, rows)
    tray = setcols(tray, cols)

    return tray


def clonetray(oldtray, **kwargs):
    """
    Copy a tray, overriding parameters as desired

    Parameters
    ----------
    oldtray : dict
        Tray to be copied
    **kwargs : any type
        Accepts all arguments accepted by tray(), including rows and cols.
        Any parameters extant in oldtray not specified here will be copied into newtray

    Returns
    -------
    newtray : dict
        Dictionary to be passed to well() for logging hits from this tray

    """

    newtray = deepcopy(oldtray)

    rows = kwargs.pop("rows", None)
    if rows is not None:
        newtray = setrows(newtray, rows)

    cols = kwargs.pop("cols", None)
    if cols is not None:
        newtray = setcols(newtray, cols)

    newtray["statics"].update(kwargs)


    return newtray


def setrows(tray, *args):
    """
    Set values encoded by row names, e.g. the values static across each row

    Parameters
    ----------
    tray : dict
        Tray to which rows will be added.
    *args : list or float
        Row values can be passed as one number to apply to all rows,
        numrows numbers to map directly to rows, or
        two numbers to create an evenly spaced gradient across the rows

    Returns
    -------
    screen : dict
        Screen containing the tray to which rows have been added

    """

    numrows = string.ascii_uppercase.find(tray["maxwell"][0]) + 1

    rownames = [i for i in string.ascii_uppercase[:numrows]]

    rowdata = rowcolparser(numrows, "rows", args)

    for name, data in zip(rownames, rowdata):
        tray[name] = data

    return tray


def setcols(tray, *args):
    """
    Set values encoded by column names, e.g. the values static down each column

    Parameters
    ----------
    tray : dict
        Tray to which columns will be added.
    *args : list or float
        Column values can be passed as one number to apply to all columns,
        numcols numbers to map directly to columns, or
        two numbers to create an evenly spaced gradient across the columns

    Returns
    -------
    screen : dict
        Screen containing the tray to which columns have been added

    """

    numcols = int(tray["maxwell"][1])

    colnames = [str(i) for i in range(1, numcols + 1)]

    coldata = rowcolparser(numcols, "column", args)

    for name, data in zip(colnames, coldata):
        tray[name] = data

    return tray


def rowcolparser(n, which, *args):
    """
    Helper function not exported
    """

    if len(args) == n:
        data = args
    elif len(args) == 2:
        data = np.linspace(args[0], args[1], n)
    elif len(args) == 1:
        if type(args[0]) is int or type(args[0]) is float:
            data = [args[0]] * n
        elif len(args[0]) == n:
            data = args[0]
        elif len(args[0]) == 2:
            data = np.linspace(args[0][0], args[0][1], n)
        elif len(args[0]) == 1:
            if type(args[0][0]) is int or type(args[0][0]) is float:
                data = [args[0][0]] * n
            elif len(args[0][0]) == n:
                data = args[0][0]
            elif len(args[0][0]) == 2:
                data = np.linspace(args[0][0][0], args[0][0][1], n)
            elif len(args[0][0]) == 1:
                data = args[0][0] * n
                # print(data)
            else:
                raise ValueError(f"Unexpected {which} specification")

    return data


def main():

    screen1 = screen("protein", "PEG", "H6", construct="wt DHFR")

    tray1 = tray(screen1, rows=3, cols=[4, 5], date='2021-01-01')
    # tray1 = setrows(tray1, 3)
    # screen1 = setrows(screen1, 'DB1', [3])

    # screen1 = tray(screen1, 'DB2', rows = [1,8], cols = [1, 2, 3, 4, 5, 6])
    # screen1 = setrows(screen1, 'DB2', 1, 8)
    # screen1 = setcols(screen1, 'DB2', 1,2,3,4,5,8)

    # screen1 = newtray(screen1, 'DB1', date='2021', rows = [10])

    # screen1 = setrows(screen1, 'DB1', 3)
    # screen1 = setcols(screen1, 'DB1', 4, 9)

    tray2 = clonetray(tray1, rows=[3, 5])
    # screen1 = setrows(screen1, 'DB2', [1,2,3,5,6.7,5.5,1,16])

    print(tray2)

    return


if __name__ == "__main__":
    main()
