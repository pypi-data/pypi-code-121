"""
GUI Module.
"""

from typing import TYPE_CHECKING

from ..auxiliar import get_color
from ..consts import GUI_SPACE, HEIGHT, WIDTH
from ..gamelib import draw_line, draw_rectangle, draw_text

if TYPE_CHECKING:

    from ..state import Game
    from ..utils import Menu
    from ..utils import Button


def draw_gui(game: "Game") -> None:
    """
    Draws the User Interface.
    """

    aux_cons = (HEIGHT // 70)

    draw_rectangle(WIDTH - GUI_SPACE,
                   0,
                   WIDTH,
                   HEIGHT,
                   outline=get_color(game, "GUI_OUTLINE_1"),
                   fill=get_color(game, "GUI_COLOR_1"))

    # Power Level
    draw_text("Power Level:",
              WIDTH - GUI_SPACE + aux_cons,
              HEIGHT * 0.73,
              size=(WIDTH // 50),
              fill=get_color(game, "TEXT_COLOR_1"),
              anchor='w')
    draw_text(f"{game.power_level.name}",
              WIDTH - aux_cons,
              HEIGHT * 0.73,
              size=(WIDTH // 50),
              fill=get_color(game, "TEXT_COLOR_1"),
              anchor='e')

    draw_line(WIDTH - GUI_SPACE + aux_cons,
              HEIGHT * 0.765,
              WIDTH - aux_cons,
              HEIGHT * 0.765,
              width=(aux_cons // 2),
              fill=get_color(game, "GUI_COLOR_2"))

    # Hardness
    draw_text("Current Hardness:",
              WIDTH - GUI_SPACE + aux_cons,
              HEIGHT * 0.8,
              size=(WIDTH // 62),
              fill=get_color(game, "TEXT_COLOR_1"),
              anchor='w')
    draw_text(f"{game.player.hardness}",
              WIDTH - aux_cons,
              HEIGHT * 0.8,
              size=(WIDTH // 62),
              fill=get_color(game, "TEXT_COLOR_1"),
              anchor='e')

    # Speed
    draw_text("Current Speed:",
              WIDTH - GUI_SPACE + aux_cons,
              HEIGHT * 0.85,
              size=(WIDTH // 62),
              fill=get_color(game, "TEXT_COLOR_1"),
              anchor='w')
    draw_text(f"{game.player.speed}",
              WIDTH - aux_cons,
              HEIGHT * 0.85,
              size=(WIDTH // 62),
              fill=get_color(game, "TEXT_COLOR_1"),
              anchor='e')

    # Health
    draw_text("Remaining health:",
              WIDTH - GUI_SPACE + aux_cons,
              HEIGHT * 0.9,
              size=(WIDTH // 62),
              fill=get_color(game, "TEXT_COLOR_1"),
              anchor='w')
    draw_text(f"{game.player.hp}  /  {game.player.max_hp}",
              WIDTH - aux_cons,
              HEIGHT * 0.9,
              size=(WIDTH // 62),
              fill=get_color(game, "TEXT_COLOR_1"),
              anchor='e')

    # Health Bar
    draw_rectangle(WIDTH - GUI_SPACE + aux_cons,
                  HEIGHT * 0.93, WIDTH - aux_cons,
                  HEIGHT - aux_cons,
                  width=(aux_cons // 2),
                  outline=get_color(game, "GUI_OUTLINE_2"),
                  fill=get_color(game, "GUI_OUTLINE_1"))

    if not game.player.has_no_health():

        hp_percentage = (game.player.hp / game.player.max_hp) * 100

        bar_start = WIDTH - GUI_SPACE + (2 * aux_cons)
        bar_end = WIDTH - (2 * aux_cons)

        augment = ((bar_end - bar_start) / 100) * hp_percentage

        draw_rectangle(bar_start,
                       HEIGHT * 0.945,
                       bar_start + augment,
                       HEIGHT - (2 * aux_cons),
                       outline=get_color(game, "GUI_OUTLINE_1"),
                       fill=get_color(game, "GUI_COLOR_3"))


def draw_button_hitbox(game: "Game", menu: "Menu", btn: "Button") -> None:
    """
    Draws a single button square.
    """

    x1, y1, x2, y2 = btn.all_coords # pylint: disable=invalid-name
    fill_color = (get_color(game, "BUTTON_COLOR_1")
                  if menu is game.current_scene.selected_menu
                  else get_color(game, "BUTTON_COLOR_3"))

    draw_rectangle(x1, y1, x2, y2,
                   width=((y2 - y1) // 25),
                   outline=get_color(game, "TEXT_COLOR_1"),
                   fill=fill_color,
                   activefill=get_color(game, "BUTTON_COLOR_2"))


def draw_exiting_bar(game: "Game") -> None:
    """
    Draws a mini-bar that shows how much time is left until it exits the game.
    """
    aux_cons = (HEIGHT // 60)
    initial = game.exiting_cooldown.initial_time
    current = game.exiting_cooldown.current_time

    draw_rectangle(aux_cons,
                   aux_cons,
                   (10 * aux_cons),
                   (3 * aux_cons),
                   width=(aux_cons // 3),
                   outline=get_color(game, "TEXT_COLOR_1"),
                   fill=get_color(game, "GUI_OUTLINE_1"))

    percentage = 100 - ((current / initial) * 100)
    bar_start = (1.5 * aux_cons)
    bar_end = (9.5 * aux_cons)
    augment = ((bar_end - bar_start) / 100) * percentage

    draw_rectangle(bar_start,
                   (1.5 * aux_cons),
                   bar_start + augment,
                   (2.5 * aux_cons),
                   outline=get_color(game, "GUI_OUTLINE_1"),
                   fill=get_color(game, "TEXT_COLOR_1"))

    draw_text("Exiting Game...",
              (5.5 * aux_cons),
              (4.5 * aux_cons), size=aux_cons, anchor='c')
