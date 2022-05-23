"""
Playable Character Module.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generator, List, Optional

from ..entity import Entity
from ..utils import HitBox, Timer
from .shield import Shield

if TYPE_CHECKING:

    from ..bullets import Bullet


class PlayableCharacter(Entity, HitBox, ABC):
    """
    Abstract class for defining a playable character.
    """

    def __init__(self,
                 *,
                 shooting_cooldown: int=30,
                 invulnerability: int=55,
                 has_shield: bool=False,
                 shield_x: Optional[float]=None,
                 shield_y: Optional[float]=None,
                 shield_rad: Optional[float]=None,
                 shield_orbit_center_x: Optional[float]=None,
                 shield_orbit_center_y: Optional[float]=None,
                 **kwargs) -> None:
        """
        Initializes an instance of type 'PlayableCharacter'.
        """

        super().__init__(**kwargs)
        self.shooting_cooldown: Timer = Timer(shooting_cooldown)
        self.invulnerability: Timer = Timer(invulnerability)

        if has_shield and any((shield_x is None,
                               shield_y is None,
                               shield_rad is None,
                               shield_orbit_center_x is None,
                               shield_orbit_center_y is None)):
            raise ValueError("If the character has a shield, the its coordinates must be present.")

        self.shield: Optional[Shield] = (None
                                         if not has_shield
                                         else Shield(cx=shield_x,
                                                     cy=shield_y,
                                                     radius=shield_rad,
                                                     orbit_center_x=shield_orbit_center_x,
                                                     orbit_center_y=shield_orbit_center_y))


    def change_cooldown(self, new_cooldown: int) -> None:
        """
        Changes the shooting cooldown, for example when it
        powers up.
        """

        self.shooting_cooldown = Timer(new_cooldown)


    def change_invulnerability(self, new_invulnerability: int) -> None:
        """
        Changes the shooting invulnerability, for example when it
        powers up.
        """

        self.invulnerability = Timer(new_invulnerability)


    def get_timers(self) -> Generator[Timer, None, None]:
        """
        Yields each timer that the player has.
        """

        yield self.shooting_cooldown
        yield self.invulnerability


    @abstractmethod
    def shoot_simple_bullets(self, bullets: List["Bullet"]) -> None:
        """
        Shoots simple bullets.
        """

        raise NotImplementedError


    @abstractmethod
    def shoot_super_bullets(self, bullets: List["Bullet"]) -> None:
        """
        Shoots super bullets.
        """

        raise NotImplementedError


    @abstractmethod
    def shoot_ultra_bullets(self, bullets: List["Bullet"]) -> None:
        """
        Shoots ultra bullets.
        """

        raise NotImplementedError


    @abstractmethod
    def shoot_mega_bullets(self, bullets: List["Bullet"]) -> None:
        """
        Shoots mega bullets.
        """

        raise NotImplementedError


    @abstractmethod
    def shoot_hyper_bullets(self, bullets: List["Bullet"]) -> None:
        """
        Shoots hyper bullets.
        """

        raise NotImplementedError


    def move(self, dx: int, dy: int, freely: bool=False) -> bool:
        """
        Moves the chracter around inside the boundaries of the screen,
        along with its shield.
        """

        did_move = super().move(dx, dy)

        if self.shield and did_move:
            new_cx, new_cy = self.center
            self.shield.change_orbit_center(new_cx, new_cy)
            self.shield.move(dx, dy, freely=True)

        return did_move
