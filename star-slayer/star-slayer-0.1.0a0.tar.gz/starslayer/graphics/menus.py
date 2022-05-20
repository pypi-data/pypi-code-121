"""
Menus Graphics Module.
"""

from typing import TYPE_CHECKING

from ..auxiliar import get_color
from ..consts import PROFILES_CHANGER, PROFILES_DELETER, SPECIAL_CHARS
from ..gamelib import draw_text
from .gui import draw_button_hitbox

if TYPE_CHECKING:

    from ..state import Game
    from ..utils import Menu


def draw_menu_buttons(game: "Game", menu: "Menu") -> None:
    """
    Draws all the buttons of a given menu.
    """

    if menu.hidden:
        return

    for button in menu.buttons_on_screen:

        draw_button_hitbox(game, menu, button)

        if not button.msg:
            continue

        x_coord, y_coord = button.center
        btn_anchor = menu.button_anchor

        if button.msg in SPECIAL_CHARS or button.msg in [PROFILES_CHANGER, PROFILES_DELETER]:

            btn_anchor = 'c'

        else:

            if menu.button_anchor == 'c':

                x_coord += menu.offset_x
                y_coord += menu.offset_y

            else:

                width_extra = (button.width // 50)
                height_extra = (button.height // 50)

                if 'n' in menu.button_anchor:

                    y_coord = button.y1 + height_extra

                elif 's' in menu.button_anchor:

                    y_coord = button.y2 - height_extra

                if 'w' in menu.button_anchor:

                    x_coord = button.x1 + width_extra

                elif 'e' in menu.button_anchor:

                    x_coord = button.x2 - width_extra

        draw_text(' '.join(button.msg.split('_')),
                  x_coord, y_coord,
                  size=int((button.y2 - button.y1) // (2 if button.msg in SPECIAL_CHARS else 4)),
                  fill=get_color(game, "TEXT_COLOR_1"),
                  anchor=btn_anchor,
                  justify='c')
