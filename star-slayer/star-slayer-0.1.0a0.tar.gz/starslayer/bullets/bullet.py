"""
Bullets Module. Here are stored the classes for the
different types of bullets.
"""

from abc import ABC, abstractmethod
from typing import Optional

from ..entity import Entity

BulletKwargs = dict[str, Optional[int | str | bool]]


class Bullet(Entity, ABC):
    """
    Class for defining a bullet that is shot
    from a ship, enemy or not.
    """

    def __init__(self, **kwargs: BulletKwargs) -> None:
        """
        Initializes an instance of type 'Bullet'.
        """

        # Defining default types
        if kwargs.get("health", None) is None:
            kwargs["health"] = 10

        super().__init__(**kwargs)
        self.accel: int = kwargs.get("acceleration", 1)


    @abstractmethod
    def trajectory(self) -> None:
        """
        Defines the trajectory of the bullet.
        """

        ...
