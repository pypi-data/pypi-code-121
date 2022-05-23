"""
Auxiliar Functions Module. The situations where these might
come in handy are kind of miscellaneous.
"""

from re import match
from typing import TYPE_CHECKING, Optional

from ..consts import GUI_SPACE, HEIGHT, WIDTH
from ..files import StrDict

if TYPE_CHECKING:

    from ..state import Game


#pylint: disable=invalid-name
def is_out_bounds(x1: int, y1: int, x2: int, y2: int) -> bool:
    """
    Checks if something is out of the bounds of the playable screen.

    Return 'True' if so. Else returns 'False'.
    """

    width, height = WIDTH - GUI_SPACE, HEIGHT

    return any((x1 < 0, y1 < 0, x2 > width, y2 > height))


def copy_dict(original: StrDict) -> StrDict:
    """
    Copies, element-by-element, a dictionary into another, so it
    does not work with shallow copies.
    """

    new_dict = {}

    for key, value in original.items():

        new_dict[key] = value

    return new_dict


def get_health_color(game: "Game", health_percentage: float, color_type: int=1) -> str:
    """
    Returns a color depending of the remaining health of the player.
    """

    if 100 <= health_percentage:
        return game.color_profile.get(f"FULL_HEALTH_{color_type}")

    if 75 <= health_percentage < 100:
        return game.color_profile.get(f"STILL_HEALTHY_{color_type}")

    if 50 <= health_percentage < 75:
        return game.color_profile.get(f"OK_MAYBE_IT_STARTS_TO_HURT_{color_type}")

    if 25 <= health_percentage < 50:
        return game.color_profile.get(f"AYO_ITS_ACTUALLY_PAINFUL_{color_type}")

    if 10 <= health_percentage < 25:
        return game.color_profile.get(f"LIKE_IM_GONNA_DIE_AND_STUFF_{color_type}")

    if 5 <= health_percentage < 10:
        return game.color_profile.get(f"NO_SERIOUSLY_IM_GONNA_DIE_{color_type}")

    if 0 < health_percentage < 5:
        return game.color_profile.get(f"HELP_GOD_DAMMIT_{color_type}")

    return ''


def get_color(game: "Game", name: str, health_percentage: Optional[float]=None) -> str:
    """
    Wrapper for searching colors in game profile.
    """

    true_name = '_'.join(name.upper().split())

    if match(r"^HEALTH_COLOR_[1-9]+$", true_name):
        if health_percentage is None:
            health_percentage = game.player.health_percentage()

        return get_health_color(game, health_percentage, int(true_name[-1]))

    if not true_name or true_name == '/':
        return ''

    return game.color_profile.get(true_name)
