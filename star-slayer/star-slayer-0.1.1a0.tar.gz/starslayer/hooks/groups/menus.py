"""
Action group for menus navigation.
"""

from typing import TYPE_CHECKING

from ...checks import is_in_game, scene_has_parent, scene_is_cool
from ..hooks_group import HooksGroup

if TYPE_CHECKING:

    from ...state import Game


class Menus(HooksGroup):
    """
    Menus Group.
    """

    @HooksGroup.action(on_action="UP")
    @is_in_game(False)
    @scene_is_cool()
    def menu_up(self) -> None:
        """
        Navigates UP on menus.
        """

        self.game.current_scene.selected_menu.change_page(False)
        self.game.current_scene.press_cooldown.reset()


    @HooksGroup.action(on_action="DOWN")
    @is_in_game(False)
    @scene_is_cool()
    def menu_down(self) -> None:
        """
        Navigates DOWN on menus.
        """

        self.game.current_scene.selected_menu.change_page(True)
        self.game.current_scene.press_cooldown.reset()


    @HooksGroup.action(on_action="LEFT")
    @is_in_game(False)
    @scene_is_cool()
    def menu_prev(self) -> None:
        """
        Cycles to the previous menu in the scene.
        """

        self.game.current_scene.change_selection(reverse=True)
        self.game.current_scene.press_cooldown.reset()

    @HooksGroup.action(on_action="RIGHT")
    @is_in_game(False)
    @scene_is_cool()
    def menu_next(self) -> None:
        """
        Cycles to the next menu in the scene.
        """

        self.game.current_scene.change_selection(reverse=False)
        self.game.current_scene.press_cooldown.reset()


    @HooksGroup.action(on_action="RETURN")
    @is_in_game(False)
    @scene_has_parent()
    @scene_is_cool()
    def return_to_prev_menu(self) -> None:
        """
        Returns to parent menu.
        """

        self.game.current_scene.press_cooldown.reset() # First we reset the current menu
        self.game.current_scene = self.game.current_scene.parent
        self.game.current_scene.press_cooldown.reset() # Then the parent


def setup_hook(game: "Game") -> None:
    """
    Adds the hook group in this file to the game.
    """

    game.add_group(Menus(game))
