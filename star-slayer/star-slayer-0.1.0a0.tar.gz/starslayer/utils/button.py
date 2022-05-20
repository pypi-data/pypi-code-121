"""
Button Module. A button is a hitbox with
a message and a designed handler.
"""

from typing import Callable, TYPE_CHECKING, List, Optional

from .hitbox import HitBox

if TYPE_CHECKING:

    from ..state import Game
    from ..scene import Scene

ButtonsList = List["Button"]
ButtonHandler = Callable[["Game", "Scene", "Button"], None]


class Button(HitBox):
    """
    Class for defining a hitbox of a button and
    a message it can carry.
    """

    def __init__(self, **kwargs: dict[str, int | str]) -> None:
        """
        Initializes an instance of type 'Button'.
        """

        super().__init__(**kwargs)

        self.msg: str = kwargs.get("message", '')
        self.handler: Optional[ButtonHandler] = kwargs.get("handler", None)


    def __str__(self) -> str:
        """
        Returns a string with class information so it can be printed later.
        """

        return f"Button at {self.all_coords} with message '{self.msg}'"


    def __eq__(self, other: "Button") -> bool:
        """
        Tests if the coordinates and the message is the same.
        """

        return super().__eq__(other) and (self.msg == other.msg)


    def is_inside(self, eval_x: int, eval_y: int) -> bool:
        """
        Returns 'True' if some given coordinates are inside the hitbox
        of this button.
        """

        return (self.x1 <= eval_x <= self.x2) and (self.y1 <= eval_y <= self.y2)
