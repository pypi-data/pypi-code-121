from __future__ import annotations

from enum import Enum
from functools import cached_property


class BoardVector:
    def __init__(self, x, y):
        self._x: int = x
        self._y: int = y

    def __eq__(self, other):
        if isinstance(other, BoardVector):
            return self.x == other.x and self.y == other.y
        return False

    def __hash__(self):
        return hash((self.x, self.y))

    def __add__(self, other: BoardVector):
        return BoardVector(self.x + other.x, self.y + other.y)

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return f"vector({self.x}, {self.y})"

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    @cached_property
    def adjacent(self):
        return tuple(self + d.vector for d in Direction)

    @cached_property
    def neighboring(self):
        return tuple(self + d.vector for d in Direction if d.cardinal)

    def pair(self) -> tuple[int, int]:
        return self.x, self.y


vector = BoardVector  # alias for BoardVector


class Direction(Enum):
    N = 0
    NE = 1
    E = 2
    SE = 3
    S = 4
    SW = 5
    W = 6
    NW = 7

    @cached_property
    def vector(self):
        if "E" in self.name:
            xd = 1
        elif "W" in self.name:
            xd = -1
        else:
            xd = 0

        if "N" in self.name:
            yd = -1
        elif "S" in self.name:
            yd = 1
        else:
            yd = 0

        return vector(xd, yd)

    @cached_property
    def inverse(self):
        return self - 4

    @cached_property
    def degree(self):
        return 45 * self.value

    @cached_property
    def cardinal(self):
        return len(self.name) == 1

    def __add__(self, other: int):
        return Direction((self.value + other) % 8)

    def __sub__(self, other: int):
        return Direction((self.value - other) % 8)
