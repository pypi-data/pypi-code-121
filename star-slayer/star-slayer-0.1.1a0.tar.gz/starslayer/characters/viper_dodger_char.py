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

    # pylint: disable=invalid-name
    def __init__(self,
                 *,
                 shooting_cooldown: int=30,
                 invulnerability: int=55,
                 has_shield: bool=False,
                 **kwargs) -> None:
        """
        Initializes an instance of type 'ViperDodgerCharacter'.
        """

        width_aux = WIDTH / 25
        height_aux = HEIGHT / (70 / 3)
        x1 = (WIDTH / 2) - width_aux
        y1 = (HEIGHT / 1.17) - height_aux
        x2 = (WIDTH / 2) + width_aux
        y2 = (HEIGHT / 1.17) + height_aux

        super().__init__(x1=x1,
                         y1=y1,
                         x2=x2,
                         y2=y2,
                         how_hard=1,
                         speed=7,
                         texture_path=VIPER_DODGER_REL_PATH,
                         shooting_cooldown=shooting_cooldown,
                         invulnerability=invulnerability,
                         has_shield=has_shield,
                         shield_x=x2 + width_aux,
                         shield_y=y1 - height_aux,
                         shield_rad=width_aux * 0.8,
                         shield_orbit_center_x=(x1 + x2) / 2,
                         shield_orbit_center_y=(y1 + y2) / 2,
                         **kwargs)


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
