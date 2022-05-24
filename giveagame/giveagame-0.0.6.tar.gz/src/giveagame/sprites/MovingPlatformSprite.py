from giveagame.sprites.Sprite import *
from giveagame.sprites.PlatformSprite import *
import time

class MovingPlatformSprite(PlatformSprite):
    def __init__(self, game, photo_image, x, y, width, height):
        PlatformSprite.__init__(self, game, photo_image, x, y, \
                                width, height)
        self.x = 2
        self.counter = 0
        self.last_time = time.time()
        self.width = width
        self.height = height

    def coords(self):
        xy = self.game.canvas.coords(self.image)
        self.coordinates.x1 = xy[0]
        self.coordinates.y1 = xy[1]
        self.coordinates.x2 = xy[0] + self.width
        self.coordinates.y2 = xy[1] + self.height
        return self.coordinates

    def move(self):
        if time.time() - self.last_time > 0.03:
                self.last_time = time.time()
                self.game.canvas.move(self.image, self.x, 0)
                self.counter = self.counter + 1
                if self.counter > 20:
                    self.x = self.x * -1
                    self.counter = 0