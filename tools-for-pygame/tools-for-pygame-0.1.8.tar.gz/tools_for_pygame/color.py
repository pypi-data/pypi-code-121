#!/usr/bin/env python3

"""
pgt.color

Type: module

Description: a module that contains some color utilities

Functions:
    'add_col(col1, col2)' (list[int]): the same as pygame.BLEND_ADD,
        adds the rgb values of 'col1' and 'col2'
    'sub_col(col1, col2)' (list[int]): the same as pygame.BLEND_SUB,
        subtracts the rgb values of 'col1' and 'col2'
    'mul_col(col1, col2)' (list[int]): the same as pygame.BLEND_MULT,
        multiplies the rgb values of 'col1' and 'col2'
    'min_col(col1, col2)' (list[int]): the same as pygame.BLEND_MIN,
        takes the minimum rgb value of 'col1' and 'col2'
    'max_col(col1, col2)' (list[int]): the same as pygame.BLEND_MAX,
        takes the maximum rgb value of 'col1' and 'col2'
    'calc_alpha(new_color, prev_color, alpha)' (list[int]): returns
        the color that results by putting 'new_color' with an alpha of
        'alpha' onto 'prev_color'
    'GRAY(c)' (tuple[int]): returns a color with all the color channels
        set to 'c'
    'c_alpha(c, a)' (tuple[int]): returns a new color with the same rgb
        values as 'c' and with an alpha 'a'
    'R(c)' (tuple[int]): returns a color with the red channel set to 'c'
    'G(c)' (tuple[int]): returns a color with the green channel set to 'c'
    'B(c)' (tuple[int]): returns a color with the blue channel set to 'c'
"""

from numbers import Real
from typing import List

from .mathf import clamp
from .type_hints import _col_type


def add_col(col1: _col_type, col2: _col_type) -> List[int]:
    return [clamp(c1 + c2, 0, 255) for c1, c2 in zip(col1, col2)]


def sub_col(col1: _col_type, col2: _col_type) -> List[int]:
    return [clamp(c1 - c2, 0, 255) for c1, c2 in zip(col1, col2)]


def mul_col(col1: _col_type, col2: _col_type) -> List[int]:
    return [clamp(c1 * c2, 0, 255) for c1, c2 in zip(col1, col2)]


def min_col(col1: _col_type, col2: _col_type) -> List[int]:
    return [min(c1, c2) for c1, c2 in zip(col1, col2)]


def max_col(col1: _col_type, col2: _col_type) -> List[int]:
    return [max(c1, c2) for c1, c2 in zip(col1, col2)]


def calc_alpha(new_color: _col_type, prev_color: _col_type, alpha: Real) -> List[int]:
    return [alpha * c1 + (1 - alpha) * c2 for c1, c2 in zip(new_color, prev_color)]


c_alpha = lambda c, a: tuple(c[:3]) + (a,)

GRAY = lambda c: (clamp(c, 0, 255), clamp(c, 0, 255), clamp(c, 0, 255), 255)

R = lambda c: (clamp(c, 0, 255), 0, 0, 255)

G = lambda c: (0, clamp(c, 0, 255), 0, 255)

B = lambda c: (0, 0, clamp(c, 0, 255), 255)
