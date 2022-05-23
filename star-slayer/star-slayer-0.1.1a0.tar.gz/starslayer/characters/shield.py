"""
Player Shield Module.
"""

from math import atan2, cos, sin, sqrt

from ..entity import Entity
from ..utils import FloatTuple2, HitCircle


class Shield(Entity, HitCircle):
    """
    Shield for a player.
    """

    def __init__(self,
                 cx: float,
                 cy: float,
                 radius: float,
                 orbit_center_x: float,
                 orbit_center_y: float,
                 **kwargs) -> None:
        """
        Initializes an instance of type 'Shield'.
        """

        super().__init__(cx=cx,
                         cy=cy,
                         radius=radius,
                         health=1000000,
                         how_hard=50,
                         can_spawn_outside=True,
                         **kwargs)

        self.orbit_center_x: float = orbit_center_x
        self.orbit_center_y: float = orbit_center_y
        self.orbit_radius: float = sqrt((orbit_center_x - cx) ** 2 + (orbit_center_y - cy) ** 2)
        self.angle: float = atan2(-cy, cx) # in radians


    @property
    def orbit_center(self) -> FloatTuple2:
        """
        Returns the center of the shield orbit.
        """

        return self.orbit_center_x, self.orbit_center_y


    def change_orbit_center(self, new_x: float, new_y: float) -> None:
        """
        Makes up a new orbit center.
        """

        self.orbit_center_x = new_x
        self.orbit_center_y = new_y


    def polar_to_cart(self, rad: float, theta: float) -> FloatTuple2:
        """
        Converts polar coordinates to cartesian ones.
        """

        return (rad * cos(theta),
                rad * sin(theta))


    def rotate(self, how_much: float) -> None:
        """
        Rotates the shield across the orbit.

        if `how_much` is a negative value it rotates anti-clockwise,
        otherwise it rotates clockwise.
        """

        self.angle += how_much

        new_cx, new_cy = self.polar_to_cart(self.orbit_radius, self.angle)
        self.cx = self.orbit_center_x + new_cx
        self.cy = self.orbit_center_y + new_cy
