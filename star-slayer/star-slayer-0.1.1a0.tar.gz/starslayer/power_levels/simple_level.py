"""
Simple Level Module.
"""

from typing import TYPE_CHECKING, List, Optional

from .power_level import PowerLevel
from .super_level import SuperPower

if TYPE_CHECKING:

    from ..bullets import Bullet
    from ..characters import PlayableCharacter


class SimplePower(PowerLevel):
    """
    Simple Power Level.
    """

    def shoot_bullets(self,
                      player: "PlayableCharacter",
                      bullets: List["Bullet"]) -> None:
        """
        Shoots simple bullets..
        """

        player.shoot_simple_bullets(bullets)


    def next_level(self) -> Optional["PowerLevel"]:
        """
        Returns the next power level to this one.
        """

        return SuperPower()


    @property
    def cooldown(self) -> int:
        """
        Defines the cooldown for shooting bullets.
        """

        return 30


    @property
    def invulnerability(self) -> int:
        """
        Defines the iframes in which the player is immune, when
        it has received damage.
        """

        return 55


    @property
    def name(self) -> str:
        """
        Defines the name of the power level.
        """

        return "Simple"
