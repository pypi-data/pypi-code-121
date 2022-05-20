"""
Scene Graphics Module.
"""

from typing import TYPE_CHECKING

from ..auxiliar import get_color
from ..consts import HEIGHT, KEYS_PATH, WIDTH
from ..files import list_repeated_keys, load_json
from ..gamelib import draw_line, draw_oval, draw_rectangle, draw_text
from .menus import draw_menu_buttons
from .prompt import draw_attribute_prompt, draw_key_changing_prompt
from .sprites import draw_sprite

if TYPE_CHECKING:

    from ..state import Game
    from ..scene import AnimationsList


class SceneDrawer:
    """
    Class for drawing extra things on the scene.
    """

    def __init__(self, game: "Game") -> None:
        """
        Initializes an instance of type 'SceneDrawer'.
        """

        self.game: "Game" = game


    def draw_scene(self) -> None:
        """
        Draws in the screen the current scene.
        """

        self.draw_scene_rear_animations()
        self.draw_scene_buttons()
        self.draw_scene_labels()
        self.draw_scene_sprites()
        self.draw_scene_front_animations()

        draw_handler = getattr(SceneDrawer,
                               f"draw_{self.game.current_scene.id.replace('-', '_')}",
                               None)

        if draw_handler:
            draw_handler(self)


    def draw_scene_animations(self, anim_list: "AnimationsList") -> None:
        """
        Draws animations in the screen, without caring if
        they are rear or front.
        """

        for anim in anim_list:

            if "fill" not in anim.properties:
                fill_name = anim.properties.pop("fill_name", "MENU COLOR 1")
                anim.properties.update(fill=get_color(self.game, fill_name))

            if "outline" not in anim.properties:
                outline_name = anim.properties.pop("outline_name", "BG COLOR")
                anim.properties.update(outline=get_color(self.game, outline_name))

            anim.animate()
            anim.post_hook()


    def draw_scene_rear_animations(self) -> None:
        """
        Draws in the screen the current scene rear animations.
        """

        self.draw_scene_animations(self.game.current_scene.rear_animations)


    def draw_scene_front_animations(self) -> None:
        """
        Draws in the screen the current scene front animations.
        """

        self.draw_scene_animations(self.game.current_scene.front_animations)


    def draw_scene_buttons(self) -> None:
        """
        Draws in the screen the current scene buttons.
        """

        scene = self.game.current_scene
        for menu in scene.menus:
            draw_menu_buttons(self.game, menu)


    def draw_scene_labels(self) -> None:
        """
        Draws in the screen the current scene labels.
        """

        scene = self.game.current_scene
        for label in scene.labels:

            if not "fill" in label.properties:
                color_name = label.properties.pop("color_name", "TEXT_COLOR_1")
                label.properties.update(fill=get_color(self.game, color_name))

            draw_text(label.text, label.x, label.y, **label.properties)


    def draw_scene_sprites(self) -> None:
        """
        Draws in the screen the current scene sprites.
        """

        scene = self.game.current_scene
        for sprite_properties in scene.sprites:
            sprite = sprite_properties.get("sprite")
            draw_sprite(sprite,
                        sprite_properties.get("x1"),
                        sprite_properties.get("y1"),
                        sprite_properties.get("x2"),
                        sprite_properties.get("y2"))

            sprite.next_frame()


    def draw_scene_controls(self) -> None:
        """
        Draws the information of the action and its assigned keys.
        If possible, it also allows it to edit said information.
        """

        aux_cons = (HEIGHT // 70)

        draw_rectangle((WIDTH // 4) + aux_cons,
                    aux_cons,
                    WIDTH - aux_cons,
                    HEIGHT - aux_cons,
                    width=(HEIGHT // 87),
                    outline=get_color(self.game, "MENU_OUTLINE_1"),
                    fill=get_color(self.game, "MENU_COLOR_1"))
        draw_text(' '.join(self.game.action_to_show.split('_')),
                int(WIDTH * (5 / 8)),
                (HEIGHT // 8),
                fill=get_color(self.game, "TEXT_COLOR_1"),
                size=(WIDTH // 10),
                justify='c')

        keys_assigned = list_repeated_keys(self.game.action_to_show, load_json(KEYS_PATH))

        if '' in keys_assigned:

            keys_assigned.remove('')

        if not keys_assigned:

            draw_text("Action is currently not binded to any key",
                    (WIDTH * (5 / 8)),
                    (HEIGHT / 3.5),
                    fill=get_color(self.game, "TEXT_COLOR_1"),
                    size=(WIDTH // 34),
                    justify='c')

        else:

            draw_text(" - ".join(keys_assigned),
                    int(WIDTH * (5 / 8)),
                    int(HEIGHT / 2.5),
                    fill=get_color(self.game, "TEXT_COLOR_1"),
                    size=(HEIGHT // 20),
                    justify='c')

            draw_text("Action is currently bound to the " +
                      f"key{'s' if len(keys_assigned) > 1 else ''}",
                     (WIDTH * (5 / 8)),
                     (HEIGHT / 3.5),
                     fill=get_color(self.game, "TEXT_COLOR_1"),
                     size=(WIDTH // 34),
                     justify='c')

        self.draw_scene_buttons() # re-draw on top

        if self.game.is_on_prompt:

            draw_key_changing_prompt(self.game)


    def draw_scene_profiles(self) -> None:
        """
        Shows the user the current values for each attributes of a
        selected color profile.
        If possible, they can also edit such values.
        """

        theme_name = ' '.join(self.game.selected_theme.split('_'))
        draw_text(f"Current Profile: {theme_name}",
                int(WIDTH * 0.066666),
                (HEIGHT // 9),
                fill=get_color(self.game, "TEXT_COLOR_1"),
                size=(WIDTH // 27),
                anchor='w',
                justify='c')

        for menu in self.game.current_scene.menus:

            if menu.hidden:
                continue

            for button in menu.buttons_on_screen:

                if button.msg not in self.game.color_profile:
                    continue

                width_extra = (button.width // 30)
                height_extra = (button.height // 4)

                oval_x = (button.width // 30)
                oval_y = (button.height // 30)

                btn_x1 = button.x2 - width_extra * 5
                btn_y1 = button.y1 + height_extra
                btn_x2 = button.x2 - width_extra
                btn_y2 = button.y2 - height_extra

                button_color = self.game.color_profile.get(button.msg, None)
                button_outline = get_color(self.game, "TEXT_COLOR_1")

                if button_color == '':

                    draw_line(btn_x2 - oval_x,
                            btn_y1 + oval_y,
                            btn_x1 + oval_x,
                            btn_y2 - oval_y,
                            fill=button_outline, width=(WIDTH // 375))

                draw_oval(btn_x1, btn_y1, btn_x2, btn_y2,
                        outline=button_outline,
                        fill=button_color)

        if self.game.is_on_prompt:

            draw_attribute_prompt(self.game)


    def draw_scene_characters(self) -> None:
        """
        Draws the player selection scene details.
        """

        ...
