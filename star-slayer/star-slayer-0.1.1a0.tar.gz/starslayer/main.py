"""
Main Module. It encases all the other modules to start the game.
"""

from .consts import GAME_VERSION, HEIGHT, GAME_ICON, WIDTH
from .gamelib import (EventType, draw_begin, draw_end, get_events, icon, init,
                      loop, resize, title)
from .graphics import draw_screen, SceneDrawer
from .state import Game


def main() -> int:
    """
    Main function. Initializes the game.
    """

    title(f"Star Slayer v{GAME_VERSION}")
    resize(WIDTH, HEIGHT)
    icon(GAME_ICON)

    game = Game()

    scene_drawer = SceneDrawer(game)

    keys_pressed = game.keys_pressed
    keys_released = game.keys_released

    is_first_lap = True # So that some actions take place in the next iteration of the loop

    cursor_x = None
    cursor_y = None

    while loop(fps=game.time_flow):

        if game.exit:
            break

        draw_begin()
        draw_screen(game, cursor_x, cursor_y, scene_drawer)
        draw_end()

        for event in get_events():

            if not event:
                break

            if event.type == EventType.KeyPress:
                keys_pressed[event.key] = True
                keys_released[event.key] = False

            elif event.type == EventType.KeyRelease:
                keys_pressed[event.key] = False
                keys_released[event.key] = True

            elif event.type in (EventType.ButtonPress, EventType.ButtonRelease):
                game.execute_button(event.x, event.y,
                                    event_type=event.type,
                                    mouse_button=event.mouse_button)

            elif event.type == EventType.Motion:
                cursor_x = event.x
                cursor_y = event.y

        game.process_events()

        if game.is_on_prompt:

            if is_first_lap:
                is_first_lap = False

            else:
                is_first_lap = True
                game.prompt()

        game.advance_game(keys_pressed)

    return 0


if __name__ == "__main__":

    init(main)
