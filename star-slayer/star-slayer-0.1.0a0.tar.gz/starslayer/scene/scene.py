"""
Scenes Module. Dictates how a scene contains menus and
the content on display.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..sprites import Sprite
from ..utils import ButtonKwargs, Label, Menu, Timer

if TYPE_CHECKING:

    from ..graphics.animations import Animation
    from ..state import Game

MenuList = List[Menu]
LabelList = List[Label]
SpriteProperties = Dict[str, int | Sprite]
SpritesList = List[SpriteProperties]
AnimationsList = List["Animation"]
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
        self._labels: LabelList = []
        self._sprites: SpritesList = []
        self._rear_animations: AnimationsList = []
        self._front_animations: AnimationsList = []

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
    def labels(self) -> LabelList:
        """
        Returns all the labels of the scene.
        """

        return self._labels


    @property
    def sprites(self) -> SpritesList:
        """
        Returns all the sprites of the scene.
        """

        return self._sprites


    @property
    def rear_animations(self) -> AnimationsList:
        """
        Returns all the animations in the scene.
        """

        return self._rear_animations


    @property
    def front_animations(self) -> AnimationsList:
        """
        Returns all the front animations in the scene.
        These ones are special in that they are drawn above
        everything else.
        """

        return self._front_animations


    def add_menu(self, menu: Menu) -> None:
        """
        Adds a new menu to the scene.
        """

        if not self.selected_menu:

            self._selected_menu_index = 0

        self.menus.append(menu)


    def add_label(self, label: Optional[Label]=None, **kwargs) -> None:
        """
        Adds a label to the scene.
        """

        if label:
            self.labels.append(label)
            return

        self.labels.append(Label(x=kwargs.get("x"),
                                 y=kwargs.get("y"),
                                 text=kwargs.get("text", ''),
                                 **kwargs))


    def add_sprite(self, sprite: Optional[Sprite]=None, **kwargs) -> None:
        """
        Adds a sprite to the scene.
        """

        if not sprite:
            sprite = Sprite(kwargs.get("texture_path"))

        kwargs.update(sprite=sprite)
        self.sprites.append(kwargs)


    def add_animation(self, animation: "Animation", is_front: bool=False) -> None:
        """
        Adds an animation to the scene.
        """

        if is_front:
            anim_list = self.front_animations
        else:
            anim_list = self.rear_animations

        anim_list.append(animation)


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
