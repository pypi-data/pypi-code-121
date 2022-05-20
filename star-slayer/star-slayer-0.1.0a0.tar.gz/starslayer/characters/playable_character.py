"""
Playable Character Module.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

from ..entity import Entity

if TYPE_CHECKING:

    from ..bullets import Bullet


class PlayableCharacter(Entity, ABC):
    """
    Abstract class for defining a playable character.
    """

    @abstractmethod
    def shoot_simple_bullets(self, bullets: List["Bullet"]) -> None:
        """
        Shoots simple bullets.
        """

        ...


    @abstractmethod
    def shoot_super_bullets(self, bullets: List["Bullet"]) -> None:
        """
        Shoots super bullets.
        """

        ...


    @abstractmethod
    def shoot_ultra_bullets(self, bullets: List["Bullet"]) -> None:
        """
        Shoots ultra bullets.
        """

        ...

    @abstractmethod
    def shoot_mega_bullets(self, bullets: List["Bullet"]) -> None:
        """
        Shoots mega bullets.
        """

        ...

    @abstractmethod
    def shoot_hyper_bullets(self, bullets: List["Bullet"]) -> None:
        """
        Shoots hyper bullets.
        """

        ...
