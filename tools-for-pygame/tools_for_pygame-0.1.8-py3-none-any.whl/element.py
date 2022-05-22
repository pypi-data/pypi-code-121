#!/usr/bin/env python3
from __future__ import annotations

import time
from typing import Optional, Iterable, Callable, Union

import pygame

from .constants import UL
from .mathf import clamp, Pos, Size
from .type_hints import _pos, _size, _col_type

pygame.init()

_point_to_rect_point = {
    "ul": "topleft",
    "dl": "bottomleft",
    "ur": "topright",
    "dr": "bottomright",
    "uc": "midtop",
    "cl": "midleft",
    "dc": "midbottom",
    "cr": "midright",
    "cc": "center"
}


class Element(pygame.sprite.Sprite):
    """
    Element(pygame.sprite.Sprite)

    Type: class

    Description: base class that supports a position, an image, a size,
        a rotation and an alpha

    Args:
        'pos' (pgt.Pos): the position of the element
        'size' (pgt.Size): the size of the element, defaults to (0, 0)
        'image' (pygame.Surface): the image of the element, if set to
            None the element won't be displayed
        'pos_point' (str): the point the position refers to
        'anchor_element' (pgt.Element): element to witch this element is
            anchored to, if set there is no need to set the 'pos'
            argument
        'anchor_point' (str): the point of the 'anchor_element' that
            this element anchors to, defaults to pgt.UL
        'point' (str?): attribute that overwrites 'pos_point' and
            'anchor_point' to set them to the same point
        'offset' (pgt.Pos): the offset of the element from 'pos' or the
            point of the 'anchor_element'
        'img_offset' (pgt.Pos): offset of the image from the top-left
            corner of the element
        'alpha' (int): transparency of the element (from 0 to 255),
            doesn't rise errors, the value is camped
        'rotation' (int): rotation in degrees of the element
        'hidden' (boon): if the element is hidden

    Attrs:
        'rect' (pygame.Rect): rect of the element with position and size
        'image' (pygame.Surface?): see 'image' in arguments
        '__backup_image' (pygame.Surface?): if the element is rotated,
            is a copy of 'image' not rotated, to not lose quality
        '_pos_point' (str): see 'pos_point' in arguments
        '__a_element' (pgt.Element?): see 'anchor_element' in arguments
        '_a_point' (str?): see 'anchor_point' in arguments
        'offset' (pgt.Pos): see 'offset' in arguments
        'img_offset' (pgt.Pos): see 'img_offset' in arguments
        'alpha' (int): see 'alpha in arguments'
        '_rot' (int): the current rotation of the element in degrees
        'hidden' (bool): if the element is currently hidden
        'is_anchored' (bool): if the element is currently anchored
        'u' (int): up
        'd' (int): down
        'l' (int): left
        'r' (int): right
        'ul' (pgt.Pos): up-left
        'uc' (pgt.Pos): up-centre
        'ur' (pgt.Pos): up-right
        'cl' (pgt.Pos): centre-left
        'cc' (pgt.Pos): centre-centre
        'cr' (pgt.Pos): centre-right
        'dl' (pgt.Pos): down-left
        'dc' (pgt.Pos): down-centre
        'dr' (pgt.Pos): down-right
        'pos' (pgt.Pos): position of the '_pos_point' of the element
        'size' (pgt.Size): size of the element
        '_size' (pgt.Size): the original size of the element (without
            rotation or scaling)
        'x' (int): x position of the element
        'y' (int): y position of the element
        'w' (int): width of the element
        'h' (int): height of the element

    Methods:
        - anchor(anchor_element, anchor_point)
        - _update_anchor_pos()
        - handle_event()
        - rotate(angle, abs_, colorkey)
        - scale(size, smooth, point)
        - change_image(surface)
        - collide(other)
        - collide_point(point)
        - show()
        - hide()
        - draw(surface, pos, point, offset, flag, show_rect, rect_color)
    """
    def __init__(self,
                 pos: _pos = None,
                 size: _size = Size(0),
                 image: Optional[pygame.Surface] = None,
                 pos_point: str = UL,
                 anchor_element: Optional[Element] = None,
                 anchor_point: str = UL,
                 point: Optional[str] = None,
                 offset: _pos = Pos(0),
                 img_offset: _pos = Pos(0),
                 alpha: int = 255,
                 rotation: int = 0,
                 hidden: bool = False):
        pygame.sprite.Sprite.__init__(self)
        size = Size(size)
        self.rect = pygame.Rect((0, 0), size)
        self._size = size
        self.image = image
        self.__backup_image = None if rotation == 0 else image

        if self.image: self.image.set_alpha(clamp(alpha, 0, 255))
        self._alpha = alpha

        self.__offset = Pos(offset)
        self.img_offset = Pos(img_offset)
        self.hidden = hidden
        self._pos_point = point if point else pos_point
        self._a_point = point if point else anchor_point

        if pos is not None:
            self.__a_element = None
            self.pos = pos + self.__offset
        elif anchor_element is not None:
            self.__a_element = anchor_element
            self.pos = getattr(self.__a_element, self._a_point) + self.__offset
        else:
            self.__a_element = None
            self.pos = self.__offset

        self._rot = 0
        if rotation != 0:
            if self.image is not None:
                self.rotate(rotation)
            else:
                self._rot = rotation

    def __eq__(self, other):
        return self.size == other.size \
               and self.image == other.image \
               and self._rot == other._rot \
               and self._alpha == other._alpha \
               and self.pos == other.pos

    def __repr__(self):
        return f"{self.__class__.__name__}(pos={self.pos}, size={self.size}, " \
               f"anchor_element={self.__a_element}, rotation={self._rot}, " \
               f"alpha={self.alpha})"

    @property
    def u(self): return self.rect.top
    @property
    def d(self): return self.rect.bottom
    @property
    def l(self): return self.rect.left
    @property
    def r(self): return self.rect.right
    @property
    def ul(self): return Pos(self.rect.topleft)
    @property
    def uc(self): return Pos(self.rect.midtop)
    @property
    def ur(self): return Pos(self.rect.topright)
    @property
    def cl(self): return Pos(self.rect.midleft)
    @property
    def cc(self): return Pos(self.rect.center)
    @property
    def cr(self): return Pos(self.rect.midright)
    @property
    def dl(self): return Pos(self.rect.bottomleft)
    @property
    def dc(self): return Pos(self.rect.midbottom)
    @property
    def dr(self): return Pos(self.rect.bottomright)

    @u.setter
    def u(self, value): self.rect.top = round(value)
    @d.setter
    def d(self, value): self.rect.bottom = round(value)
    @l.setter
    def l(self, value): self.rect.left = round(value)
    @r.setter
    def r(self, value): self.rect.right = round(value)
    @ul.setter
    def ul(self, value): self.rect.topleft = round(Pos(value))
    @uc.setter
    def uc(self, value): self.rect.midtop = round(Pos(value))
    @ur.setter
    def ur(self, value): self.rect.topright = round(Pos(value))
    @cl.setter
    def cl(self, value): self.rect.midleft = round(Pos(value))
    @cc.setter
    def cc(self, value): self.rect.center = round(Pos(value))
    @cr.setter
    def cr(self, value): self.rect.midright = round(Pos(value))
    @dl.setter
    def dl(self, value): self.rect.bottomleft = round(Pos(value))
    @dc.setter
    def dc(self, value): self.rect.midbottom = round(Pos(value))
    @dr.setter
    def dr(self, value): self.rect.bottomright = round(Pos(value))

    @property
    def pos(self):
        return getattr(self, self._pos_point)

    @pos.setter
    def pos(self, value):
        setattr(self, self._pos_point, value)

    @property
    def x(self):
        return self.pos.x
    @property
    def y(self):
        return self.pos.y

    @x.setter
    def x(self, value):
        self.pos = (round(value), self.y)
    @y.setter
    def y(self, value):
        self.pos = (self.x, round(value))

    @property
    def size(self):
        return Size(self.rect.size)

    @size.setter
    def size(self, value):
        self.rect.size = round(Size(value))

    @property
    def w(self):
        return self.size.w
    @property
    def h(self):
        return self.size.h

    @w.setter
    def w(self, value):
        self.size = (round(value), self.h)
    @h.setter
    def h(self, value):
        self.size = (self.w, round(value))

    @property
    def offset(self):
        return self.__offset

    @offset.setter
    def offset(self, value):
        value = Pos(value)
        self.pos -= self.__offset
        self.pos += value
        self.__offset = value

    @property
    def alpha(self):
        if self.image: return self.image.get_alpha()
        else: return 0

    @alpha.setter
    def alpha(self, value):
        if self.image: self.image.set_alpha(clamp(value, 0, 255))
        self._alpha = value

    @property
    def is_anchored(self):
        return self.__a_element is not None

    def anchor(self,
               anchor_element: Element,
               anchor_point: Optional[str] = None) -> None:
        """
        anchor(self, anchor_element, anchor_point=None)

        Type: method

        Description: anchors the element to another one

        Args:
            'anchor_element' (Element?): the element to anchor to, if
                set to None, the anchor is removed
            'anchor_point' (str): the point of the 'anchor_element' that
                this element anchors to, if None, defaults to the point
                given on initialization

        Return type: None
        """
        if anchor_element is not None and \
           not isinstance(anchor_element, Element):
            raise TypeError("Expected an instance of Element, got "\
                           f"'{anchor_element.__class__.__name__}' instead")

        self.__a_element = anchor_element

        if anchor_element is None:
            return

        # anchor_point overwrites self._a_point
        if anchor_point is not None:
            self._a_point = anchor_point
        setattr(self, self._pos_point,
                getattr(self.__a_element, self._a_point) + self.__offset)

    def _update_anchor_pos(self):
        """Updates the element's position when it's anchored"""
        if self.__a_element is not None:
            setattr(self, self._pos_point,
                getattr(self.__a_element, self._a_point) + self.__offset)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        handle_event(self, event: pygame.event.Event)

        Type: method

        Description: a method to overwrite in custom classes which
            inherit from pgt.Element and need to handle some user event,
            returns True if the event was handles, else False

        Args:
            'event' (pygame.event.Event): the event to handle

        Return type: bool
        """
        return False

    def rotate(self,
               angle: int,
               abs_: bool = False,
               colorkey: _col_type = (0, 0, 0)) -> None:
        """
        rotate(self, angle, abs_=False, colorkey=(0, 0, 0))

        Type: method

        Description: rotates the element and resizes it to fit the size
            of the newly rotated image, the position doesn't change

        Args:
            'angle' (int): angle of the rotation in degrees
            'abs_' (bool): if the rotation should be absolute
            'colorkey' (iterable): the colorkey set to the image of the
                element after it's been rotated

        Return type: None
        """
        prev_pos = self.pos.copy()

        # Makes a backup to not lose quality
        if self.__backup_image is None:
            self.__backup_image = self.image.copy()
        elif self.__backup_image is not None:
            self.image = self.__backup_image.copy()

        self.image.set_colorkey(colorkey)

        angle += self._rot if not abs_ else 0

        # Rotates the image
        if angle != 0:
            if not angle % 90:
                self.image = pygame.transform.rotate(self.image, angle)
            else:
                self.image = pygame.transform.rotozoom(self.image, angle, 1)
                self.image.set_alpha(self._alpha)
            self._rot = angle

        self._rot %= 360

        self.size = self.image.get_size()
        self.image.set_colorkey(colorkey)

        self.pos = prev_pos

    def scale(self,
              size: _size,
              smooth: bool = False,
              point: Optional[str] = None) -> None:
        """
        scale(self, size, smooth=False, point=None)

        Type: method

        Description: scales the element's image and the size accordingly,
            the position doesn't change

        Args:
            'size' (Size): the new size of the image
            'smooth' (bool): if the function should use
                'pygame.transform.smoothscale' instead of
                'pygame.transform.scale'
            'point' (Pos): the point that doesn't change it's position,
                if None, defaults to the element's 'pos' property

        Return type: None
        """
        # Makes a backup to not lose quality
        if self.__backup_image is None:
            self.__backup_image = self.image.copy()
        else:
            self.image = self.__backup_image.copy()
        size = Size(size)
        prev_pos = self.pos.copy() if point is None else getattr(self, point)

        # Scales the image
        if smooth:
            self.image = pygame.transform.smoothscale(self.image, size)
        else:
            self.image = pygame.transform.scale(self.image, size)

        self.size = size

        # Updates the position
        if point is None:
            self.pos = prev_pos
        else:
            setattr(self, point, prev_pos)

    def change_image(self, surface: pygame.Surface) -> None:
        """
        change_image(self, surface)

        Type: method

        Description: changes the image of an element re-applying alpha
            and rotation (hence this method calls Element.rotate)

        Args:
            'surface' (pygame.Surface): the new element's image

        Return type: None
        """
        if not isinstance(surface, pygame.Surface):
            raise TypeError("Expected 'surface' to be pygame.Surface, "
                           f"got '{surface.__class__.__name__}' instead")

        self.image = surface

        # Change the values to match the previous image
        self.image.set_alpha(self._alpha)
        if self.__backup_image is not None:
            self.__backup_image = self.image.copy()
        self.rotate(self._rot, True)

    def collide(self, other: pygame.sprite.Sprite) -> bool:
        """
        collide(self, other)

        Type: method

        Description: checks for collision with another element, sprite
            or rect

        Args:
            'other' (Element, pygame.sprite.Sprite, pygame.Rect): the
                object to check the collision against

        Return type: bool, returns False if hidden
        """
        if self.hidden: return False

        # An element is a subclass of pygame.sprite.Sprite
        if isinstance(other, pygame.sprite.Sprite):
            return self.rect.colliderect(other.rect)
        elif isinstance(other, pygame.Rect):
            return self.rect.colliderect(other)
        else:
            raise TypeError("Expected 'other' to be pygame.Rect or "
                           f"pygame.sprite.Sprite, got '{other.__class__.__name__}'"
                            " instead")

    def collide_point(self, point: _pos) -> bool:
        """
        collide_point(self, point)

        Type: method

        Description: checks the collision of the element with a point

        Args:
            'point' (Pos): the point to check the collision against

        Return type: bool, returns False if hidden
        """
        if self.hidden: return False
        return self.rect.collidepoint(Pos(point))

    def show(self) -> None:
        """Shows the element"""
        self.hidden = False

    def hide(self) -> None:
        """Hides the element"""
        self.hidden = True

    def draw(self,
             surface: pygame.Surface,
             pos: _pos = None,
             point: str = UL,
             offset: Optional[_pos] = None,
             flags: int = 0,
             show_rect: bool = False,
             rect_color: _col_type = (255, 0, 255)) -> None:
        """
        draw(self,
             surface,
             pos=None,
             point=None,
             flags=0,
             show_rect=False,
             rect_color=pgt.MAGENTA)

        Type: method

        Description: draws the element onto a surface

        Args:
            'surface' (pygame.Surface): the surface to draw the image on
            'pos' (Pos): a position that overwrites the element's pos
            'point' (str): used only when 'pos' is not None, the point
                the position refers to
            'offset' (Pos): overwrites the element's 'img_offset'
            'flags' (int): special flags for pygame.Surface.blit
            'show_rect' (bool): if the rect of the element should be shown
            'rect_color' (tuple): the color of the rect if shown

        Return type: None
        """
        # If the element is anchored and there is no arbitrary position set,
        # get the position of the element
        if pos is None: self._update_anchor_pos()

        if self.hidden or self.image is None:
            if show_rect:
                pygame.draw.rect(surface, rect_color, self.rect, 1)
            return

        # Sets the position based on the parameters given in the arguments
        if pos is None:
            pos = self.ul
        else:
            if not isinstance(pos, pygame.Rect):
                pos = pygame.Rect(Pos(pos), self.size)

            if point is not None:
                attr = _point_to_rect_point.get(point, None)
                if attr is None:
                    raise ValueError("invalid point for "\
                                    f"{self.__class__.__name__}.draw()")
                pos = getattr(pos, attr)
            else:
                pos = pos.topleft

        # Sets the offset
        if offset is not None: pos += offset
        else: pos += self.img_offset

        # Draws the image
        surface.blit(self.image, pos, special_flags=flags)

        # Draws the rectangle if requested
        if show_rect:
            pygame.draw.rect(surface, rect_color, self.rect, 1)


class AniElement(Element):
    """
    AniElement(Element)

    Type: class

    Description: Element that supports animations, for more about the
        elements see 'help(pgt.Element)' for more about animations,
        see 'help(pgt.animations)'

    Args:
        'animations' (list): a list that contains all the animations of
            the element (the 'element' argument of the animations is
            set automatically)

    Attrs:
        'current_ani' (list[str]): the names of the animations that are
            currently running
        any animation can be accessed as an attribute named after the
        name of the animation (to access an animation called "jump" of
        'player_sprite' you write 'player_sprite.jump')

    Methods:
        add_ani(ani)
        update_ani(global_time=None)
        draw(*args, **kwargs, update_ani=False)

    Notes:
        - if the element is hidden all the animations are still updated
        - animations with the names '_show' and '_hide' will start when
          calling the show() or hide() methods, the element is hidden
          at the end of the '_hide' animation
    """
    def __init__(self,
       animations: Optional[Iterable] = None,
       *args, **kwargs):
        super().__init__(*args, **kwargs)

        if animations is None: animations = ()

        for i in animations:
            self.add_ani(i)

        self.current_ani = []
        self.is_hiding = False

    def show(self):
        self.hidden = False
        try:
            self._show.start()
        except AttributeError:
            pass

    def hide(self):
        try:
            self._hide.start()
            self.is_hiding = True
        except AttributeError:
            self.hidden = True

    def add_ani(self, ani):
        """
        add_ani(self, ani)

        Type: method

        Description: adds an animation to the element

        Args:
            'ani' (ani.AniBase): the animation to add

        Return type: None
        """
        setattr(self, ani.name, ani)
        ani.set_new_element(self)

    def update_ani(self, global_time: Optional[float] = None) -> None:
        """
        update_ani(self, global_time=None)

        Type: method

        Description: updates each animation of the element

        Args:
            'global_time' (float?): the time the animation should
                consider when updating, if not set time.perf_counter()
                is used

        Return type: None
        """
        if global_time is None:
            global_time = time.perf_counter()

        hide = self.is_hiding

        for i in self.current_ani.copy():
            getattr(self, i[0]).update(global_time)
            if self.is_hiding and i[0] == "_hide" and getattr(self, i[0]).running:
                hide = False

        if hide:
            self.hidden = True
            self.is_hiding = False

    def draw(self, *args, **kwargs) -> None:
        """
        Args:
            'update_ani' (bool): if true, calls self.update_ani

        For full documentation see help(pgt.Element.draw)
        """
        if "update_ani" in kwargs:
            if kwargs["update_ani"]: self.update_ani()
            del kwargs["update_ani"]
        elif len(args) == 8:
            if args[7]: self.update_ani()
            args = args[:7]
        else:
            self.update_ani()
        super().draw(*args, **kwargs)


class MouseInteractionElement(Element):
    """
    MouseInteractionElement(Element)

    Type: class

    Description: element that keeps track of the interactions it has
        with the mouse cursor

    Args:
        'transform_mouse_pos' (Callable): a function that changes the
            mouse position for the single element, can be used when
            it's part of a SurfaceElement

    Attrs:
        'hovered' (bool): if the mouse is over the rect of the element
        'clicked' (tuple[bool]): returns a tuple with the buttons
            that are clicking the element, at index 0 is the leftmost
            button, at index 1 the middlemost one ant at index 2 the
            rightmost one
        'transform_mouse_pos' (Callable): see 'transform_mouse_pos' in args

    Methods:
        get_mouse_pos()
    """
    def __init__(self,
                 transform_mouse_pos: Callable = lambda x: x,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        # These prevent that the element is considered clicked when
        # the mouse enters already clicking
        self.__prev_hovered = False
        self.__keep_clicked = False
        self.transform_mouse_pos = transform_mouse_pos

    def get_mouse_pos(self) -> Pos:
        """
        get_mouse_pos(self)

        Type: method

        Description: gets the current mouse position passed through
            'transform_mouse_pos'

        Return type: Pos
        """
        return self.transform_mouse_pos(Pos(pygame.mouse.get_pos()))

    @property
    def hovered(self):
        if self.hidden: return False

        in_area = self.collide_point(self.get_mouse_pos())

        if not any(pygame.mouse.get_pressed()) and in_area:
            self.__prev_hovered = True
            self.__keep_clicked = False
        elif not in_area:
            self.__prev_hovered = False
            self.__keep_clicked = False

        return in_area

    @property
    def clicked(self):
        if not self.hovered: return False, False, False

        if not (self.__prev_hovered or self.__keep_clicked):
            return False, False, False

        self.__prev_hovered = False
        self.__keep_clicked = True

        return pygame.mouse.get_pressed()


class MouseInteractionAniElement(MouseInteractionElement, AniElement):
    """
    MouseInteractionAniElement(MouseInteractionElement, AniElement)

    Type: class

    Description: a MouseInteractionElement that supports animations
    """
    pass
