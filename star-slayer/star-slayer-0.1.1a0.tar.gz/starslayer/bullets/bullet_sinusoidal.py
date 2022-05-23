"""
Bullets with sinusoidal trajectories.
"""

from ..utils import SpringTimer
from .bullet import Bullet, BulletKwargs


class BulletSinusoidalSimple(Bullet):
    """
    A bullet of normal acceleration.
    """

    def __init__(self,
                 *,
                 oscillation_time: int=30,
                 first_to_right: bool=True,
                 **kwargs: BulletKwargs) -> None:
        """
        Initializes an instance of type 'BulletSinusoidalSimple'.
        """

        super().__init__(**kwargs)

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
