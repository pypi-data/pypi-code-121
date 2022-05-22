from abc import ABC

from pygame import display

from .button import Button
from .draggable import Draggable
from .surface_element import SurfaceElement
from tools_for_pygame.constants import CC, BUTTON_CLICK, BUTTON_HOVER, BUTTON_NORMAL
from tools_for_pygame.mathf import Pos, Size, safe_div
from tools_for_pygame.utils import transform_func

display.init()


class SliderCursor(Button, Draggable):
    """
    SliderCursor(Button, Draggable)

    Type: class

    Description: this class should be used to create the cursor of the
        slider and merges pgt.gui.Button and pgt.gui.Draggable
        functionality
    """
    pass


class _SliderBase(SurfaceElement, ABC):
    def __init__(self,
                 ruler: Button,
                 cursor: SliderCursor,
                 min_val: float = 0,
                 max_val: float = 1,
                 *args, **kwargs):
        kwargs["elements"] = [ruler, cursor]
        super().__init__(*args, **kwargs)
        self.ruler = ruler
        self.cursor = cursor

        self.min_val = min_val
        self.max_val = max_val

        self.ruler.func = None
        self.ruler.fargs = []
        self.ruler.fkwargs = {}
        self.ruler.transform_mouse_pos = transform_func(self)

        self.cursor.func = None
        self.cursor.fargs = []
        self.cursor.fkwargs = {}
        self.cursor.transform_mouse_pos = transform_func(self)
        self.cursor._pos_point = CC

        self._rect_size = self.size

    @property
    def value(self):
        return None

    def draw(self, *args, **kwargs) -> None:
        if self.hidden: return
        if self.ruler.button_clicked \
           and not self.cursor.dragging \
           and not self.cursor.hovered:
            self.cursor.dragging = True
            self.cursor.drag_point = Pos(0, 0)

        if self.cursor.dragging:
            self.cursor.force_state = BUTTON_CLICK
        elif self.ruler.hovered or self.cursor.hovered:
            self.cursor.force_state = BUTTON_HOVER
        else:
            self.cursor.force_state = BUTTON_NORMAL

        super().draw(*args, **kwargs)


class HSlider(_SliderBase):
    """
    HSlider(_SliderBase)

    Type: class

    Description: horizontal slider that returns a value between 0 and 1

    Args:
        'ruler' (Button): the ruler where the cursor slides
        'cursor' (SliderCursor): the cursor that can be dragged around
        'min_val' (float): minimum value of the slider
        'max_val' (float): maximum value of the slider

    Attrs:
        'ruler' (Button): see 'ruler' in args
        'cursor' (SliderCursor): see 'cursor' in args
        'max_x' (int): the maximum x position of the cursor
        'value' (float): the value that the slider is set to, if changed
            the position of the slider is changed accordingly
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        new_size = Size(self.ruler.w, max(self.ruler.h, self.cursor.h))
        self.size = new_size
        self._size = new_size
        self.base_size = Size(self.ruler.base_size.w, 0)
        self.ruler.x = 0

        if self.ruler.h <= self.cursor.h:
            self.cursor.b_top = 0
            self.cursor.b_bottom = self.true_size.h
            self.ruler.offset = (0, (self.cursor.h - self.ruler.h) / 2)
        else:
            self.cursor.b_top = (self.true_size.h - self.cursor.h) / 2
            self.cursor.b_bottom = (self.true_size.h + self.cursor.h) / 2

        self.cursor.b_left = 0
        self.cursor.b_right = self.ruler.w

        self.max_x = self.ruler.w - self.cursor.w

        if self.max_x < 0:
            raise ValueError("the ruler's width must be greater than the cursor's")

    @property
    def value(self):
        return self.min_val + (safe_div(self.cursor.l, self.max_x)) * (self.max_val - self.min_val)

    @value.setter
    def value(self, new_value):
        if self.min_val == self.max_val:
            return
        self.cursor.l = (new_value - self.min_val) / (self.max_val - self.min_val) * self.max_x

    def draw(self, *args, **kwargs) -> None:
        prev_val = self.value

        if self.layout:
            max_size = self.layout.size
        else:
            max_size = Size(display.get_window_size())

        if self.rel_size.w is not None:
            self._size.w = max_size.w * self.rel_size.w
            if self._size.w < self.base_size.w:
                self._size.w = self.base_size.w

        self.ruler.w = self._size.w
        self.max_x = self.ruler.w - self.cursor.w
        self.cursor.b_right = self.ruler.w
        if not self.cursor.dragging:
            self.value = prev_val
        self._size = Size(self.ruler.w, max(self.ruler.h, self.cursor.h))
        super().draw(*args, **kwargs)


class VSlider(_SliderBase):
    """
    HSlider(_SliderBase)

    Type: class

    Description: vertical slider that returns a value between 0 and 1

    Args:
        'ruler' (Button): the ruler where the cursor slides
        'cursor' (SliderCursor): the cursor that can be dragged around

    Attrs:
        'ruler' (Button): see 'ruler' in args
        'cursor' (SliderCursor): see 'cursor' in args
        'max_y' (int): the maximum y position of the cursor
        'value' (float): the value that the slider is set to, if changed
            the position of the slider is changed accordingly
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        new_size = Size(max(self.ruler.w, self.cursor.w), self.ruler.h)
        self.size = new_size
        self._size = new_size
        self.base_size = Size(0, self.ruler.base_size.h)
        self.ruler.y = 0

        if self.ruler.w <= self.cursor.w:
            self.cursor.b_left = 0
            self.cursor.b_right = self.true_size.w
            self.ruler.offset = ((self.cursor.w - self.ruler.w) / 2, 0)
        else:
            self.cursor.b_left = (self.true_size.w - self.cursor.w) / 2
            self.cursor.b_right = (self.true_size.w + self.cursor.w) / 2

        self.cursor.b_top = 0
        self.cursor.b_bottom = self.ruler.h

        self.max_y = self.ruler.h - self.cursor.h
        if self.max_y < 0:
            raise ValueError("the ruler's height must be greater than the cursor's")

    @property
    def value(self):
        return self.min_val + (safe_div(self.cursor.u, self.max_y)) * (self.max_val - self.min_val)

    @value.setter
    def value(self, new_value):
        if self.min_val == self.max_val:
            return
        self.cursor.u = (new_value - self.min_val) / (self.max_val - self.min_val) * self.max_y

    def draw(self, *args, **kwargs) -> None:
        prev_val = self.value

        if self.layout:
            max_size = self.layout.size
        else:
            max_size = Size(display.get_window_size())

        if self.rel_size.w is not None:
            self._size.h = max_size.h * self.rel_size.h
            if self._size.h < self.base_size.h:
                self._size.h = self.base_size.h

        self.ruler.h = self._size.h
        self.max_y = self.ruler.h - self.cursor.h
        self.cursor.b_bottom = self.ruler.h
        if not self.cursor.dragging:
            self.value = prev_val
        self._size = Size(max(self.ruler.w, self.cursor.w), self.ruler.h)
        super().draw(*args, **kwargs)
