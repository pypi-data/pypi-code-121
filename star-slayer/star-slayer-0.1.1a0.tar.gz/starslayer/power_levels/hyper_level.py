"""
Hyper Level Module.
"""

from typing import TYPE_CHECKING, List, Optional

from .power_level import PowerLevel

if TYPE_CHECKING:

    from ..bullets import Bullet
    from ..characters import PlayableCharacter


class HyperPower(PowerLevel):
    """
    Hyper Power Level.
    """

    def shoot_bullets(self,
                      player: "PlayableCharacter",
                      bullets: List["Bullet"]) -> None:
        """
        Shoots hyper bullets..
        """

        player.shoot_hyper_bullets(bullets)


    def next_level(self) -> Optional["PowerLevel"]:
        """
        Returns the next power level to this one.
        """

        return None


    @property
    def cooldown(self) -> int:
        """
        Defines the cooldown for shooting bullets.
        """

        return 15


    @property
    def invulnerability(self) -> int:
        """
        Defines the iframes in which the player is immune, when
        it has received damage.
        """

        return 70


    @property
    def name(self) -> str:
        """
        Defines the name of the power level.
        """

        return "Hyper"
