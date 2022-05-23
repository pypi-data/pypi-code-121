"""
Action group for player ship movements.
"""

from typing import TYPE_CHECKING

from ...checks import can_shoot, has_shield, is_in_game
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
        self.game.player.shooting_cooldown.reset()


    @HooksGroup.action(on_action="ROTATE_ANTICLOCK")
    @is_in_game()
    @has_shield()
    def rotate_shield_anticlock(self) -> None:
        """
        Rotates the player shield anti-clockwise.
        """

        self.game.player.shield.rotate(-0.06)


    @HooksGroup.action(on_action="ROTATE_CLOCK")
    @is_in_game()
    @has_shield()
    def rotate_shield_clock(self) -> None:
        """
        Rotates the player shield clockwise.
        """

        self.game.player.shield.rotate(0.06)


def setup_hook(game: "Game") -> None:
    """
    Adds the hook group in this file to the game.
    """

    game.add_group(Movements(game))
