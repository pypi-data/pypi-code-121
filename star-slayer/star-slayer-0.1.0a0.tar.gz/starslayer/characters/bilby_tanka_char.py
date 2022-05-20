"""
Bilby Tanka character Module.
"""

from typing import TYPE_CHECKING, List

from ..consts import BILBY_TANKA_REL_PATH, HEIGHT, WIDTH
from .playable_character import PlayableCharacter

if TYPE_CHECKING:

    from ..bullets import Bullet


class BilbyTankaCharacter(PlayableCharacter):
    """
    The Bilby Tanka playable character.

    Its special power resides in a very powerful bomb.
    """

    def __init__(self) -> None:
        """
        Initializes an instance of type 'BilbyTankaCharacter'.
        """

        super().__init__(x1=(WIDTH / 2) - 30,
                         y1=(HEIGHT / 1.17) - 30,
                         x2=(WIDTH / 2) + 30,
                         y2=(HEIGHT / 1.17) + 30,
                         how_hard=5,
                         speed=2,
                         texture_path=BILBY_TANKA_REL_PATH)


    def shoot_simple_bullets(self, bullets: List["Bullet"]) -> None:
        """
        Shoots simple bullets.
        """

        ...


    def shoot_super_bullets(self, bullets: List["Bullet"]) -> None:
        """
        Shoots super bullets.
        """

        ...



    def shoot_ultra_bullets(self, bullets: List["Bullet"]) -> None:
        """
        Shoots ultra bullets.
        """

        ...


    def shoot_mega_bullets(self, bullets: List["Bullet"]) -> None:
        """
        Shoots mega bullets.
        """

        ...


    def shoot_hyper_bullets(self, bullets: List["Bullet"]) -> None:
        """
        Shoots hyper bullets.
        """

        ...
