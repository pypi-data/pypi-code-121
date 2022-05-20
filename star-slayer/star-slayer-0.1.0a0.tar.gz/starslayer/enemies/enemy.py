"""
Generic Enemy class module.
"""

from abc import ABC, abstractmethod

from ..entity import Entity


class Enemy(Entity, ABC):
    """
    Class for defining a NPC ship that attacks
    the player.
    """

    default: "Enemy"
    types: dict[str: "Enemy"]

    def __init_subclass__(cls) -> None:
        """
        Registers sublcasses into an internal list.
        """

        try:

            Enemy.types[cls.__name__] = cls

        except AttributeError:

            Enemy.default = cls
            Enemy.types = {cls.__name__: cls}


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
