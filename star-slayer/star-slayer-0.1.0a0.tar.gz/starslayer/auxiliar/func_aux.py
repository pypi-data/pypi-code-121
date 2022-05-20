"""
Auxiliar Functions Module. The situations where these might
come in handy are kind of miscellaneous.
"""

from typing import TYPE_CHECKING

from ..files import StrDict

if TYPE_CHECKING:

    from ..state import Game


def copy_dict(original: StrDict) -> StrDict:
    """
    Copies, element-by-element, a dictionary into another, so it
    does not work with shallow copies.
    """

    new_dict = {}

    for key, value in original.items():

        new_dict[key] = value

    return new_dict


def get_color(game: "Game", name: str) -> str:
    """
    Wrapper for searching colors in game profile.
    """

    true_name = '_'.join(name.upper().split())

    if not true_name or true_name == '/':
        return ''

    return game.color_profile.get(true_name)
