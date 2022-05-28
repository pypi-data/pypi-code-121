from enum import Enum


class CommonColor(Enum):
    """An enum that defines common colors.
    Contains red, green, blue, cyan, yellow, magenta, white and black.
    """

    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    yellow = (255, 255, 0)
    white = (255, 255, 255)
    black = (0, 0, 0)
