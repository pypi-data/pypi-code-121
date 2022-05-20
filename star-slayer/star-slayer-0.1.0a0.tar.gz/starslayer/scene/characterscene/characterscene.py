"""
Characters Selection Scene Module.
"""

from ...consts import (BILBY_TANKA_REL_PATH, CHARACTERS_TITLE, HEIGHT,
                       STAR_SLAYER_REL_PATH, VIPER_DODGER_REL_PATH, WIDTH)
from ...sprites import Sprite
from ...utils import Label
from ...utils.menus import CharactersMenu
from ..scene import Scene


class CharacterScene(Scene):
    """
    Characters Selection Scene. It shows once
    when the user must choose a player ship.
    """

    def __init__(self, name_id: str="scene-characters", **kwargs) -> None:
        """
        Initializes an instance of 'CharacterScene'.
        """

        super().__init__(name_id, **kwargs)
        characters = CharactersMenu()
        self.add_menu(characters)

        self.add_label(Label(WIDTH / 2,
                             HEIGHT / 7,
                             CHARACTERS_TITLE,
                             size=(WIDTH // 100),
                             color_name="TEXT_COLOR_1",
                             justify='c'))

        self.add_sprite(Sprite(STAR_SLAYER_REL_PATH),
                        x1=int((WIDTH / 9) - (WIDTH * 0.08)),
                        y1=int(HEIGHT * 0.5),
                        x2=int((WIDTH / 9) * 1.7 + (WIDTH * 0.08)),
                        y2=int(HEIGHT * 0.8))
        self.add_sprite(Sprite(BILBY_TANKA_REL_PATH),
                        x1=int((WIDTH / 9) * 2.7 + (WIDTH * 0.08)),
                        y1=int(HEIGHT * 0.5),
                        x2=int((WIDTH / 9) * 4.7 + (WIDTH * 0.08)),
                        y2=int(HEIGHT * 0.8))
        self.add_sprite(Sprite(VIPER_DODGER_REL_PATH),
                        x1=int((WIDTH / 9) * 5.7 + (WIDTH * 0.08)),
                        y1=int(HEIGHT * 0.5),
                        x2=int((WIDTH / 9) * 8 + (WIDTH * 0.08)),
                        y2=int(HEIGHT * 0.8))
