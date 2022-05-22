#!/usr/bin/env python3
from __future__ import annotations

from pygame import mouse, transform

from .button import Button
from .gui_element import GUIElement
from tools_for_pygame.constants import AUTOMATIC
from tools_for_pygame.mathf import Pos, Size
from tools_for_pygame.element import Element, MouseInteractionElement
from tools_for_pygame.type_hints import _col_type, _pos
from tools_for_pygame.utils import filled_surface


class GUILayout(GUIElement, MouseInteractionElement):
    """
    GUILayout(GUIElement, MouseInteractionElement)

    Type: class

    Description: a container for GUIElement (therefore also other
        GUILayout elements) that allows you to show the hits of the
        buttons, position element automatically and hide or show them
        all at once

    Args:
        'elements' (dict[str: Element]): a dictionary that contains the
            element and its name, the name is later set as an attribute
            allowing you to access it more easily
        'bg_color' (pygame.color.Color): the background color of the
            layout
        'adapt_height' (bool): whether the layout should resize
            according to the bottom-most element with and automatic
            position mode

    Attrs:
        'bg_color' (pygame.color.Color): see 'bg_color' in args
        'elements' (list): a list containing the elements
        'adapt_height' (bool): see 'adapt_height' in args

    Methods:
        - auto_run()
        - set_layout(new_layout)
        - collide_point(point)
    """
    def __init__(self,
                 elements: dict[str: Element],
                 bg_color: _col_type = None,
                 adapt_height: bool = False,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bg_color = bg_color
        self.adapt_height = adapt_height

        if self.bg_color is not None:
            self.image = filled_surface(self.size, self.bg_color)
        self._curr_button_hint = None

        self.elements = []

        if not isinstance(elements, dict):
            raise TypeError("'elements' must be 'dict', " \
                            f"not {elements.__class__.__name__}")

        for name, element in elements.items():
            if name in self.__dict__:
                raise NameError(f"name '{name}' already exists in the layout")
            setattr(self, name, element)
            self.elements.append(element)
            if not isinstance(element, GUIElement):
                element.anchor(self)
                continue

            element.set_layout(self)

        self.__prev_button = None
        self._calculate_autopos_offsets()

    def _calculate_autopos_offsets(self) -> None:
        max_h = 0
        curr_y = 0
        curr_x = 0

        for e in self.elements:
            if not isinstance(e, GUIElement) or e.position_mode != AUTOMATIC:
                continue

            offset = e.padding_ul + Pos(0, curr_y)
            if curr_x + e.w <= self.w or e.w > self.w and curr_x == 0:
                offset.x += curr_x
                curr_x += e.w
                if e.h > max_h:
                    max_h = e.h
            else:
                offset.y += max_h
                curr_y += max_h
                max_h = e.h
                curr_x = e.w
            e.offset = offset
            e._pos_point = "ul"

        if not self.adapt_height: return

        self.rect.h = max_h + curr_y
        if self.bg_color is None: return
        self.image = filled_surface(self.size, self.bg_color)

    @property
    def size(self):
        size = Size(self.rect.size)
        size += self.padding_ul
        size += self.padding_dr
        return size

    @size.setter
    def size(self, value):
        value = round(Size(value))
        value -= self.padding_ul
        value -= self.padding_dr
        self.rect.size = value
        if self.bg_color is None: return
        self.image = filled_surface(self.size, self.bg_color)
        self._calculate_autopos_offsets()

    def rotate(self, *args, **kwargs) -> None:
        raise NotImplemented("Rotating GUILayout is not supported")

    def scale(self, *args, **kwargs) -> None:
        raise NotImplemented("Scaling GUILayout is not supported")

    def change_image(self, surface) -> None:
        self.image = transform.scale(surface, self.true_size)

    def collide_point(self, point: _pos) -> bool:
        """
        Collides each element with a point, if there is a bg_color
        the collision is checked also onto itself
        """
        for i in self.elements:
            if i.collide_point(point):
                return True
        if self.bg_color is not None:
            return super().collide_point(point)
        return False

    def auto_run(self) -> None:
        """
        If the element hovered is a button or another layout calls
        'auto_run' on that element
        """
        if self.__prev_button is not None:
            res = self.__prev_button.auto_run()
        else:
            res = False

        for i in reversed(self.elements):
            if i.collide_point(self.get_mouse_pos()):
                if i is self.__prev_button:
                    return res

                if isinstance(i, Button):
                    self.__prev_button = i
                    return i.auto_run()
                return False
        return res

    def show(self) -> None:
        for i in self.elements:
            i.show()
        super().show()

    def hide(self) -> None:
        for i in self.elements:
            i.hide()
        super().hide()

    def set_layout(self, new_layout: Layout) -> None:
        """
        Anchors itself to the new layout and sets the 'layout' attribute
        of its elements to the new layout without changing their anchor
        """
        for i in self.elements:
            if isinstance(i, GUIElement):
                i.layout = new_layout
        super().set_layout(new_layout)

    def draw(self, *args, **kwargs) -> None:
        super().draw(*args, **kwargs)

        for i in self.elements:
            i.draw(*args, **kwargs)

        if self.hidden or self.auto_run(): return

        if self._curr_button_hint:
            mouse_pos = Pos(mouse.get_pos())
            if mouse_pos.y - self._curr_button_hint[1].size.h < 0:
                attr = "u"
            else:
                attr = "d"

            if self._curr_button_hint[1].size.w + mouse_pos.x > self.size.w:
                attr += "r"
            else:
                attr += "l"

            setattr(self._curr_button_hint[1], attr, mouse_pos)

            self._curr_button_hint[1].draw(*args, **kwargs)
            self._curr_button_hint[2].draw(*args, **kwargs)
