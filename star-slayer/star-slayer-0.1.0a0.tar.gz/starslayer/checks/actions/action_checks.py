"""
Action Checks Module. Contains some pre-defined checks as well as the custom decorator.
"""

from typing import TYPE_CHECKING, Callable

from ...hooks import ActionHandler

if TYPE_CHECKING:

    from ...state import Game

ActionCheck = Callable[["Game"], bool]


def check(predicate: ActionHandler) -> ActionHandler:
    """
    Adds a check to an action function.

    The check function needs a 'Game' instance as the
    argument.
    """

    def inner(func: ActionCheck) -> ActionCheck:


        if not hasattr(func, "__checks__"):

            func.__checks__ = []

        func.__checks__.append(predicate)
        return func

    return inner


def is_in_game(inside_game: bool=True) -> ActionHandler:
    """
    Adds a in-game checker.
    """

    def in_a_game(game: "Game") -> bool:
        """
        Checks if the focus is in-game.
        """

        return game.is_in_game if inside_game else not game.is_in_game

    return check(in_a_game)


def can_show_debug() -> ActionHandler:
    """
    Adds a debug checker.
    """

    def show_debug(game: "Game") -> bool:
        """
        Verifies if the cooldown for showing
        debug messages is ready.
        """

        return game.debug_cooldown.is_zero_or_less()

    return check(show_debug)


def can_shoot() -> ActionHandler:
    """
    Adds a shooting checker.
    """

    def can_shoot_bullets(game: "Game") -> bool:
        """
        Verifies if the game shooting cooldown
        is ready.
        """

        return game.shooting_cooldown.is_zero_or_less()

    return check(can_shoot_bullets)


def can_exit() -> ActionHandler:
    """
    Adds a exit checker.
    """

    def can_exit_game(game: "Game") -> bool:
        """
        Verifies if the cooldown for exiting
        the game is ready.
        """

        return game.exiting_cooldown.is_zero_or_less()

    return check(can_exit_game)


def scene_has_parent() -> ActionHandler:
    """
    Adds a scene parent checker.
    """

    def is_there_a_parent(game: "Game") -> bool:
        """
        Verifies if the current menu has a valid parent.
        """

        return bool(game.current_scene.parent)

    return check(is_there_a_parent)


def scene_is_cool() -> ActionHandler:
    """
    Adds a scene cooldown checker.
    """

    def current_scene_cooldown(game: "Game") -> bool:
        """
        Verifies if the current menu pressing cooldown
        timer is zero or less.
        """

        return game.current_scene.press_cooldown.is_zero_or_less()

    return check(current_scene_cooldown)
