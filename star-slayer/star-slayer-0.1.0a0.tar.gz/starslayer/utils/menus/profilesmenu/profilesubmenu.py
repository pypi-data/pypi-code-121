"""
Profiles Sub Menu Module.
"""

from ....auxiliar import Singleton
from ....consts import SUB_MENU_LEFT
from ...hitbox import FloatTuple4
from ...menu import Menu, MenuDict


__all__ = ["ProfileSubMenu"]


class ProfileSubMenu(Menu, metaclass=Singleton):
    """
    The Controls Sub Menu.
    """


    def __init__(self,
                 area_corners: FloatTuple4=SUB_MENU_LEFT,
                 **kwargs: MenuDict) -> None:
        """
        Initializes an instance of 'ProfileSubMenu'.
        """

        kwargs.update(max_rows=7,
                      how_many_columns=2,
                      space_between_x=20,
                      space_between_y=15,
                      button_anchor='w',
                      special_btn_on_right=False)
        super().__init__(area_corners, **kwargs)
