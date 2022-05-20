"""
Super Level Module.
"""

from typing import TYPE_CHECKING, List, Optional

from .power_level import PowerLevel
from .ultra_level import UltraPower

if TYPE_CHECKING:

    from ..bullets import Bullet
    from ..characters import PlayableCharacter


class SuperPower(PowerLevel):
    """
    Super Power Level.
    """

    def shoot_bullets(self,
                      player: "PlayableCharacter",
                      bullets: List["Bullet"]) -> None:
        """
        Shoots super bullets..
        """

        player.shoot_super_bullets(bullets)


    def next_level(self) -> Optional["PowerLevel"]:
        """
        Returns the next power level to this one.
        """

        return UltraPower()


    @property
    def cooldown(self) -> int:
        """
        Defines the cooldown for shooting bullets.
        """

        return 27


    @property
    def invulnerability(self) -> int:
        """
        Defines the iframes in which the player is immune, when
        it has received damage.
        """

        return 57


    @property
    def name(self) -> str:
        """
        Defines the name of the power level.
        """

        return "Super"
