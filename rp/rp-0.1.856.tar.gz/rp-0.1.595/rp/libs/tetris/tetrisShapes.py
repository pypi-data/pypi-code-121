import os
dir_path = os.path.dirname(os.path.realpath(__file__))
import sys
sys.path.append(os.path.join(dir_path,'graphics'))
from graphics import shapes, funcs

class Shape(shapes.Image):
    def __init__(self, n):
        self.n = n
        self.direction = 0

    def image(self):
        return funcs.rotateImage((
            ((1, 1),
             (1, 1)),

            ((0, 1, 0),
             (1, 1, 1)),

            ((1, 0, 0),
             (1, 1, 1)),

            ((0, 0, 1),
             (1, 1, 1)),

            ((1, 1, 1, 1),),

            ((0, 1, 1),
             (1, 1, 0)),

            ((1, 1, 0),
             (0, 1, 1))
        )[self.n], self.direction)
