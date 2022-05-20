"""
Generic Module for storing base Entity class.
"""

from typing import Tuple


FloatTuple4 = Tuple[float, float, float, float]
FloatTuple2 = Tuple[float, float]


class HitBox:
    """
    Generic class for defining a bounding box.

    This is a basic class that is not used by itself.
    It serves as superclass of many others.
    """

    def __init__(self, **kwargs: dict[str, int]) -> None:
        """
        Initializes an instance of type '_Entity'.

        It should always be true that 'x1 <= x2 && y1 <= y2'. If
        it is not the case, those variables are inverted.
        """

        # pylint: disable=invalid-name
        x1 = kwargs.get("x1")
        y1 = kwargs.get("y1")
        x2 = kwargs.get("x2")
        y2 = kwargs.get("y2")

        if x1 > x2:

            x1, x2 = x2, x1

        if y1 > y2:

            y1, y2 = y2, y1

        self.x1: float = x1
        self.y1: float = y1
        self.x2: float = x2
        self.y2: float = y2


    def __eq__(self, other: "HitBox") -> bool:
        """
        Tests if all cordinates are the same.
        """

        return all((self.x1 == other.x1,
                    self.y1 == other.y1,
                    self.x2 == other.x2,
                    self.y2 == other.y2))


    @property
    def all_coords(self) -> FloatTuple4:
        """
        Returns a tuple with all the coordiantes of its hitbox.
        """

        return self.x1, self.y1, self.x2, self.y2


    @property
    def upper_left(self) -> FloatTuple2:
        """
        Returns the UPPER LEFT coordinates of its hitbox.
        """

        return self.x1, self.y1


    @property
    def upper_right(self) -> FloatTuple2:
        """
        Returns the UPPER RIGHT coordinates of its hitbox.
        """

        return self.x1, self.y1


    @property
    def bottom_left(self) -> FloatTuple2:
        """
        Returns the BOTTOM LEFT coordinates of its hitbox.
        """

        return self.x1, self.y2


    @property
    def bottom_right(self) -> FloatTuple2:
        """
        Returns the BOTTOM RIGHT coordinates of its hitbox.
        """

        return self.x2, self.y2


    @property
    def center(self) -> FloatTuple2:
        """
        Return the CENTER coordinates of its hitbox.
        """

        return ((self.x2 + self.x1) // 2), ((self.y2 + self.y1) // 2)


    @property
    def width(self) -> int:
        """
        Returns the WIDTH of its hitbox.
        """

        return self.x2 - self.x1


    @property
    def height(self) -> int:
        """
        Returns the HEIGHT of its hitbox.
        """

        return self.y2 - self.y1
