"""
Bullets with sinusoidal trajectories.
"""

from ..utils import SpringTimer
from .bullet import Bullet, BulletKwargs


class BulletSinusoidalSimple(Bullet):
    """
    A bullet of normal acceleration.
    """

    def __init__(self, **kwargs: BulletKwargs) -> None:
        """
        Initializes an instance of type 'BulletSinusoidalSimple'.
        """

        super().__init__(**kwargs)

        oscillation_time: int = kwargs.get("oscillation_time", 30)
        first_to_right: bool = kwargs.get("first_to_right", True)
        self.oscillatation = SpringTimer(-oscillation_time,
                                         oscillation_time,
                                         (oscillation_time if first_to_right
                                                           else -oscillation_time))


    def trajectory(self) -> None:
        """
        Defines the trajectory of a simple sinusoidal bullet.
        """

        self.oscillatation.count()
        self.transfer((self.oscillatation.current * 0.1) * self.speed, -self.speed)
