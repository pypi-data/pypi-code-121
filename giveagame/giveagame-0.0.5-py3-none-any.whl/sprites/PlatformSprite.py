from giveagame.sprites.Sprite import *
from giveagame.Coords import *

class PlatformSprite(Sprite):
    def __init__(self, game, photo_image, x, y, width, height):
        Sprite.__init__(self, game)
        self.photo_image = photo_image
        self.image = game.canvas.create_image(x, y, \
                                              image=self.photo_image, anchor='nw')
        self.coordinates = Coords(x, y, x + width, y + height)