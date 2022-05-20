"""
Controls Scene Module.
"""

from ...consts import CONTROLS_TITLE, HEIGHT, WIDTH
from ...utils import Label
from ...utils.menus import ControlsMenu, ControlSubMenu
from ..scene import Scene


class ControlScene(Scene):
    """
    Controls Scene. Contains configurable controls.
    """

    def __init__(self, name_id: str="scene-controls", **kwargs) -> None:
        """
        Initializes an instance of 'ControlScene'.
        """

        super().__init__(name_id, **kwargs)
        controls = ControlsMenu()
        controls.show_return = True
        self.add_menu(controls)

        subcontrols = ControlSubMenu()
        self.add_menu(subcontrols)

        self.add_label(Label(int(WIDTH * 0.130666),
                             (HEIGHT // 15),
                             CONTROLS_TITLE,
                             size=(HEIGHT // 235),
                             color_name="TEXT_COLOR_1",
                             justify='c'))
