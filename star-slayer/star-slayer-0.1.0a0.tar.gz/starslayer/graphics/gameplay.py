"""
Gmaeplay Graphics Module.
"""

from typing import TYPE_CHECKING

from ..auxiliar import get_color
from ..consts import DEBUG_LINES, DEBUG_TEXT, HEIGHT, WIDTH
from ..gamelib import draw_line, draw_oval, draw_text

if TYPE_CHECKING:

    from ..state import Game


def draw_bullets(game: "Game") -> None:
    """
    Draws every single bullet currently on screen.
    """

    bullets = game.bullets

    for bullet in bullets:

        draw_oval(bullet.x1,
                  bullet.y1,
                  bullet.x2,
                  bullet.y2,
                  outline=get_color(game, "GUI_OUTLINE_1"),
                  fill=get_color(game, "TEXT_COLOR_1"))


def draw_debug_lines(game: "Game") -> None:
    """
    Marks the limit of hitboxes and additional debug info through lines.
    """

    player = game.player
    cx, cy = player.center # pylint: disable=invalid-name
    aux = (WIDTH // 150)

    # Upper Lines
    draw_line(cx,
              0,
              cx,
              player.y1,
              fill=get_color(game, "DEBUG_LINES_1"))
    draw_line(cx - aux,
              player.y1,
              cx + aux,
              player.y1,
              fill=get_color(game, "DEBUG_LINES_1"))

    # Bottom Lines
    draw_line(cx,
              player.y2,
              cx,
              HEIGHT,
              fill=get_color(game, "DEBUG_LINES_1"))
    draw_line(cx - aux,
              player.y2,
              cx + aux,
              player.y2,
              fill=get_color(game, "DEBUG_LINES_1"))

    # Left Lines
    draw_line(0,
              cy,
              player.x1,
              cy,
              fill=get_color(game, "DEBUG_LINES_1"))
    draw_line(player.x1,
              cy - aux,
              player.x1,
              cy + aux,
              fill=get_color(game, "DEBUG_LINES_1"))

    # Right Lines
    draw_line(player.x2,
              cy, WIDTH,
              cy,
              fill=get_color(game, "DEBUG_LINES_1"))
    draw_line(player.x2,
              cy - aux,
              player.x2,
              cy + aux,
              fill=get_color(game, "DEBUG_LINES_1"))


    # Upper-Left Corner
    draw_line(player.x1,
              player.y1,
              player.x1 + (aux * 2),
              player.y1,
              fill=get_color(game, "DEBUG_LINES_1"))
    draw_line(player.x1,
              player.y1,
              player.x1,
              player.y1 + (aux * 2),
              fill=get_color(game, "DEBUG_LINES_1"))

    # Upper-Right Corner
    draw_line(player.x2,
              player.y1,
              player.x2 - (aux * 2),
              player.y1,
              fill=get_color(game, "DEBUG_LINES_1"))
    draw_line(player.x2,
              player.y1,
              player.x2,
              player.y1 + (aux * 2),
              fill=get_color(game, "DEBUG_LINES_1"))

    # Bottom-Left Corner
    draw_line(player.x1,
              player.y2,
              player.x1 + (aux * 2),
              player.y2,
              fill=get_color(game, "DEBUG_LINES_1"))
    draw_line(player.x1,
              player.y2,
              player.x1,
              player.y2 - (aux * 2),
              fill=get_color(game, "DEBUG_LINES_1"))

    # Bottom-Right Corner
    draw_line(player.x2,
              player.y2,
              player.x2 - (aux * 2),
              player.y2,
              fill=get_color(game, "DEBUG_LINES_1"))
    draw_line(player.x2,
              player.y2,
              player.x2,
              player.y2 - (aux * 2),
              fill=get_color(game, "DEBUG_LINES_1"))


def draw_debug_info(game: "Game") -> None:
    """
    Draws debug information about the current game.
    """

    player = game.player
    debug_cons = (HEIGHT // 70)

    settings = {"player_x1": f"{player.x1:.2f}",
               "player_y1": f"{player.y1:.2f}",
               "player_x2": f"{player.x2:.2f}",
               "player_y2": f"{player.y2:.2f}",

               "hitbox_center": player.center,
               "shooting_cooldown": ("Ready!" if game.shooting_cooldown.is_zero_or_less()
                                     else game.shooting_cooldown.current_time),
               "inv_cooldown": ("Ready!" if game.invulnerability.is_zero_or_less()
                                else game.invulnerability.current_time),

               "level_time": f"{game.level_time.current_time:.2f}",
               "power_level": game.power_level.name,

               "health": game.player.hp,
               "hardness": game.player.hardness,
               "speed": game.player.speed,

               "enemies": len(game.enemies),
               "bullets": len(game.bullets)}

    debug_text = DEBUG_TEXT.format(**settings)

    draw_text(debug_text,
              debug_cons,
              debug_cons,
              size=debug_cons,
              fill=get_color(game, "TEXT_COLOR_1"),
              anchor="nw")

    if not DEBUG_LINES:
        return

    draw_debug_lines(game)

    aux = (WIDTH // 30)

    for bullet in game.bullets:

        x, y = bullet.center # pylint: disable=invalid-name
        draw_line(x, y - aux,
                  x, y + aux,
                  fill=get_color(game, "DEBUG_LINES_2"))
        draw_line(x - aux, y,
                  x + aux, y,
                  fill=get_color(game, "DEBUG_LINES_2"))

    for enem in game.enemies:

        aux2 = int(aux * 1.67)

        x, y = enem.center # pylint: disable=invalid-name
        draw_line(x, y - aux2, x,
                  y + aux2,
                  fill=get_color(game, "DEBUG_LINES_2"))
        draw_line(x - aux2,
                  y, x + aux2,
                  y, fill=get_color(game, "DEBUG_LINES_2"))
