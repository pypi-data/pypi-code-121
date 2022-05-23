"""
Color selector Graphics Module.
"""

from typing import TYPE_CHECKING

from ..auxiliar import get_color
from ..consts import HEIGHT, SPECIAL_CHARS, WIDTH
from ..gamelib import draw_line, draw_oval, draw_rectangle, draw_text
from .gui import draw_button_hitbox

if TYPE_CHECKING:

    from ..state import Game


def draw_color_table(game: "Game") -> None:
    """
    Draws the color table of the selector prompt.
    """

    selector = game.color_selector
    p_x1, p_y1, _, _ = selector.palette_area
    selection_width = (WIDTH // 160)

    for row in range(selector.rows):

        for col in range(selector.cols):

            draw_rectangle(p_x1 + (col * selector.augment_x),
                           p_y1 + (row * selector.augment_y),
                           p_x1 + ((col + 1) * selector.augment_x),
                           p_y1 + ((row + 1) * selector.augment_y),
                           outline='',
                           fill=selector.color_palette[(col, row)].hex)

    extra_x = (WIDTH // 200)
    extra_y = (HEIGHT // 180)

    if selector.selection and not selector.is_transparent:

        i, j = selector.selection

        draw_rectangle(p_x1 + i * (selector.augment_x) - extra_x,
                       p_y1 + j * (selector.augment_y) - extra_y,
                       p_x1 + (i + 1) * (selector.augment_x) + extra_x,
                       p_y1 + (j + 1) * (selector.augment_y) + extra_y,
                       width=selection_width,
                       outline=get_color(game, "TEXT_COLOR_1"),
                       fill=selector.get_selected_color_hex())


def draw_hue_bar(game: "Game") -> None:
    """
    Draws he hue bar of the selector prompt.
    """

    selector = game.color_selector
    hue_x1, hue_y1, _, hue_y2 = selector.hue_bar_area
    hue_augment = selector.hue_augment

    for i, (_, hue_col) in enumerate(selector.hue_bar):

        draw_rectangle(hue_x1 + (i * hue_augment),
                       hue_y1,
                       hue_x1 + ((i + 1) * hue_augment),
                       hue_y2,
                       outline='',
                       fill=hue_col.hex)

    hue_i = selector.hue_index
    _, hue_color = selector.hue_bar[hue_i]
    extra_x = (WIDTH // 150)
    extra_y = (HEIGHT // 140)

    if not selector.is_transparent:

        draw_rectangle(hue_x1 + (hue_i * hue_augment) - extra_x,
                       hue_y1 - extra_y,
                       hue_x1 + ((hue_i + 1) * hue_augment) + extra_x,
                       hue_y2 + extra_y,
                       width=int(extra_x * 0.6),
                       outline=get_color(game, "TEXT_COLOR_1"),
                       fill=hue_color.hex)


def draw_selector_buttons(game: "Game") -> None:
    """
    Draws on the screen the buttons that the color selector has.
    """

    selector = game.color_selector

    for button in selector.buttons:

        draw_button_hitbox(game, game.current_scene.selected_menu, button)

        cx, cy = button.center # pylint: disable=invalid-name
        draw_text(' '.join(button.msg.split('_')),
                  cx, cy,
                  size=int((button.y2 - button.y1) // (2 if button.msg in SPECIAL_CHARS else 4)),
                  fill=get_color(game, "TEXT_COLOR_1"),
                  justify='c')


def draw_selector_details(game: "Game") -> None:
    """
    Draws details of the selector like the color selected,
    or the RGB indicator.
    """

    selector = game.color_selector

    aux_x = (WIDTH // 75)
    aux_y = (HEIGHT // 70)
    aux_font = (WIDTH // 150)

    s_x1 = selector.x2 - (WIDTH * 0.293333)
    s_y1 = selector.hue_bar_area[3] + (HEIGHT * 0.021428)
    s_x2 = selector.p_x2
    s_y2 = selector.y2 - (HEIGHT * 0.094285)

    draw_rectangle(selector.x1 + (aux_x * 0.5),
                   s_y1 - (aux_y * 0.5),
                   selector.x2 - (aux_x * 0.5),
                   selector.x2 - (aux_y * 0.5),
                   width=(aux_x // 10),
                   outline=get_color(game, "MENU_OUTLINE_1"),
                   fill=get_color(game, "MENU_COLOR_2"))

    # Invisible Color
    inv_x1, inv_y1, inv_x2, inv_y2 = selector.inv_color_area
    oval_x = ((inv_x2 - inv_x1) // 7)
    oval_y = ((inv_y2 - inv_y1) // 7)

    draw_oval(inv_x1, inv_y1, inv_x2, inv_y2,
              width=((aux_x // 2) if selector.is_transparent else (aux_x // 5)),
              outline=get_color(game, "TEXT_COLOR_1"),
              fill='')

    draw_line(inv_x2 - oval_x,
              inv_y1 + oval_y,
              inv_x1 + oval_x,
              inv_y2 - oval_x,
              width=(aux_x // 5),
              fill=get_color(game, "TEXT_COLOR_1"))

    # Color Preview
    draw_rectangle(s_x1, s_y1, s_x2, s_y2,
                  outline='',
                  fill=selector.get_selected_color_hex())

    # --- HEX --- #

    middle_hex = (s_y1 + (s_y2 - s_y1) * 0.19)

    draw_rectangle(selector.x1 + (aux_x * 0.7),
                  middle_hex - (2 * aux_y),
                  selector.x1 + (27.3 * aux_x),
                  middle_hex + (2 * aux_y),
                  width=(aux_x // 5),
                  outline=get_color(game, "MENU_OUTLINE_1"),
                  fill='')

    draw_line(selector.x1 + (9 * aux_x),
              middle_hex - (2 * aux_y),
              selector.x1 + (9 * aux_x),
              middle_hex + (2 * aux_y),
              width=(aux_x // 3),
              fill=get_color(game, "MENU_OUTLINE_1"))

    draw_text("HEX",
              selector.x1 + aux_x, middle_hex,
              size=(5 * aux_font),
              anchor='w',
              fill=get_color(game, "TEXT_COLOR_1"),
              justify='c')

    hex_color = selector.get_selected_color_hex()

    draw_text(("N/A" if not hex_color else hex_color.upper()),
              selector.x1 + (18.15 * aux_x), middle_hex,
              size=(4 * aux_font),
              anchor='c',
              fill=get_color(game, "TEXT_COLOR_1"),
              justify='c')

    # --- RGB --- #

    red, green, blue = (("N/A", "N/A", "N/A")
                        if selector.is_transparent
                        else selector.get_selected_color().rgb)

    upper_rgb = s_y1 + (s_y2 - s_y1) * 0.43
    bottom_rgb = upper_rgb + (3 * aux_y)
    middle_rgb = (upper_rgb + bottom_rgb) / 2

    draw_rectangle(selector.x1 + (aux_x * 0.7),
                   upper_rgb - (aux_y * 0.5),
                   selector.x1 + (36.5 * aux_x),
                   bottom_rgb + (aux_y * 0.5),
                   width=(aux_x // 5),
                   outline=get_color(game, "MENU_OUTLINE_1"),
                   fill='')

    draw_line(selector.x1 + (9 * aux_x),
              upper_rgb - (aux_y * 0.5),
              selector.x1 + (9 * aux_x),
              bottom_rgb + (aux_y * 0.5),
              width=(aux_x // 3),
              fill=get_color(game, "MENU_OUTLINE_1"))

    draw_line(selector.x1 + (18.3 * aux_x),
              upper_rgb - (aux_y * 0.5),
              selector.x1 + (18.3 * aux_x),
              bottom_rgb + (aux_y * 0.5),
              width=(aux_x // 5),
              fill=get_color(game, "MENU_OUTLINE_1"))

    draw_line(selector.x1 + (27.3 * aux_x),
              upper_rgb - (aux_y * 0.5),
              selector.x1 + (27.3 * aux_x),
              bottom_rgb + (aux_y * 0.5),
              width=(aux_x // 5),
              fill=get_color(game, "MENU_OUTLINE_1"))

    draw_text("RGB",
              selector.x1 + aux_x, middle_rgb,
              size=(5 * aux_font),
              anchor='w',
              fill=get_color(game, "TEXT_COLOR_1"),
              justify='c')

    # Red
    draw_oval(selector.x1 + (10 * aux_x),
              upper_rgb,
              selector.x1 + (13 * aux_x),
              bottom_rgb,
              width=(aux_x // 5),
              outline=get_color(game, "TEXT_COLOR_1"),
              fill="#ff0000")

    draw_text(red,
              selector.x1 + (16 * aux_x), middle_rgb,
              size=(3 * aux_font),
              fill=get_color(game, "TEXT_COLOR_1"),
              justify='c')

    # Green
    draw_oval(selector.x1 + (19 * aux_x),
              upper_rgb,
              selector.x1 + (22 * aux_x),
              bottom_rgb,
              width=(aux_x // 5),
              outline=get_color(game, "TEXT_COLOR_1"),
              fill="#00ff00")

    draw_text(green,
              selector.x1 + (25 * aux_x), middle_rgb,
              size=(3 * aux_font),
              fill=get_color(game, "TEXT_COLOR_1"),
              justify='c')

    # Blue
    draw_oval(selector.x1 + (28 * aux_x),
              upper_rgb,
              selector.x1 + (31 * aux_x),
              bottom_rgb,
              width=(aux_x // 5),
              outline=get_color(game, "TEXT_COLOR_1"),
              fill="#0000ff")

    draw_text(blue,
              selector.x1 + (34 * aux_x), middle_rgb,
              size=(3 * aux_font),
              fill=get_color(game, "TEXT_COLOR_1"),
              justify='c')

    # --- HSV --- #

    middle_hsv = (s_y1 + (s_y2 - s_y1) * 0.837373)

    draw_rectangle(selector.x1 + (aux_x * 0.7),
                   middle_hsv - (2 * aux_y),
                   selector.x1 + (36.5 * aux_x),
                   middle_hsv + (2 * aux_y),
                   width=(aux_x // 5),
                   outline=get_color(game, "MENU_OUTLINE_1"),
                   fill='')

    draw_line(selector.x1 + (9 * aux_x),
              middle_hsv - (2 * aux_y),
              selector.x1 + (9 * aux_x),
              middle_hsv + (2 * aux_y),
              width=(aux_x // 3),
              fill=get_color(game, "MENU_OUTLINE_1"))

    draw_text("HSV",
              selector.x1 + aux_x, middle_hsv,
              size=(5 * aux_font),
              anchor='w',
              fill=get_color(game, "TEXT_COLOR_1"),
              justify='c')

    i, j = selector.selection
    cols, rows = selector.cols, selector.rows

    hue = int(selector.hue_bar[selector.hue_index][0] * 360)
    saturation = int(i * (1.0 / cols) * 100)
    value = 100 - int(j * (1.0 / rows) * 100)

    draw_text(("N/A   -   N/A   -   N/A"
               if selector.is_transparent
               else f"{hue:03d}°  -  {saturation}%  -  {value}%"),
              selector.x1 + (10 * aux_x), middle_hsv,
              size=(4 * aux_font),
              anchor='w',
              fill=get_color(game, "TEXT_COLOR_1"),
              justify='c')
