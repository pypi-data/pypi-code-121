"""
Buttons Checks Module. Contains some pre-defined checks as well as the custom decorator.
"""

from typing import TYPE_CHECKING, Callable, Tuple

from ...gamelib import EventType

if TYPE_CHECKING:

    from ...state.game_state import Game
    from ...utils import Button, ButtonHandler, ButtonKwargs

ButtonCheck = Callable[["Game", "Button", "ButtonKwargs"], bool]


def check(predicate: ButtonCheck) -> "ButtonHandler":
    """
    Adds a check to an action function.

    The check function needs a 'Game' instance as its
    first argument, and the button itself as the second.
    Also, it must accept 'kwargs' keyword arguments.
    """

    def inner(func: "ButtonHandler") -> "ButtonHandler":

        if not hasattr(func, "__btn_checks__"):

            func.__btn_checks__ = []

        func.__btn_checks__.append(predicate)
        return func

    return inner


def is_on_prompt(it_is: bool=True) -> "ButtonHandler":
    """
    Adds a prompt checker.
    """

    def game_is_on_prompt(game: "Game", _btn: "Button", **_kwargs: "ButtonKwargs") -> bool:
        """
        Checks if the game is currently prompting the user.
        """

        return game.is_on_prompt if it_is else not game.is_on_prompt

    return check(game_is_on_prompt)


def on_press() -> "ButtonHandler":
    """
    Adds a press checker.
    """

    def is_pressing(_game: "Game", _btn: "Button", **kwargs: "ButtonKwargs") -> bool:
        """
        Checks if the button is being pressed.
        """

        return kwargs.get("event_type") == EventType.ButtonPress

    return check(is_pressing)


def on_release() -> "ButtonHandler":
    """
    Adds a release checker.
    """

    def is_releasing(_game: "Game", _btn: "Button", **kwargs: "ButtonKwargs") -> bool:
        """
        Checks if the button is being released.
        """

        return kwargs.get("event_type") == EventType.ButtonRelease

    return check(is_releasing)


def clicks(*types: Tuple[int, ...]) -> "ButtonHandler":
    """
    Adds a clicks checker. With this you can check
    multiple click types.

    1 for left click.
    2 for middle click.
    3 for right click.
    """

    def is_certain_click(_game: "Game", _btn: "Button", **kwargs: "ButtonKwargs") -> bool:
        """
        Checks if the event mouse button is one of the click types
        """

        click = kwargs.get("mouse_button")
        return click in types

    return check(is_certain_click)


def left_click(it_is: bool=True) -> "ButtonHandler":
    """
    Adds a left click checker.
    """

    def is_left_click(_game: "Game", _btn: "Button", **kwargs: "ButtonKwargs") -> bool:
        """
        Checks if the mouse left click was pressed or released.
        """

        click = kwargs.get("mouse_button")
        click_check = click == 1

        return click_check if it_is else not click_check

    return check(is_left_click)


def right_click(it_is: bool=True) -> "ButtonHandler":
    """
    Adds a right click checker.
    """

    def is_right_click(_game: "Game", _btn: "Button", **kwargs: "ButtonKwargs") -> bool:
        """
        Checks if the mouse right click was pressed or released.
        """

        click = kwargs.get("mouse_button")
        click_check = click == 3

        return click_check if it_is else not click_check

    return check(is_right_click)


def middle_click(it_is: bool=True) -> "ButtonHandler":
    """
    Adds a middle click checker.
    """

    def is_middle_click(_game: "Game", _btn: "Button", **kwargs: "ButtonKwargs") -> bool:
        """
        Checks if the mouse middle click was pressed or released.
        """

        click = kwargs.get("mouse_button")
        click_check = click == 2

        return click_check if it_is else not click_check

    return check(is_middle_click)
