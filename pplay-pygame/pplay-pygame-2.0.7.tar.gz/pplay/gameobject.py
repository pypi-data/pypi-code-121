# coding= utf-8

"""The most basic game class"""

from pplay.baseobject import BaseObject
from pplay.collision import Collision
from pplay.sound import Sound


class GameObject(BaseObject):
    """Creates a GameObject in X, Y co-ords, with Width x Height"""

    def __init__(self):
        super(GameObject, self).__init__()
        self.sound = None

    def collided(self, target: BaseObject):
        return Collision.collided(self, target)

    def load_sound(self, sound_file):
        self.sound = Sound(sound_file)
