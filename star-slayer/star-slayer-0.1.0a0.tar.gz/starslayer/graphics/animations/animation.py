"""
Animation abstract class Module.
"""

from abc import ABC, abstractmethod
from typing import Tuple


# pylint: disable=invalid-name
class Animation(ABC):
    """
    Abstract class for a defined Animation.
    """

    def __init__(self,
                 x1: float,
                 y1: float,
                 x2: float,
                 y2: float,
                **kwargs) -> None:
        """
        Initializes an instance of type 'Animation'.
        """

        if not all((x1, y1, x2, y2)):
            raise ValueError("All corner coordinates must be present.")

        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

        self.properties = kwargs


    @property
    def area(self) -> Tuple[int, int, int, int]:
        """
        Defines the area in which the animation takes place.
        """

        return self.x1, self.y1, self.x2, self.y2


    @abstractmethod
    def animate(self) -> None:
        """
        Proceeds with the animation.
        """

        ...


    @abstractmethod
    def post_hook(self) -> None:
        """
        For anything that needs atention after an animation frame.
        """

        ...
