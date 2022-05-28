import math
from pyRetroGame.vector import Vector2


class gameMath:
    def __init__(self):
        pass

    def distance(A_position : Vector2, B_position : Vector2):
        return math.sqrt((A_position.x - B_position.x)**2 + (A_position.y - B_position.y)**2)
