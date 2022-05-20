"""
Options Menu Module.
"""

from typing import TYPE_CHECKING

from ....auxiliar import Singleton
from ....checks import left_click, on_press
from ....consts import HEIGHT, WIDTH
from ...hitbox import FloatTuple4
from ...menu import ButtonKwargs, Menu, MenuDict

if TYPE_CHECKING:
    from ....state import Game
    from ....scene import Scene
    from ...button import Button


__all__ = ["OptionsMenu"] # We DON'T want the local variable 'optionsmenu' to be exported


class OptionsMenu(Menu, metaclass=Singleton):
    """
    The Options Menu of the game.
    """

    def __init__(self,
                 area_corners: FloatTuple4=(
                    int(WIDTH / 3.75),
                    int(HEIGHT / 2),
                    int(WIDTH / 1.363636),
                    int(HEIGHT / 1.076923)
                 ),
                 **kwargs: MenuDict) -> None:
        """
        Initializes an instance of 'OptionsMenu'.
        """

        kwargs.update(max_rows=4)
        super().__init__(area_corners, **kwargs)


optionsmenu = OptionsMenu() # instantiated temporarily

@optionsmenu.button(message="Configure Controls")
@left_click()
@on_press()
def configure_controls(game: "Game",
                       _scene: "Scene",
                       _btn: "Button",
                       **_kwargs: ButtonKwargs) -> None:
    """
    Goes to the controls menu.
    """

    game.change_scene("scene-controls")


@optionsmenu.button(message="Edit Color Profiles")
@left_click()
@on_press()
def edit_profiles(game: "Game",
                  _scene: "Scene",
                  _btn: "Button",
                  **_kwargs: ButtonKwargs) -> None:
    """
    Goes to the profiles menu.
    """

    game.change_scene("scene-profiles")
