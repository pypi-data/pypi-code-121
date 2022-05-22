#!/usr/bin/env python3
from typing import Optional

from pygame import display

from tools_for_pygame.constants import ABSOLUTE
from tools_for_pygame.element import Element, AniElement
from tools_for_pygame.mathf import Pos, Size
from tools_for_pygame.type_hints import _size


class GUIElement(Element):
    """
    GUIElement(Element)

    Type: class

    Description: this class adds some functionality to the element that
        is related to GUI

    Args:
        'layout' (GUILayout?): the layout the element resembles to, see
            help(pgt.gui.GUILayout) for more info
        'position_mode' (int): this can be either pgt.ABSOLUTE (default)
            or pgt.AUTOMATIC; the latter positions the elements
            automatically only if the layout is set and the pos_point is
            pgt.UL
        'rel_size' (Size): percentage of the element's size relative to
            the layout or to the window if the layout is not set
            can be anything from 0 to 1 and None, if deactivated. The
            minimum size is set with the 'size' argument
        'padding_top' (int): the space from the top that the element
            should keep when position_mode is automatic
        'padding_bottom' (int): space from the bottom
        'padding_left' (int): space from the left
        'padding_right' (int): space from the right
        'app' (Any): an attribute that should be used to link the
            element with the application you're creating

    Attrs:
        'rel_size' (Size): see 'rel_size' in args
        'base_size' (Size): the minimum size of the element
        'layout' (GUILayout?): the layout the element resembles to
        'position_mode' (int): see 'position_mode' in args
        'padding_ul' (Pos): padding_top and padding_left
        'padding_dr' (Pos): padding_bottom and padding_right
        'true_size' (Size): the size without the padding
        'size' (Size): instead of returning only the size of the element,
            size here adds the padding, the setter sets the size not
            considering the padding

    Methods:
        set_layout(new_layout)
    """
    def __init__(self,
                 layout: Optional["GUILayout"] = None,
                 position_mode: int = ABSOLUTE,
                 rel_size: _size = Size(None),
                 padding_top: int = 0,
                 padding_bottom: int = 0,
                 padding_left: int = 0,
                 padding_right: int = 0,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rel_size = Size(rel_size)
        self.base_size = self._size
        self.layout = layout
        self.position_mode = position_mode
        self.padding_ul = round(Pos(padding_left,  padding_top))
        self.padding_dr = round(Pos(padding_right, padding_bottom))

    @property
    def size(self):
        size = Size(self.rect.size)
        size += self.padding_ul
        size += self.padding_dr
        return size

    @size.setter
    def size(self, value):
        self.rect.size = round(Size(value))

    @property
    def true_size(self):
        return Size(self.rect.size)

    def set_layout(self, new_layout: "GUILayout") -> None:
        """
        set_layout(self, new_layout)

        Type: method

        Description: changes the layout of the element and anchors the
            GUIElement to it if the element is not already anchored to
            something

        Args:
            'new_layout' (GUILayout): the new element's layout

        Return type: None
        """
        self.layout = new_layout
        if not self.is_anchored:
            self.anchor(new_layout, self._a_point)

    def draw(self, *args, **kwargs) -> None:
        if self.layout:
            max_size = self.layout.size
        else:
            max_size = Size(display.get_window_size())

        if self.rel_size.w is not None:
            self.w = max_size.w * self.rel_size.w
            if self.w < self._size.w:
                self.w = self._size.w
        if self.rel_size.h is not None:
            self.h = max_size.h * self.rel_size.h
            if self.h < self._size.h:
                self.h = self._size.h
        super().draw(*args, **kwargs)


class GUIAniElement(GUIElement, AniElement):
    pass
