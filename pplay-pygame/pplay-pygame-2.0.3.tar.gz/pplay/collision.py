# coding= utf-8

# Modules import
from baseobject import BaseObject, BaseRectObject
from point import Point
import pygame

# -*- coding: utf-8 -*-

"""A simple class to deal with basic collision methods"""
"""
Must note that the collision is inclusive, i.e.,
occurs when one enters the other effectively,
not only when over the same position of the edge.
"""


class Collision:
    """
    minN: the Point of the top left of the N rect
    maxN: the Point of the bottom right of the N rect
    """

    @classmethod
    def collided_rect(cls, min1, max1, min2, max2):
        if min1.x >= max2.x or max1.x <= min2.x:
            return False
        if min1.y >= max2.y or max1.y <= min2.y:
            return False
        return True

    """
    args[0]: the origin Point
    args[1]: the target Point
    """

    @classmethod
    def collided(cls, obj: BaseObject, target: BaseObject):
        obj_min = Point(obj.x, obj.y)
        obj_max = Point(obj.x + obj.width, obj.y + obj.height)

        target_min = Point(target.x, target.y)
        target_max = Point(target.x + target.width, target.y + target.height)

        return cls.collided_rect(obj_min, obj_max, target_min, target_max)

    """
    Perfect-pixel collision using masks.
    """

    @classmethod
    def perfect_collision(cls, obj: BaseRectObject, target: BaseRectObject):
        """
        Both objects must extend a BaseRectObject,
        since it has the pygame.mask and pygame.Rect
        """
        if not obj.rect or not target.rect:
            return False

        offset_x = target.rect.left - obj.rect.left
        offset_y = target.rect.top - obj.rect.top

        mask_1 = pygame.mask.from_surface(obj.image)
        mask_2 = pygame.mask.from_surface(target.image)

        return not not mask_1.overlap(mask_2, (offset_x, offset_y))

    """
    Perfect collision aux - is called by GameImage
    """

    @classmethod
    def collided_perfect(cls, gameimage1, gameimage2):
        return Collision.perfect_collision(gameimage1, gameimage2)
