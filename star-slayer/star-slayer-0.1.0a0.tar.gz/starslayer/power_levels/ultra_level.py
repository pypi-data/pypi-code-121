"""
Ultra Level Module.
"""

from typing import TYPE_CHECKING, List, Optional

from .mega_level import MegaPower
from .power_level import PowerLevel

if TYPE_CHECKING:

    from ..bullets import Bullet
    from ..characters import PlayableCharacter


class UltraPower(PowerLevel):
    """
    Ultra Power Level.
    """

    def shoot_bullets(self,
                      player: "PlayableCharacter",
                      bullets: List["Bullet"]) -> None:
        """
        Shoots ultra bullets..
        """

        player.shoot_ultra_bullets(bullets)


    def next_level(self) -> Optional["PowerLevel"]:
        """
        Returns the next power level to this one.
        """

        return MegaPower()


    @property
    def cooldown(self) -> int:
        """
        Defines the cooldown for shooting bullets.
        """

        return 25


    @property
    def invulnerability(self) -> int:
        """
        Defines the iframes in which the player is immune, when
        it has received damage.
        """

        return 60


    @property
    def name(self) -> str:
        """
        Defines the name of the power level.
        """

        return "Ultra"
