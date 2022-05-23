"""
Generic Module for defining an abstract class
for a bounding shape.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:

    from .hitbox import HitBox
    from .hitcircle import HitCircle

FloatTuple4 = Tuple[float, float, float, float]
FloatTuple2 = Tuple[float, float]


# pylint: disable=invalid-name
class BoundingShape(ABC):
    """
    Generic class for a bounding polygon.
    """

    def __init__(self, **kwargs) -> None:
        """
        Saves the properties of the shape.
        """

        self.properties = kwargs


    @abstractmethod
    def __eq__(self, other: "BoundingShape") -> bool:
        """
        Tests if all coordinates are the same.
        """

        raise NotImplementedError


    @property
    @abstractmethod
    def all_coords(self) -> FloatTuple2 | FloatTuple4:
        """
        Returns a tuple with all the coordiantes of its shape.
        """

        raise NotImplementedError


    @property
    @abstractmethod
    def center(self) -> FloatTuple2:
        """
        Return the CENTER coordinates of its shape.
        """

        raise NotImplementedError


    @abstractmethod
    def is_over(self, line: float) -> bool:
        """
        Tests if the shape is over a line.
        """

        raise NotImplementedError


    @abstractmethod
    def is_left_of(self, line: float) -> bool:
        """
        Tests if the shape is left of a line.
        """

        raise NotImplementedError


    @abstractmethod
    def is_right_of(self, line: float) -> bool:
        """
        Tests if the shape is right of a line.
        """

        raise NotImplementedError


    @abstractmethod
    def is_below(self, line: float) -> bool:
        """
        Tests if the shape is below a line.
        """

        raise NotImplementedError


    @abstractmethod
    def collides_with_box(self, other_box: "HitBox") -> bool:
        """
        Tests if the shape is colliding with another given one.
        """

        raise NotImplementedError


    @abstractmethod
    def collides_with_circle(self, other_circle: "HitCircle") -> bool:
        """
        Tests if the shape is colliding with a HitCircle.
        """

        raise NotImplementedError


    @abstractmethod
    def transfer(self, dx: int, dy: int) -> None:
        """
        Changes shape coordinates.
        """

        raise NotImplementedError


    @abstractmethod
    def move(self, dx: int, dy: int, freely: bool=False) -> bool:
        """
        Moves the shape around inside the boundaries of the screen.

        Returns 'False' if the atempted move is invalid, or 'True' if it is
        valid. Either way, invalid moves are ignored.
        """

        raise NotImplementedError
