"""
Circumference Animation Module.
"""

from math import cos, sin
from typing import List, Optional, Tuple

from ...gamelib import draw_oval
from ...utils import SpringTimer
from .animation import Animation


class Circumference(Animation):
    """
    Animation for a circular trajectory.
    """

    def __init__(self,
                 cx: float,
                 cy: float,
                 *,
                 initial_radius: float=50.0,
                 dot_density: int=1,
                 dot_radius: float=5.0,
                 dot_speed: float=0.05,
                 clockwise: bool=False,
                 radius_variance: float=0.0,
                 variance_speed: float=1.0,
                 **kwargs) -> None:
        """
        Initializes an instance of types 'Circumference'.
        """

        super().__init__(cx - initial_radius,
                         cy - initial_radius,
                         cx + initial_radius,
                         cy + initial_radius,
                         **kwargs)
        self.dot_coords: List[Tuple[float, float]] = [] # polar coordinates, mind you
        self.radius: float = initial_radius
        self.dot_density: int = dot_density
        self.dot_raidus: float = dot_radius
        self.dot_speed: float = abs(dot_speed)
        self.clockwise: bool = clockwise
        self.radius_timer: Optional[SpringTimer] = (None
                                                    if not radius_variance
                                                    else SpringTimer(-radius_variance,
                                                                     radius_variance,
                                                                     0))
        self.variance_speed: float = variance_speed

        self.generate_circumference()


    @property
    def angle_density(self) -> float:
        """
        Returns the angle distance between each dot.
        """

        return 360.0 / self.dot_density


    @property
    def current_variance(self) -> float:
        """
        Returns the current radius variance.
        """

        return (0 if not self.radius_timer else self.radius_timer.current)


    def polar_to_cartesian(self, radius: float, theta: float) -> Tuple[float, float]:
        """
        Converts polar coordinates to cartesian ones.
        """

        return radius * cos(theta), radius * sin(theta)


    def generate_dot_coordinates(self, dot_num: int) -> Tuple[float, float]:
        """
        Generates the POLAR coordinates of a dot.
        """

        return self.radius, dot_num * self.angle_density


    def generate_circumference(self) -> None:
        """
        Generates the dots coordinates.
        """

        for dot_num in range(self.dot_density):
            radius, theta = self.generate_dot_coordinates(dot_num)
            self.dot_coords.append((radius, theta))


    def get_hitbox(self, dot_x: float, dot_y: float) -> Tuple[float, float, float, float]:
        """
        Returns the real coordinates to be used in the game screen.
        """

        cart_x, cart_y = self.polar_to_cartesian(dot_x, dot_y)
        return (cart_x - self.dot_raidus + self.center_x,
                cart_y - self.dot_raidus + self.center_y,
                cart_x + self.dot_raidus + self.center_x,
                cart_y + self.dot_raidus + self.center_y)


    # pylint: disable=invalid-name
    def animate(self) -> None:
        """
        Proceeds with the animation.
        """

        for x, y in self.dot_coords:
            x1, y1, x2, y2 = self.get_hitbox(x, y)
            draw_oval(x1=x1,
                      y1=y1,
                      x2=x2,
                      y2=y2,
                      **self.properties)


    def post_hook(self) -> None:
        """
        Moves each dot into its next coords.
        """

        new_dots = []

        for radius, theta in self.dot_coords:
            new_dots.append((radius + self.current_variance,
                             theta + self.dot_speed))

        self.dot_coords = new_dots
        if self.radius_timer:
            self.radius_timer.count(0.1 * self.variance_speed)
