"""
Mega Level Module.
"""

from typing import TYPE_CHECKING, List, Optional

from .hyper_level import HyperPower
from .power_level import PowerLevel

if TYPE_CHECKING:

    from ..bullets import Bullet
    from ..characters import PlayableCharacter


class MegaPower(PowerLevel):
    """
    Mega Power Level.
    """

    def shoot_bullets(self,
                      player: "PlayableCharacter",
                      bullets: List["Bullet"]) -> None:
        """
        Shoots mega bullets..
        """

        player.shoot_mega_bullets(bullets)


    def next_level(self) -> Optional["PowerLevel"]:
        """
        Returns the next power level to this one.
        """

        return HyperPower()


    @property
    def cooldown(self) -> int:
        """
        Defines the cooldown for shooting bullets.
        """

        return 20


    @property
    def invulnerability(self) -> int:
        """
        Defines the iframes in which the player is immune, when
        it has received damage.
        """

        return 65


    @property
    def name(self) -> str:
        """
        Defines the name of the power level.
        """

        return "Mega"
