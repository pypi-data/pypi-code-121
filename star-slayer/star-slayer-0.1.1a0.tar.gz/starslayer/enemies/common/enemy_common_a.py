"""
Common Enemy A Module.
"""

from typing import TYPE_CHECKING

from ...bullets import BulletNormalAcc
from ...entity import ShipDict
from ...utils import Timer
from ..enemy import Enemy

if TYPE_CHECKING:

    from ...state import BulletsList

class EnemyCommonA(Enemy):
    """
    A common enemy (A version).
    """

    def __init__(self,
                 *,
                 health=3,
                 how_hard=5,
                 speed=3,
                 internal_timer_initial: int=30,
                 initial_direction: int=0, # 0 for "LEFT", 1 for "DOWN" and 2 for "RIGHT"
                 shooting_cooldown=200,
                 **kwargs: ShipDict) -> None:
        """
        Initializes an instance of type 'EnemyCommonA'.
        """

        super().__init__(health=health,
                         how_hard=how_hard,
                         speed=speed,
                         shooting_cooldown=shooting_cooldown,
                         **kwargs)

        self.internal_timer: Timer = Timer(internal_timer_initial)
        self.direction: int = initial_direction


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


    def shoot_bullets(self, bullets: "BulletsList") -> None:
        """
        Shoots the bullets specially made for this enemy.
        """

        center_x, center_y = self.center

        bullets.append(BulletNormalAcc(cx=center_x,
                                       cy=center_y + 15,
                                       radius=5,
                                       how_hard=self.hardness,
                                       upwards=False,
                                       can_spawn_outside=True))
