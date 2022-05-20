"""
Sinusoidal Wave Animation Module.
"""

from math import pi as MATH_PI
from math import sin
from typing import List, Tuple

from ...gamelib import draw_oval
from ...utils import SpringTimer
from .animation import Animation


class SinusoidalWave(Animation):
    """
    An animation for a sinusoidal wave of bullets.
    """

    def __init__(self,
                 x1: float,
                 y1: float,
                 x2: float,
                 y2: float,
                 *,
                 vertical: bool=True,
                 bulge_frequency: int=3,
                 initial_phase: float=0.0,
                 dot_radius: int=5,
                 dot_density: int=1,
                 wave_speed: float=-1.0,
                 translation_speed: float=30.0,
                **kwargs) -> None:
        """
        Initializes an instance of type 'SinusoidalWav'.
        """

        super().__init__(x1, y1, x2, y2, **kwargs)

        self.is_vertical: bool = vertical
        self.is_horizontal: bool = not self.is_vertical
        self.dot_coords: List[Tuple[float, float, float, float]] = []
        self.bulge_frequency: int = bulge_frequency
        self.initial_phase: float = initial_phase
        self.dot_radius: int = dot_radius
        self.dot_density: int = self._validate_density(dot_density)
        self.wave_speed: float = wave_speed
        self.translation_speed: float = translation_speed
        self.translation_timer: SpringTimer = SpringTimer(floor=-100,
                                                          ceiling=10,
                                                          where_to_start=0)

        self.generate_wave()


    def longitude_space_between(self, dots: int) -> float:
        """
        Returns the space between the center of a number of dots
        in the longitude axis.
        """

        return self.longitude / dots


    def amplitude_space_between(self, dots: int) -> float:
        """
        Returns the space between the center of a number of dots
        in the amplitude axis.
        """

        return self.amplitude / dots


    def _validate_density(self, density: int) -> int:
        """
        Checks if the density value is valid, and modifies it if necesessary.
        """

        space_between = self.longitude_space_between(density)
        if space_between < 1:
            density = self.longitude // 2

        return int(density)


    def _correct_float(self, float_num: float) -> float:
        """
        Rounds a float to 3 (three) decimal digits.
        """

        return float(f"{float_num:.3f}")


    @property
    def amplitude(self) -> float:
        """
        Returns the amplitude of the wave.
        """

        return self.x2 - self.x1 if self.is_vertical else self.y2 - self.y1


    @property
    def longitude(self) -> float:
        """
        Returns the longitude of the wave.
        """

        return self.y2 - self.y1 if self.is_vertical else self.x2 - self.x1


    @property
    def translation_coefficient(self) -> float:
        """
        Returns how much to add to simulate a translation.
        """

        return self.translation_timer.current


    def calculate_coords(self, dot_long: int) -> Tuple[float, float]:
        """
        Calculates the coordinates of a dot.
        """

        ampl_aux = ((self.x1 + self.x2) / 2 if self.is_vertical else (self.y1 + self.y2) / 2)
        bulge_aux = 34 / self.bulge_frequency
        phase = (dot_long / (MATH_PI * bulge_aux) + ampl_aux + self.initial_phase
                 - (self.translation_coefficient * self.translation_speed))

        dot_x = dot_long
        dot_y = ((self.amplitude / 2) * sin(phase)) + ampl_aux

        if self.is_vertical:
            dot_x, dot_y = dot_y, dot_x

        return dot_x, dot_y


    def get_hitbox(self, dot_x: float, dot_y: float) -> Tuple[float, float, float, float]:
        """
        Calculates the hitbox of the dot.
        """

        return (dot_x - self.dot_radius,
                dot_y - self.dot_radius,
                dot_x + self.dot_radius,
                dot_y + self.dot_radius)


    def generate_wave(self) -> None:
        """
        Generates the wave and all the dot coords.
        """

        long_aux = (self.y1 if self.is_vertical else self.x1)
        space_between = self.longitude_space_between(self.dot_density)

        for dot_num in range(self.dot_density):
            dot_x, dot_y = self.calculate_coords(dot_num * space_between + long_aux) # long, ampl
            self.dot_coords.append(self.get_hitbox(dot_x, dot_y))


    def animate(self) -> None:
        """
        Proceeds with the animation.
        """

        for x1, y1, x2, y2 in self.dot_coords: # pylint: disable=invalid-name
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

        for coords in self.dot_coords:

            dot_x1, dot_y1, dot_x2, dot_y2 = coords
            dot_y_center = (dot_y1 + dot_y2) / 2
            dot_x_center = (dot_x1 + dot_x2) / 2

            if dot_y1 > self.y2:
                dot_y_center = self.y1

            elif dot_y2 < self.y1:
                dot_y_center = self.y2

            if dot_x1 > self.x2:
                dot_x_center = self.x1

            elif dot_x2 < self.x1:
                dot_x_center = self.x2

            which_to_use = (dot_y_center if self.is_vertical else dot_x_center)

            dot_x, dot_y = self.calculate_coords(which_to_use + self.wave_speed)
            new_dots.append(self.get_hitbox(dot_x, dot_y))

        self.dot_coords = new_dots
        self.translation_timer.count(0.001)
