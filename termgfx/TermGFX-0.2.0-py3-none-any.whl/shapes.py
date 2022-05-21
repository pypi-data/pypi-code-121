"""
Different shape implementations
to be used with the engine
"""

from engine import paint
from engine import Canvas

import math

## Types
Size = tuple[int, int]
Pos = tuple[int, int]
Rect = tuple[tuple[str]] | list[list[str]]


## Defaults
BLOCK_CURSOR = "█"
WHITE = "#ffffff"


## Classes
# A base class for all other shapes
class BaseRect:
    def __init__(self, chars: tuple[tuple[str]], pos: Pos = (0, 0), color=WHITE):
        assert max(map(len, chars)) == min(map(len, chars)), "All columns should be the same size"

        self.rect = chars
        self.color = color
        self.pos = pos


    def __str__(self):
        sep = "\n  "  # As for Python 3.10, \'es are not supported in f-strings

        return f"""{type(self).__name__}(
  {sep.join(["".join(line) for line in self.rect])},
color = {self.color}
)"""

    @property
    def size(self):
        return (
            len(self.rect[0]),
            len(self.rect)
        )

    def get_rect(self):
        return self.rect

    def set_pixel(self, pos: Pos, char: str):
        self.rect[pos[1]][pos[0]] = paint(char, self.color)

    def move(self, pos: Pos):
        self.pos = pos

    def draw(self, surface: Canvas):
        assert not any(
                map(
                    lambda l: l[0] > l[1],
                    zip(self.size, surface.size)
                )
            ), "Rect size bigger than canvas"

        for y, line in enumerate(self.rect):
            for x, char in enumerate(line):
                if char != paint(" ", self.color):  # " " imitates alpha/transparent pixels
                    surface.set((x + self.pos[0], y + self.pos[1]), char)


# A rectangular area filled with a single char
class FilledRect(BaseRect):
    def __init__(self, size: Size, char: str = BLOCK_CURSOR, pos: Pos = (0, 0), color=WHITE):
        assert len(char) == 1, "You can pass only a single char"

        self.char = paint(char, color)
        self.color = color
        self.pos = pos

        self.rect = list(list(self.char for _ in range(size[0])) for _ in range(size[1]))


# Class representing lines
class Line(BaseRect):
    def __init__(self, start: Pos, end: Pos, char: str = BLOCK_CURSOR, color=WHITE, algorithm: str = "bresenham"):
        assert algorithm in ("custom", "bresenham"), "Unknown algorighm"

        self.char = char
        self.color = color
        self.rect_size = tuple(map(max, ((start[0], end[0]), (start[1], end[1]))))

        self.start, self.end, self.pos = self.__simplify(start, end)

        exec(f"self.rect = self._construct_{algorithm}(self.start, self.end, self.char)")

    # Simplify the coordinates (And return the offset)
    # TODO: Rewrite to accept `*coords`
    @staticmethod
    def __simplify(start: Pos, end: Pos) -> tuple[Pos, Pos, Pos]:
        # start = (3, 1)
        # end   = (6, 4)
        # | simplify
        # start = (0, 0)
        # end   = (3, 3)

        # WARNING: Entering functional programming realm

        # Zip the coordinates (Split by directions)
        zipped = tuple(zip(start, end))

        # Calculate offset for each
        offset = tuple(map(min, zipped))

        # Subtract mininal cooedinate from each direction
        simplified = tuple(map(
            lambda a: tuple(map(
                lambda b: b[1] - offset[b[0]],  # FIXME
                enumerate(a)
                )),
            (start, end)
        ))

        # Split the coords into positions again
        # (x, x), (y, y) ->
        # -> (x, y), (x, y)
        # start, end = tuple(zip(*simplified))
        start, end = simplified

        return start, end, offset

    # A yet another implementation...
    def _construct_custom(self, start: Pos, end: Pos, char: str):
        """
        y = mx + b
        """

        # Prepare a rect to draw on and return later
        # rect = FilledRect(self.rect_size, " ")
        rect = FilledRect(list(map(lambda x: x + 10, self.rect_size)), " ")

        # Calculate `m` (slope) using `b` equality
        """ Reference:
        { y1 = x1m + b
        { y2 = x2m + b

        { b = y1 - x1m
        { b = y2 - x2m

        y1 - x1m = y2 - x2m

        y1 - y2 = x1m - x2m = m(x1 - x2)

        m = (y1 - y2) / (x1 - x2) (= (y2 - y1) / (x2 - x1), since the signs are mirrored)
        """

        m = (end[1] - start[1]) // (end[0] - start[0])

        # Draw the initial point (`start`)
        rect.rect[start[1]][start[0]] = paint(char, self.color)

        # FIXME
        x, y = start
        if abs(m) < 1:
            while (x, y) != end:
                x += int(math.copysign(1, m))
                y = x//abs(m)

                rect.rect[y][x] = paint(char, self.color)
        else:
            while (x, y) != end:
                x = y//abs(m)
                y += int(math.copysign(1, m))

                rect.rect[y][x] = paint(char, self.color)

        return rect.rect

    def _construct_bresenham(self, start: Pos, end: Pos, char: str = BLOCK_CURSOR):
        # Reference: https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm

        # Calculate the deltas for each coordinate
        delta = {
            "x": end[0] - start[0],
            "y": end[1] - start[1]
        }

        # Prepare a Rect to be filled
        rect = FilledRect(list(map(lambda x: x+1, self.rect_size)), " ", self.color)

        def plot_low(start, end):
            if delta["y"] < 0:
                delta["y"] = -delta["y"]
                yi = -1
            else:
                yi = 1

            error = 2 * delta["y"] - delta["x"]

            y = start[1]

            for x in range(start[0], end[0]+1):
                rect.set_pixel((x, y), char)

                if error > 0:
                    y += yi
                    error += 2 * (delta["y"] - delta["x"])
                else:
                    error += 2 * delta["y"]

        def plot_high(start, end):
            if delta["x"] < 0:
                delta["x"] = -delta["x"]
                xi = -1
            else:
                xi = 1

            error = 2 * delta["x"] - delta["y"]

            x = start[0]

            for y in range(start[1], end[1]+1):
                rect.set_pixel((x, y), char)

                if error > 0:
                    x += xi
                    error += 2 * (delta["x"] - delta["y"])
                else:
                    error += 2 * delta["x"]

        if abs(end[1] - start[1]) < abs(end[0] - start[0]):
            if start[0] > end[0]:
                plot_low(end, start)
            else:
                plot_low(start, end)
        else:
            if start[1] > end[1]:
                plot_high(end, start)
            else:
                plot_high(start, end)


        return rect.get_rect()


class Shape(Line):  # FIXME
    def __init__(self, *vertices: Pos, char: str = BLOCK_CURSOR, color=WHITE, algorithm: str = "bresenham"):
        assert len(vertices) >= 3, "At least 3 vertices should be supplied, otherwise try `shapes.Line`"
        assert vertices[0] != vertices[-1], "Starting vertex shouldn't be repeated in the end"

        self.vertices = tuple(zip(vertices, vertices[1:] + vertices[:1]))
        self.char = char
        self.rect = None

        for start, end in self.vertices:
            exec(f"self.rect = self._construct_{algorithm}({start}, {end}, self.char, self.rect)")
