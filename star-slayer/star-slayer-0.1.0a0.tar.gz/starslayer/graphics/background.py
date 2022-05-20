"""
Background Graphics Module.
"""

from sys import version_info
from typing import TYPE_CHECKING

from ..auxiliar import get_color
from ..consts import HEIGHT, WIDTH
from ..gamelib import draw_rectangle, draw_text

if TYPE_CHECKING:

    from ..state import Game


def draw_background(game: "Game") -> None:
    """
    Draws the background of the game (duh).
    """

    draw_rectangle(0, 0, WIDTH, HEIGHT, fill=get_color(game, "BG_COLOR"))


def draw_default_background() -> None:
    """
    In case of some error, shows a message indicading so.
    """

    version = '.'.join(str(num) for num in tuple(version_info)[:3])

    # Colors are independent on color profile
    draw_rectangle(0, 0, WIDTH * 1.1, HEIGHT * 1.1, outline='', fill="#aaaaaa")
    draw_text(f"[ERROR] Python version {version} is not valid.\n" +
               "Please use 3.10.0 or higher instead.",
              WIDTH / 2,
              HEIGHT / 2,
              size=(WIDTH // 40),
              anchor='c')
