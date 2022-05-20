"""
Enemies Module. Contains the different types
of hostiles.
"""

from ..utils import Timer, SpringTimer
from ..entity import ShipDict
from .enemy import Enemy


class EnemyCommonA(Enemy):
    """
    A common enemy (A version).
    """

    def __init__(self, **kwargs: ShipDict) -> None:
        """
        Initializes an instance of type 'EnemyCommonA'.
        """

        # kwargs.update({"texture_path": "enemies/common_a"})
        super().__init__(**kwargs)

        self.hp = 3 #pylint: disable=invalid-name
        self.hardness = 10
        self.speed = 3

        self.internal_timer = Timer(30)
        self.direction = 0 # 0 for "LEFT", 1 for "DOWN" and 2 for "RIGHT"


    def trajectory(self) -> None:
        """
        Defines the movement of a common enemy (A version).
        """

        if self.internal_timer.is_zero_or_less():

            self.direction = (self.direction + 1) % 3
            self.internal_timer.reset()

        else:

            self.internal_timer.deduct(1)

        self.transfer((-self.speed if self.direction == 0
                                   else (self.speed if self.direction == 2 else 0)),
                      ((self.speed // 2) if self.direction == 1 else 0))


class EnemyCommonB(Enemy):
    """
    A common enemy (B version).
    """

    def __init__(self, **kwargs: ShipDict) -> None:
        """
        Initializes an instance of type 'EnemyCommonB'.
        """

        # kwargs.update({"texture_path": "enemies/common_b"})
        super().__init__(**kwargs)

        self.hp = 3
        self.hardness = 10
        self.speed = 3

        self.internal_timer = SpringTimer(0, 30, 30)
        self.direction = 0 # 0 for "LEFT", 1 for "DOWN" and 2 for "RIGHT"


    def trajectory(self) -> None:
        """
        Defines the movement of a common enemy (B version).
        """

        if self.internal_timer.current == self.internal_timer.floor:

            self.direction += 1

        elif self.internal_timer.current == self.internal_timer.ceil:

            self.direction -= 1

        elif self.internal_timer.current == self.internal_timer.ceil // 2:

            if self.internal_timer.adding:

                self.direction = (self.direction + 1) % 3

            else:

                self.direction = (self.direction + 2) % 3

        self.internal_timer.count()

        self.transfer((-self.speed if self.direction == 0
                                   else (self.speed if self.direction == 2 else 0)),
                      ((self.speed // 2) if self.direction == 1 else 0))
