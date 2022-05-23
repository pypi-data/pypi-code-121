"""
Generic Enemy class module.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict

from ..entity import Entity
from ..utils import HitBox, Timer

if TYPE_CHECKING:

    from ..state import BulletsList


class Enemy(Entity, HitBox, ABC):
    """
    Class for defining a NPC ship that attacks
    the player.
    """

    default: "Enemy"
    types: Dict[str, "Enemy"]

    def __init_subclass__(cls) -> None:
        """
        Registers sublcasses into an internal list.
        """

        try:

            Enemy.types[cls.__name__] = cls

        except AttributeError:

            Enemy.default = cls
            Enemy.types = {cls.__name__: cls}


    def __init__(self,
                 *,
                 shooting_cooldown: int=300,
                 **kwargs) -> None:
        """
        Initializes an instance of type 'Enemy'.
        """

        super().__init__(**kwargs)

        self._shooting_cooldown: int = Timer(shooting_cooldown)


    def __contains__(self, enemy: "Enemy") -> bool:
        """
        Returns if a specified enemy type is present.
        """

        return enemy in Enemy.types.values()


    @abstractmethod
    def trajectory(self) -> None:
        """
        Abstract method for sub-class responsability enforcement.
        """

        raise NotImplementedError


    @property
    def shooting_cooldown(self) -> Timer:
        """
        The shooting cooldown of the enemy.
        """

        return self._shooting_cooldown


    def shoot(self, bullets: "BulletsList") -> None:
        """
        Tries to fire bullets.
        """

        self.shooting_cooldown.deduct(1)

        if not self.shooting_cooldown.is_zero_or_less():
            return

        self.shoot_bullets(bullets)
        self.shooting_cooldown.reset()


    def shoot_bullets(self, _bullets: "BulletsList") -> None:
        """
        Shoots the bullets specially made for this enemy.
        It is recommended to inherit this method to be useful.
        """

        return None
