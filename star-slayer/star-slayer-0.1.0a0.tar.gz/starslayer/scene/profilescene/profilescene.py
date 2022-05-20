"""
Color Profiles Scene Module.
"""

from ...consts import HEIGHT, PROFILES_TITLE, WIDTH
from ...utils import Label
from ...utils.menus import ProfilesMenu, ProfileSubMenu
from ..scene import Scene


class ProfileScene(Scene):
    """
    Porfiles Scene. Contains configurable color profiles.
    """

    def __init__(self, name_id: str="scene-profiles", **kwargs) -> None:
        """
        Initializes an instance of 'ProfileScene'.
        """

        super().__init__(name_id, **kwargs)
        profiles = ProfilesMenu()
        profiles.show_return = True
        self.add_menu(profiles)

        subprofiles = ProfileSubMenu()
        self.add_menu(subprofiles)

        self.add_label(Label(int(WIDTH * 0.893333),
                             (HEIGHT // 15),
                             PROFILES_TITLE,
                             size=(HEIGHT // 235),
                             color_name="TEXT_COLOR_1",
                             justify='c'))
