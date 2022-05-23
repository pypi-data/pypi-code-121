"""
Sprites Graphics Module.
"""

from typing import TYPE_CHECKING, Optional

from ..gamelib import draw_arc, draw_rectangle

if TYPE_CHECKING:

    from ..sprites import Sprite
    from ..state import Game


# pylint: disable=invalid-name
def draw_sprite_pixels(sprite: "Sprite",
                       x1: float,
                       y1: float,
                       x2: float,
                       y2: float,
                       *,
                       to_next: bool=True,
                       circular: bool=True) -> None:
    """
    Draws a definite sprite on the screen.
    """

    width = sprite.width
    height = sprite.height
    x_increment = (x2 - x1) / width
    y_increment = (y2 - y1) / height
    cur_frame = sprite.current_frame

    for i in range(width):
        for j in range(height):

            frame_color = cur_frame[(i, j)]
            if not frame_color:
                continue

            draw_rectangle(x1 + (i * x_increment),
                           y1 + (j * y_increment),
                           x1 + ((i + 1) * x_increment),
                           y1 + ((j + 1) * y_increment),
                           outline='',
                           fill=frame_color.hex)

    if to_next:
        sprite.next_frame(circular)
        return

    sprite.previous_frame(circular)


# pylint: disable=invalid-name
def draw_sprite(sprite: Optional["Sprite"],
                x1: float,
                y1: float,
                x2: float,
                y2: float,
                *,
                to_next: bool=True,
                circular: bool=True,
                sprite_type: str="BOX") -> None:
    """
    Draws a sprite in the given coordinates.
    """

    if not sprite:

        middle_x = (x2 - x1) / 2
        middle_y = (y2 - y1) / 2
        sprite_type = sprite_type.upper()

        if sprite_type == "BOX":
            draw_rectangle(x1,
                           y1,
                           x1 + middle_x,
                           y1 + middle_y,
                           outline='',
                           fill="#ff00ff")
            draw_rectangle(x1 + middle_x,
                           y1,
                           x2,
                           y1 + middle_y,
                           outline='',
                           fill="#000000")
            draw_rectangle(x1,
                           y1 + middle_y,
                           x1 + middle_x,
                           y2, outline='',
                           fill="#000000")
            draw_rectangle(x1 + middle_x,
                           y1 + middle_y,
                           x2,
                           y2,
                           outline='',
                           fill="#ff00ff")


        elif sprite_type == "CIRCLE":
            draw_arc(x1,
                     y1,
                     x2,
                     y2,
                     outline='',
                     fill="#ff00ff",
                     start=90.0,
                     extent=90.0)
            draw_arc(x1,
                     y1,
                     x2,
                     y2,
                     outline='',
                     fill="#000000",
                     start=0.0,
                     extent=90.0)
            draw_arc(x1,
                     y1,
                     x2,
                     y2,
                     outline='',
                     fill="#000000",
                     start=180.0,
                     extent=90.0)
            draw_arc(x1,
                     y1,
                     x2,
                     y2,
                     outline='',
                     fill="#ff00ff",
                     start=270.0,
                     extent=90.0)
        return

    draw_sprite_pixels(sprite, x1, y1, x2, y2,
                       to_next=to_next,
                       circular=circular)
