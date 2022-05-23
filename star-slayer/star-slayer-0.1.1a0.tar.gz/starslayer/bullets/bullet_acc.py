"""
Bullets with normal acceleration.
"""

from ..utils import Timer
from .bullet import Bullet, BulletKwargs


class BulletNormalAcc(Bullet):
    """
    A bullet of normal acceleration.
    """

    def __init__(self,
                 *,
                 oscillation_time: int=30,
                 upwards: bool=True,
                 **kwargs: BulletKwargs) -> None:
        """
        Initializes an instance of type 'BulletNormalAcc'.
        """

        super().__init__(**kwargs)

        self.upwards: bool = upwards
        self.accel_timer = Timer(oscillation_time)


    def trajectory(self) -> None:
        """
        Defines the trajectory of a normal acceleration bullet.
        """

        if self.accel_timer.current_time > 0:
            self.accel_timer.deduct(1)
            self.accel += 0.3

        self.transfer(0, (-1 if self.upwards else 1) * self.speed * self.accel)
