"""
Viper Dodger character Module.
"""

from typing import TYPE_CHECKING, List

from ..consts import HEIGHT, VIPER_DODGER_REL_PATH, WIDTH
from .playable_character import PlayableCharacter

if TYPE_CHECKING:

    from ..bullets import Bullet


class ViperDodgerCharacter(PlayableCharacter):
    """
    The Viper Dodger playable character.

    Its special power resides in slowing time.
    """

    def __init__(self) -> None:
        """
        Initializes an instance of type 'ViperDodgerCharacter'.
        """

        super().__init__(x1=(WIDTH / 2) - 30,
                         y1=(HEIGHT / 1.17) - 30,
                         x2=(WIDTH / 2) + 30,
                         y2=(HEIGHT / 1.17) + 30,
                         how_hard=1,
                         speed=7,
                         texture_path=VIPER_DODGER_REL_PATH)


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
