#!/usr/bin/env python3

from typing import Optional
import pygame.mouse
from tools_for_pygame.element import MouseInteractionAniElement
from tools_for_pygame.mathf import Pos


class Draggable(MouseInteractionAniElement):
    """
    Draggable(MouseInteractionAniElement)

    Type: class

    Description: an element that can be dragged around

    Args:
        'button' (int): which mouse button should activate the button
            1 - left, 2 - middle, 3 - right
        'locked' (bool): if the element can be dragged or not
        'boundary_top' (int?): the top boundary that the element can
            never surpass
        'boundary_left' (int?): the left boundary
        'boundary_right' (int?): the right boundary
        'boundary_bottom' (int?): the bottom boundary

    Attrs:
        'button' (int): see 'button' in args
        'dragging' (bool): whether the element is being dragged or not
        'drag_point' (Pos): the click point of the mouse relative to
            Draggable.pos
        'locked' (bool): see 'locked' in args
        'b_top' (int?): see 'boundary_top' in args
        'b_right' (int?): see 'boundary_right' in args
        'b_left' (int?): see 'boundary_left' in args
        'b_bottom' (int?): see 'boundary_bottom' in args
        'button_clicked' (bool): whether the element is being clicked by
            the button assigned with 'button'

    Methods:
        - update()
        - fix_pos()
    """
    def __init__(self,
                 button: int = 0,
                 locked: bool = False,
                 boundary_top: Optional[int] = None,
                 boundary_left: Optional[int] = None,
                 boundary_right: Optional[int] = None,
                 boundary_bottom: Optional[int] = None,
                 *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.button = button
        self.dragging = False
        self.drag_point = Pos(0, 0)
        self.locked = locked
        self.b_top = boundary_top
        self.b_right = boundary_right
        self.b_left = boundary_left
        self.b_bottom = boundary_bottom

    @property
    def button_clicked(self):
        return self.clicked[self.button]

    def fix_pos(self) -> None:
        """Repositions the draggable inside the boundaries"""
        if self.b_top is not None and self.u < self.b_top:
            self.u = self.b_top
        if self.b_bottom is not None and self.d > self.b_bottom:
            self.d = self.b_bottom
        if self.b_left is not None and self.l < self.b_left:
            self.l = self.b_left
        if self.b_right is not None and self.r > self.b_right:
            self.r = self.b_right

    def update(self) -> None:
        """Updates the draggable's position when it's dragged"""
        if not self.dragging and self.button_clicked and not self.locked:
            self.dragging = True
            self.drag_point = self.get_mouse_pos() - self.pos
        elif not pygame.mouse.get_pressed(3)[self.button]:
            self.dragging = False

        if self.dragging:
            self.pos = self.get_mouse_pos() - self.drag_point

    def draw(self, *args, **kwargs) -> None:
        self.update()
        self.fix_pos()

        super().draw(*args, **kwargs)
