"""
Power Level Module.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:

    from ..characters import PlayableCharacter
    from ..bullets import Bullet


class PowerLevel(ABC):
    """
    Class for defining a power level.
    """

    @abstractmethod
    def shoot_bullets(self,
                      player: "PlayableCharacter",
                      bullets: List["Bullet"]) -> None:
        """
        Shoots the bullets it needs.
        """

        ...


    @abstractmethod
    def next_level(self) -> Optional["PowerLevel"]:
        """
        Returns the next power level to this one.
        """

        ...


    @property
    @abstractmethod
    def cooldown(self) -> int:
        """
        Defines the cooldown for shooting bullets.
        """

        ...


    @property
    @abstractmethod
    def invulnerability(self) -> int:
        """
        Defines the iframes in which the player is immune, when
        it has received damage.
        """

        ...


    @property
    @abstractmethod
    def name(self) -> str:
        """
        Defines the name of the power level.
        """

        ...
