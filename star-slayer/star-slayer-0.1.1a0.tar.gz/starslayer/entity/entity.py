"""
Characters Module. For storing playable characters
(mainly the player).
"""

from typing import Dict, Optional

from ..sprites import Sprite

ShipVariable = Optional[float | int | str]
ShipDict = Dict[str, ShipVariable]


class Entity:
    """
    Class for defining an entity.
    An entity is a hitbox with health, speed and other
    extra attributes.
    """

    def __init__(self,
                 *,
                 health: int=100,
                 how_hard: int=0,
                 speed: int=1,
                 texture_path: Optional[str]=None,
                  **kwargs: ShipDict) -> None:
        """
        Initializes an instance of type 'Ship'.

        Kwargs:

        `max_hp` is the maximum health points to be had.
        `how_hard` is the defence stat.
        `speed` is the speed of the entity movement.
        `texture_path` is the sprites path, and must be a path
                      relative to the 'textures' package.
        """

        # This here works only if Entity is before a bounding shape in the MRO
        super().__init__(**kwargs)

        self.max_hp: int = health
        self.hp: int = self.max_hp #pylint: disable=invalid-name
        self.hardness: int = how_hard
        self.speed: int = speed
        self.sprite_path: Optional[str] = texture_path
        self.sprite: Optional[Sprite] = (Sprite(self.sprite_path) if self.sprite_path else None)


    def __str__(self) -> str:
        """
        Returns a string with class information so it can be printed later.
        """

        return (f"health: {self.hp} - " +
                f"hardness: {self.hardness} - speed: {self.speed} - sprite: {self.sprite_path}")


    def __repr__(self) -> str:
        """
        Returns a string with class information so it can be parsed 'as is' later.
        """

        return self.__str__()


    def has_no_health(self) -> bool:
        """
        Returns 'True' if if the ship has 0 health points or less, and 'False' otherwise.
        """

        return self.hp <= 0


    def health_percentage(self) -> float:
        """
        Calculates the percentage of the remaining health.
        """

        return (self.hp / self.max_hp) * 100


    def take_damage(self, how_much: int) -> None:
        """
        Process damage taken.
        """

        self.hp -= how_much

        if self.hp < 0:
            self.die()


    def die(self) -> None:
        """
        Drops the health points to zero.
        """

        self.hp = 0
