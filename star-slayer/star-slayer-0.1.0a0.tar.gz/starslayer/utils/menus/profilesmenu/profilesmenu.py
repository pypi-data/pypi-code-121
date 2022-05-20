"""
Color Profiles Menu Module.
"""

from random import choice
from typing import TYPE_CHECKING

from ....auxiliar import Singleton, copy_dict
from ....checks import left_click, on_press
from ....consts import (DEFAULT_THEME, DEFAULT_THEME_LINES, HEIGHT,
                       PROFILES_PATH, WIDTH)
from ....files import dump_json, list_attributes, list_profiles, load_json
from ....gamelib import EventType
from ....gamelib import input as lib_input
from ....gamelib import say as lib_say
from ....gamelib import wait as lib_wait
from ...hitbox import FloatTuple4
from ...menu import ButtonKwargs, Menu, MenuDict
from .profilesubmenu import ProfileSubMenu

if TYPE_CHECKING:
    from ....state import Game
    from ....scene import Scene
    from ...button import Button


__all__ = ["ProfilesMenu"] # We DON'T want the local variable 'profilesmenu' to be exported


def create_buttons(menu: "ProfilesMenu") -> None:
    """
    Creates the buttons of the Controls Menu.
    """

    menu.clear_buttons()

    for profile in list_profiles(load_json(PROFILES_PATH)):

        @menu.button(message=profile) # pylint: disable=cell-var-from-loop
        @left_click()
        @on_press()
        def select_profile(game: "Game",
                           _scene: "Scene",
                           btn: "Button",
                           **_kwargs: ButtonKwargs) -> None:
            """
            Changes the current profile of the game for another.
            """

            game.selected_theme = btn.msg
            menu.refresh_sub_menu(game)

    @menu.button(message='+')
    @left_click()
    @on_press()
    def add_theme(game: "Game",
                  _scene: "Scene",
                  _btn: "Button",
                  **_kwargs: ButtonKwargs) -> None:
        """
        Adds a new color profile, and it is initally identical to the hidden
        profile 'DEFAULT'.
        """

        repeated_new_ones = [profile for profile in game.color_profiles
                             if profile.startswith("NEW_THEME")]
        new_theme_name = f"NEW_THEME_{len(repeated_new_ones) + 1}"

        game.color_profiles[new_theme_name] = copy_dict(game.color_profiles[DEFAULT_THEME])

        game.selected_theme = new_theme_name
        dump_json(game.color_profiles, PROFILES_PATH)
        menu.refresh_sub_menu(game)
        create_buttons(menu)


class ProfilesMenu(Menu, metaclass=Singleton):
    """
    The Profiles Menu of the game.
    """

    def __init__(self,
                 area_corners: FloatTuple4=(
                    int(WIDTH / 1.25),
                    int(HEIGHT / 5.185185),
                    int(WIDTH / 1.013513),
                    int(HEIGHT / 1.076923)
                 ),
                 **kwargs: MenuDict) -> None:
        """
        Initializes an instance of 'ProfilesMenu'.
        """

        kwargs.update(max_rows=10,
                      special_btn_on_right=False)
        super().__init__(area_corners, **kwargs)


    def refresh_sub_menu(self, game: "Game") -> None:
        """
        Refreshes the buttons of the sub menu of this particular menu.
        """

        submenu = ProfileSubMenu()
        attributes = list_attributes(game.color_profile)

        submenu.clear_buttons()

        @submenu.button(message="Change Profile Name")
        @left_click()
        @on_press()
        def change_profile_name(game: "Game",
                                _scene: "Scene",
                                _btn: "Button",
                                **_kwargs: ButtonKwargs) -> None:
            """
            Changes the name of the color profile.
            """

            user_input = lib_input("Please enter the new Profile Name")
            if user_input is None:
                return

            new_name = '_'.join(user_input.upper().split())

            if new_name == '':

                lib_say("Name not valid")
                return

            if new_name in list_profiles(game.color_profiles):

                lib_say("Name already used")
                return

            if new_name == DEFAULT_THEME:

                lib_say(choice(DEFAULT_THEME_LINES))
                return

            game.color_profiles[new_name] = game.color_profiles.pop(game.selected_theme)
            game.selected_theme = new_name

            dump_json(game.color_profiles, PROFILES_PATH)
            self.refresh_sub_menu(game)
            create_buttons(self)


        @submenu.button(message="Delete this Profile")
        @left_click()
        @on_press()
        def delete_profile(game: "Game",
                           _scene: "Scene",
                           _btn: "Button",
                           **_kwargs: ButtonKwargs) -> None:
            """
            Deletes the current profile, if it is not the last one.
            """

            if len(game.color_profiles) == 2: # +1 for the hidden theme

                lib_say("You cannot delete this color profile, as it is the only one remaining.")
                return

            themes_list = list_profiles(game.color_profiles)

            old_theme_name = game.selected_theme
            old_theme_index = themes_list.index(old_theme_name)
            game.color_profiles.pop(game.selected_theme)

            game.selected_theme = themes_list[old_theme_index - 1]
            dump_json(game.color_profiles, PROFILES_PATH)
            self.refresh_sub_menu(game)
            create_buttons(self)


        for attr in attributes:

            @submenu.button(message=attr) # pylint: disable=cell-var-from-loop
            @left_click()
            @on_press()
            def select_att_color(game: "Game",
                                 _scene: "Scene",
                                 btn: "Button",
                                 **_kwargs: ButtonKwargs) -> None:
                """
                Prompts the user to select a new color.
                """

                game.attribute_to_edit = btn.msg
                game.go_prompt()


    def prompt(self, *_args, **kwargs) -> bool:
        """
        Executes the logic of the color selection.
        """

        game: "Game" = kwargs.get("game")
        selector = game.color_selector

        while True:

            event = lib_wait(EventType.ButtonPress)
            kwargs.update(event_type=EventType.ButtonPress,
                          mouse_button=event.mouse_button)

            selector.click(event.x,
                           event.y,
                           game.color_profile,
                           game.attribute_to_edit,
                           **kwargs)

            if selector.next:

                selector.next = False
                break

            if selector.exit:

                selector.exit = False
                game.attribute_to_edit = None

                dump_json(game.color_profiles, PROFILES_PATH)
                game.is_on_prompt = False

                break


profilesmenu = ProfilesMenu() # instantiated temporarily
create_buttons(profilesmenu)
