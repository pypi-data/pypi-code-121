"""
Scenes Module. Dictates how a scene contains menus and
the content on display.
"""

from re import match
from typing import TYPE_CHECKING, Dict, Generator, List, Optional

from ..sprites import Sprite
from ..utils import ButtonKwargs, Label, Menu, Timer

if TYPE_CHECKING:

    from ..graphics.animations import Animation
    from ..state import Game

MenuList = List[Menu]
LabelDict = Dict[str, Label]
SpriteProperties = Dict[str, int | Sprite]
SpritesDict = Dict[str, SpriteProperties]
AnimationsDict = Dict[str, "Animation"]
SceneDict = Dict[str, "Scene"]


class Scene:
    """
    A scene that contains elements.
    """

    def __init__(self, name_id: str, **kwargs) -> None:
        """
        Initializes an instance of 'Scene'.
        """

        self._name_id: str = name_id
        self._selected_menu_index: int = -1
        self._menus: MenuList = []
        self._labels: LabelDict = {}
        self._sprites: SpritesDict = {}
        self._rear_animations: AnimationsDict = {}
        self._front_animations: AnimationsDict = {}

        self.parent: Optional["Scene"] = kwargs.get("parent", None)

        # Timers
        self.press_cooldown = Timer(20)


    def __eq__(self, other: "Scene") -> bool:
        """
        Checks if the scene has the same id as 'other'.
        """

        if not isinstance(other, __class__):
            return False

        return self.id == other.id


    @property
    # pylint: disable=invalid-name
    def id(self) -> str:
        """
        Returns the unique name of the scene.
        """

        return self._name_id


    @property
    def menus(self) -> MenuList:
        """
        Returns all the menus of the scene.
        """

        return self._menus


    @property
    def selected_menu(self) -> Optional[Menu]:
        """
        Returns the selected menu, if any.
        """

        if self._selected_menu_index < 0:
            return None

        return self.menus[self._selected_menu_index]


    @property
    def labels(self) -> LabelDict:
        """
        Returns all the labels of the scene.
        """

        return self._labels


    def find_label_match(self, pattern: str) -> Generator[Label, None, None]:
        """
        Yields each label whose name matches the regex pattern.
        """

        for label_name, label in self.labels.items():
            if match(pattern, label_name):
                yield label


    @property
    def sprites(self) -> SpritesDict:
        """
        Returns all the sprites of the scene.
        """

        return self._sprites


    def find_sprite_prop_match(self, pattern: str) -> Generator[Sprite, None, None]:
        """
        Yields each sprite whose name matches the regex pattern.
        """

        for sprite_name, sprite_properties in self.sprites.items():
            if match(pattern, sprite_name):
                yield sprite_properties


    @property
    def rear_animations(self) -> AnimationsDict:
        """
        Returns all the animations in the scene.
        """

        return self._rear_animations


    @property
    def front_animations(self) -> AnimationsDict:
        """
        Returns all the front animations in the scene.
        These ones are special in that they are drawn above
        everything else.
        """

        return self._front_animations


    def find_animation_match(self, pattern: str) -> Generator["Animation", None, None]:
        """
        Yields each animation whose name matches the regex pattern.
        """

        for rear_anim_name, rear_anim in self.rear_animations.items():
            if match(pattern, rear_anim_name):
                yield rear_anim

        for front_anim_name, front_anim in self.front_animations.items():
            if match(pattern, front_anim_name):
                yield front_anim


    def get_default_name(self, elem_name: str, dictionary: Dict) -> str:
        """
        Gets a default name when it is not provided.
        """

        how_many = len([key for key in dictionary if (isinstance(key, str) and
                                                      key.startswith(f"{elem_name}_"))])

        return f"{elem_name}_{str(how_many + 1).zfill(3)}"


    def add_menu(self, menu: Menu) -> None:
        """
        Adds a new menu to the scene.
        """

        if not self.selected_menu:

            self._selected_menu_index = 0

        self.menus.append(menu)


    # pylint: disable=invalid-name
    def add_label(self,
                  label: Optional[Label]=None,
                  name: Optional[str]=None,
                  *,
                  x: Optional[float]=None,
                  y: Optional[float]=None,
                  text: str='',
                  **kwargs) -> None:
        """
        Adds a label to the scene.
        """

        if not name:
            name = self.get_default_name("label", self.labels)

        if label:
            self.labels[name] = label
            return

        if not all((x, y)):
            return

        self.labels[name] = Label(x=x,
                                  y=y,
                                  text=text,
                                  **kwargs)


    def add_sprite(self,
                   sprite: Optional[Sprite]=None,
                   name: Optional[str]=None,
                   *,
                   texture_path: Optional[str]=None,
                   spr_type: str="BOX",
                   **kwargs) -> None:
        """
        Adds a sprite to the scene.
        """

        if not name:
            name = self.get_default_name("sprite", self.sprites)

        if not sprite:
            if not texture_path:
                return

            sprite = Sprite(texture_path)

        kwargs.update(sprite=sprite,
                      spr_type=spr_type)
        self.sprites[name] = kwargs


    def add_animation(self,
                      animation: "Animation",
                      name: Optional[str]=None,
                      *,
                      is_front: bool=False) -> None:
        """
        Adds an animation to the scene.
        """

        if is_front:
            anim_list = self.front_animations
        else:
            anim_list = self.rear_animations

        if not name:
            name = self.get_default_name("animation", anim_list)

        anim_list[name] = animation


    def change_selection(self, reverse: bool=False) -> None:
        """
        Changes the current selected menu.
        """

        if self.menus:

            i = (-1 if reverse else 1)
            self._selected_menu_index = (self._selected_menu_index + i) % len(self.menus)


    # pylint: disable=invalid-name
    def execute_button(self, game: "Game", x: int, y: int, **kwargs: ButtonKwargs) -> bool:
        """
        Tries to execute a button from a menu it has.
        """

        for m in self.menus:

            if m.hidden:
                continue

            if m.execute_btn(game, self, x, y, **kwargs):
                return True

        return False


    def prompt(self, *args, **kwargs) -> None:
        """
        Searches if any menu can prompt the user.
        """

        for menu in self.menus:
            if menu.prompt(*args, **kwargs):
                return


    def resfresh_sub_menus(self, game: "Game") -> None:
        """
        Attemps to refresh a sub-menu for every menus the scene has.
        """

        for menu in self.menus:
            menu.refresh_sub_menu(game)


    def refresh_hook(self) -> None:
        """
        Hook for refreshing the scene. Useful if something is needed
        to be done every time the scene is in display.

        It must be overriden to be used.
        """

        return None


    def reset_hook(self) -> None:
        """
        Hook for resetting the scene. If the current scene is changed,
        this will be called to clean up what would be needed.

        It must be overriden to be used.
        """

        return None
