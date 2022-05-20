"""
Options Scene Module.
"""

from ...consts import HEIGHT, OPTIONS_TITLE, WIDTH
from ...utils import Label
from ...utils.menus import OptionsMenu
from ..scene import Scene


class OptionScene(Scene):
    """
    Options Scene. Contains configurable settings.
    """

    def __init__(self, name_id: str="scene-options", **kwargs) -> None:
        """
        Initializes an instance of 'OptionScene'.
        """

        super().__init__(name_id, **kwargs)
        options = OptionsMenu()
        options.show_return = True
        self.add_menu(options)

        self.add_label(Label(WIDTH // 2,
                       HEIGHT // 4,
                       OPTIONS_TITLE,
                       size=(WIDTH // 90),
                       color_name="TEXT_COLOR_1",
                       justify='c'))
