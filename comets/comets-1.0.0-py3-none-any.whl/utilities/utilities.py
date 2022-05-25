# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.


def to_list(variable):
    if type(variable) == list:
        return variable
    else:
        return [variable]


def check_size(variable):
    """
    Checks value of "size" input value in a variable, distribution or generator
    """
    if "size" in variable:
        if not isinstance(variable['size'], int):
            raise ValueError("Size should be an integer")
        if variable['size'] < 1:
            raise ValueError('Size should be positive')


# compute the next_multiple >= value for which next_multiple%divider = 0
def next_multiple(value, divider):
    if value % divider == 0:
        next_multiple = value
    else:
        next_multiple = divider * (value // divider + 1)
    return next_multiple
