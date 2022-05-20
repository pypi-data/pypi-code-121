"""
Characters Selection Menu Module.
"""

from typing import TYPE_CHECKING

from ....auxiliar import Singleton
from ....characters import (BilbyTankaCharacter, StarSlayerCharacter,
                            ViperDodgerCharacter)
from ....checks import left_click, on_press
from ....consts import HEIGHT, WIDTH
from ...hitbox import FloatTuple4
from ...menu import ButtonKwargs, Menu, MenuDict

if TYPE_CHECKING:
    from ....scene import Scene
    from ....state import Game
    from ...button import Button


__all__ = ["CharactersMenu"] # We DON'T want the local variable 'charactersmenu' to be exported


class CharactersMenu(Menu, metaclass=Singleton):
    """
    The characters selection menu of the game.
    """

    def __init__(self,
                 area_corners: FloatTuple4=(
                    int((WIDTH / 9) - (WIDTH * 0.08)),
                    int(HEIGHT * 0.87),
                    int((WIDTH / 9) * 8 + (WIDTH * 0.08)),
                    int(HEIGHT * 0.97)
                 ),
                 **kwargs: MenuDict) -> None:
        """
        Initializes an instance of 'CharactersMenu'.
        """

        super().__init__(area_corners, **kwargs)


charactersmenu = CharactersMenu() # instantiated temporarily

@charactersmenu.button(message="Star Slayer",
                       x1=int((WIDTH / 9) - (WIDTH * 0.08)),
                       y1=int(HEIGHT * 0.87),
                       x2=int((WIDTH / 9) * 1.7 + (WIDTH * 0.08)),
                       y2=int(HEIGHT * 0.97))
@left_click()
@on_press()
def choose_star_slayer(game: "Game",
                       _scene: "Scene",
                       _btn: "Button",
                       **_kwargs: ButtonKwargs) -> None:
    """
    Chooses the Star Slayer character.
    """

    game.player = StarSlayerCharacter()
    game.start_game()


@charactersmenu.button(message="Bilby Tanka",
                       x1=int((WIDTH / 9) * 2.7 + (WIDTH * 0.08)),
                       y1=int(HEIGHT * 0.87),
                       x2=int((WIDTH / 9) * 4.7 + (WIDTH * 0.08)),
                       y2=int(HEIGHT * 0.97))
@left_click()
@on_press()
def choose_bilby_tanka(game: "Game",
                       _scene: "Scene",
                       _btn: "Button",
                       **_kwargs: ButtonKwargs) -> None:
    """
    Chooses the Bilby Tanka character.
    """

    game.player = BilbyTankaCharacter()
    game.start_game()


@charactersmenu.button(message="Viper Dodger",
                       x1=int((WIDTH / 9) * 5.7 + (WIDTH * 0.08)),
                       y1=int(HEIGHT * 0.87),
                       x2=int((WIDTH / 9) * 8 + (WIDTH * 0.08)),
                       y2=int(HEIGHT * 0.97))
@left_click()
@on_press()
def choose_viper_dodger(game: "Game",
                       _scene: "Scene",
                       _btn: "Button",
                       **_kwargs: ButtonKwargs) -> None:
    """
    Chooses the Viper Dodger character.
    """

    game.player = ViperDodgerCharacter()
    game.start_game()
