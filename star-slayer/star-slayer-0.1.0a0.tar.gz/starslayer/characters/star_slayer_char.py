"""
Star Slayer character Module.
"""

from typing import TYPE_CHECKING, List

from ..bullets import BulletNormalAcc, BulletSinusoidalSimple
from ..consts import HEIGHT, STAR_SLAYER_REL_PATH, WIDTH
from .playable_character import PlayableCharacter

if TYPE_CHECKING:

    from ..bullets import Bullet


class StarSlayerCharacter(PlayableCharacter):
    """
    The star slayer playable character.

    Its special power resides in ???.
    """

    def __init__(self) -> None:
        """
        Initializes an instance of type 'StarSlayerCharacter'.
        """

        super().__init__(x1=(WIDTH / 2) - 30,
                         y1=(HEIGHT / 1.17) - 30,
                         x2=(WIDTH / 2) + 30,
                         y2=(HEIGHT / 1.17) + 30,
                         how_hard=2,
                         speed=5,
                         texture_path=STAR_SLAYER_REL_PATH)


    def shoot_simple_bullets(self, bullets: List["Bullet"]) -> None:
        """
        Shoots simple bullets.
        """

        player_center_x, _ = self.center

        bullets.append(BulletNormalAcc(x1=player_center_x - 5,
                                       y1=self.y1 + 30,
                                       x2=player_center_x + 5,
                                       y2=self.y1 + 20,
                                       how_hard=self.hardness,
                                       speed=2))


    def shoot_super_bullets(self, bullets: List["Bullet"]) -> None:
        """
        Shoots super bullets.
        """

        player_center_x, _ = self.center

        bullets.append(BulletSinusoidalSimple(x1=player_center_x - 5,
                                              y1=self.y1 + 30,
                                              x2=player_center_x + 5,
                                              y2=self.y1 + 20,
                                              how_hard=self.hardness,
                                              speed=3,
                                              first_to_right=True))



    def shoot_ultra_bullets(self, bullets: List["Bullet"]) -> None:
        """
        Shoots ultra bullets.
        """

        player_center_x, _ = self.center

        bullets.append(BulletSinusoidalSimple(x1=player_center_x - 15,
                                              y1=self.y1 + 30,
                                              x2=player_center_x -5,
                                              y2=self.y1 + 20,
                                              how_hard=self.hardness,
                                              speed=3,
                                              first_to_right=True))
        bullets.append(BulletSinusoidalSimple(x1=player_center_x + 5,
                                              y1=self.y1 + 30,
                                              x2=player_center_x + 15,
                                              y2=self.y1 + 20,
                                              how_hard=self.hardness,
                                              speed=3,
                                              first_to_right=False))


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
