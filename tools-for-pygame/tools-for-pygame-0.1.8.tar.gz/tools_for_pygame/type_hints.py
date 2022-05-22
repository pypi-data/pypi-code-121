#!/usr/bin/env python3

from typing import Union, List, Tuple
from pygame.color import Color
from .mathf import Pos, Size

_col_type = Union[Color, Tuple[int, int, int], Tuple[int, int, int, int], List[int]]

_pos = Union[List[float], Tuple[float, float], Pos, Size, int, float]
_size = _pos
