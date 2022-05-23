"""
Generic Module for storing the HitCircle class.
"""

from math import sqrt
from typing import TYPE_CHECKING

from ...auxiliar import is_out_bounds
from .bounding_shape import FloatTuple2, FloatTuple4, BoundingShape

if TYPE_CHECKING:

    from .hitbox import HitBox


class HitCircle(BoundingShape):
    """
    Generic class for defining a bounding circle.

    This should not be instantiated by itself, rather
    being inherited by others.
    """

    # pylint: disable=invalid-name
    def __init__(self,
                 *,
                 cx: float,
                 cy: float,
                 radius: float,
                 can_spawn_outside: bool=False,
                 **kwargs) -> None:
        """
        Initializes an instance of type 'HitCircle'.
        """

        x1, y1, x2, y2 = self._to_box_coords(cx, cy, radius)

        if (not can_spawn_outside
            and is_out_bounds(x1, y1, x2, y2)):

            raise ValueError(f"Coordinates {x1, y1}, {x2, y2} are not " +
                             "valid, as they are outside of the boundaries of the screen")

        super().__init__(**kwargs)

        self.cx: float = cx
        self.cy: float = cy
        self.radius: float = radius


    def __eq__(self, other: "HitCircle") -> bool:
        """
        Tests if all coordinates are the same.
        """

        return all((self.cx == other.cx,
                    self.cy == other.cy,
                    self.radius == other.radius))


    def _to_box_coords(self, cx: float, cy: float, radius: float) -> FloatTuple4:
        """
        Adds the radius to the center, making it look like it is
        a square bounding box.
        """

        return (cx - radius,
                cy - radius,
                cx + radius,
                cy + radius)


    @property
    def all_coords(self) -> FloatTuple2 | FloatTuple4:
        """
        Returns a tuple with all the coordiantes of its circle.
        """

        return self._to_box_coords(self.cx, self.cy, self.radius)


    @property
    def center(self) -> FloatTuple2:
        """
        Return the CENTER coordinates of its circle.
        """

        return self.cx, self.cy


    def is_over(self, line: float) -> bool:
        """
        Tests if the circle is over a line.
        """

        return (self.cy + self.radius) < line


    def is_left_of(self, line: float) -> bool:
        """
        Tests if the circle is left of a line.
        """

        return (self.cx + self.radius) < line


    def is_right_of(self, line: float) -> bool:
        """
        Tests if the circle is right of a line.
        """

        return (self.cx - self.radius) > line


    def is_below(self, line: float) -> bool:
        """
        Tests if the circle is below a line.
        """

        return (self.cy - self.radius) > line


    def collides_with_box(self, other_box: "HitBox") -> bool:
        """
        Tests if the circle is colliding with another given one.
        """

        test_x = None
        test_y = None

        if self.cx <= other_box.x1:
            test_x = other_box.x1

        elif self.cx >= other_box.x2:
            test_x = other_box.x2

        if self.cy <= other_box.y1:
            test_y = other_box.y1

        elif self.cy >= other_box.y2:
            test_y = other_box.y2

        if not test_x or not test_y: # the circle is inside the square
            return all((other_box.x1 <= self.cx <= other_box.x2,
                        other_box.y1 <= self.cy <= other_box.y2))

        distance_x = self.cx - test_x
        distance_y = self.cy - test_y
        distance = sqrt(distance_x ** 2 + distance_y ** 2)

        return distance <= self.radius


    def collides_with_circle(self, other_circle: "HitCircle") -> bool:
        """
        Tests if the circle is colliding with a HitCircle.
        """

        distance_x = self.cx - other_circle.cx
        distance_y = self.cy - other_circle.cy
        distance = sqrt(distance_x ** 2 + distance_y ** 2)

        return distance <= (self.radius + other_circle.radius)


    def transfer(self, dx: int, dy: int) -> None:
        """
        Changes circle coordinates.
        """

        self.cx += dx
        self.cy += dy


    def move(self, dx: int, dy: int, freely: bool=False) -> bool:
        """
        Moves the circle around inside the boundaries of the screen.

        Returns 'False' if the atempted move is invalid, or 'True' if it is
        valid. Either way, invalid moves are ignored.
        """

        x1, y1, x2, y2 = self.all_coords

        if not freely and is_out_bounds(x1 + dx,
                                        y1 + dy,
                                        x2 + dx,
                                        y2 + dy):
            return False

        self.transfer(dx, dy)
        return True
