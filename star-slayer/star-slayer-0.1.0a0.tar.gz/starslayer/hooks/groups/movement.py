"""
Action group for player ship movements.
"""

from typing import TYPE_CHECKING

from ...checks import can_shoot, is_in_game
from ..hooks_group import HooksGroup

if TYPE_CHECKING:

    from ...state import Game


class Movements(HooksGroup):
    """
    Movements Group.
    """

    @HooksGroup.action(on_action="UP")
    @is_in_game()
    def navigate_up(self) -> None:
        """
        Moves the player upwards.
        """

        self.game.player.move(0, -self.game.player.speed)


    @HooksGroup.action(on_action="LEFT")
    @is_in_game()
    def navigate_left(self) -> None:
        """
        Moves the player leftwards.
        """

        self.game.player.move(-self.game.player.speed, 0)


    @HooksGroup.action(on_action="RIGHT")
    @is_in_game()
    def navigate_right(self) -> None:
        """
        Moves the player rightwards.
        """

        self.game.player.move(self.game.player.speed, 0)


    @HooksGroup.action(on_action="DOWN")
    @is_in_game()
    def navigate_down(self) -> None:
        """
        Moves the player downwards.
        """

        self.game.player.move(0, self.game.player.speed)


    @HooksGroup.action(on_action="SHOOT")
    @is_in_game()
    @can_shoot()
    def shoot(self) -> None:
        """
        Makes the player shoot.
        """

        self.game.shoot_bullets()
        self.game.shooting_cooldown.reset()


def setup_hook(game: "Game") -> None:
    """
    Adds the hook group in this file to the game.
    """

    game.add_group(Movements(game))
