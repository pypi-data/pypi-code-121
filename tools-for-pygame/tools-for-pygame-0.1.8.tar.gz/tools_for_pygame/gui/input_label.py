#!/usr/bin/env python3
from string import punctuation, whitespace
import time
from typing import Optional

import pygame

from .button import Button
from .label import Label

from tools_for_pygame.constants import RIGHT, LEFT, BLACK, BUTTON_CLICK
from tools_for_pygame.draw import aa_rect
from tools_for_pygame.exceptions import NoLabelError
from tools_for_pygame.mathf import clamp
from tools_for_pygame.type_hints import _col_type


class InputLabel(Button):
    """
    InputLabel(Button)

    Type: class

    Description: a label that supports keyboard input, currently you can
        move the cursor but not select, cut, copy or paste text

    Args:
        'focused' (bool): if the input label should be focused on
            initialization
        'auto_focus' (bool): if the input label should be focused when
            there is any key press
        'allowed_chars' (str): allowed characters in the input label
        'caret_color' (list, tuple): the color of the caret, supports
            the alpha channel
        'caret_rect' (pygame.Rect): the rect of the caret, by default is
            2px wide and has the same height as the label of the button
        'caret_corner_radius' (int): corner radius of the caret
        'right_aligned' (bool): if the text should be written from the
            right to the left, such as Hebrew or Arabic scripts
        'char_subs' (dict): a string that is added to the text instead
            of the unicode of the key (Ex. {"\\t": "    "} when pressing
            [TAB])

    Attrs:
        'focused' (bool): see 'focused' in args
        'auto_focus' (bool): see 'auto_focus' in args
        'allowed_chars' (bool): see 'allowed_chars' in args
        'caret_img' (pygame.Surface): the surface blit at the
            position of the caret
        'right_aligned' (bool): see 'right_aligned' in args
        'text' (str): the current text of the label, do NOT use
            'InputLabel.label.text' to take the contents because they
            may be incomplete
        'char_subs' (dict): see 'char_subs' in args

    Changed attrs:
        'func' is now called when the label loses focus

    Changed methods:
        'handle_event':
            - now calls 'unfocus' when a MOUSEBUTTONUP event occurs, the
              event is not caught and the function returns False.
            - now catches any KEYDOWN events when the input label is
              focused, returning True

    Methods:
        - focus()
        - unfocus()
        - set_text(text)
        - _handle_keypress(key, uni)
        - _update_text()
    """
    def __init__(self,
                 focused: bool = False,
                 auto_focus: bool = False,
                 allowed_chars: str = "",
                 caret_color: _col_type = BLACK,
                 caret_rect: Optional[pygame.Rect] = None,
                 caret_corner_radius: int = 0,
                 right_aligned: bool = False,
                 char_subs: dict = None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not isinstance(self.label, Label):
            raise NoLabelError("'text_label' argument of 'InputLabel'" \
                               f" must be of type 'Label', not '{self.label.__class__.__name__}'")

        self.label.exceed_size = False

        self.right_aligned = right_aligned

        self.text = self.label.text
        self.__focused = False

        self.__caret = 0
        self.__t_offset = 0
        self.__blink_timer = 0

        self.auto_focus = auto_focus
        self.allowed_chars = allowed_chars

        if char_subs is None:
            char_subs = {}
        self.char_subs = char_subs

        if not isinstance(caret_rect, pygame.Rect):
            caret_rect = pygame.Rect(0, 0, 2, self.label.h)

        self.caret_img = aa_rect(
            None,
            caret_rect,
            caret_color,
            caret_corner_radius
        )

        self._update_text()
        if focused: self.focus()

    @property
    def focused(self):
        return self.__focused

    @focused.setter
    def focused(self, val):
        if val:
            self.focus()
        elif self.__focused:
            self.unfocus()

    def run(self) -> None:
        self.focus()

    def focus(self) -> None:
        """Focuses the input label, sets key repeat to 600, 40"""
        if self.__focused: return
        self.force_state = BUTTON_CLICK
        self.__caret = 0 if self.right_aligned else len(self.text)
        self.__blink_timer = time.perf_counter()
        self.__focused = True
        pygame.key.set_repeat(600, 40)

    def unfocus(self) -> None:
        """Unfocuses the input label, removes key repeat"""
        self.force_state = None
        if self.__focused and self.func is not None:
            if self.func_as_method:
                self.func(self, *self.fargs, **self.fkwargs)
            else:
                self.func(*self.fargs, **self.fkwargs)
        self.__focused = False
        pygame.key.set_repeat(0)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and \
           not self.hovered and self.__focused:
            self.unfocus()
            return False
        elif event.type == pygame.KEYDOWN and \
             (self.__focused or self.auto_focus):
            if self.auto_focus and not self.__focused:
                self.focus()
            self._handle_keypress(event.key, event.unicode)
            return True
        else:
            return False

    def set_text(self, text: str) -> None:
        """
        set_text(self, text: str)

        Type: method

        Description: changes the text of the input label, changing only
            the 'text' attribute will not work unless '_update_text()'
            is called

        Args:
            'text' (str): the new text of the input label

        Return type: None
        """
        self.text = text
        self._update_text()

    def __text_w(self, text: str) -> int:
        return self.label.font.size(text)[0]

    def __find_word_break(self, reverse: bool) -> int:
        idx = self.__caret

        n = -1 if reverse else 0

        # Skip whitespace before the word
        while 0 <= idx + n < len(self.text) and \
              (self.text[idx + n] in punctuation or \
              self.text[idx + n] in whitespace):
            idx += -1 if reverse else 1

        while 0 <= idx + n < len(self.text) and \
              self.text[idx + n] not in punctuation and \
              self.text[idx + n] not in whitespace:

            idx += -1 if reverse else 1

        return abs(self.__caret - idx) + 1

    def _handle_keypress(self, key: int, uni: str) -> None:
        """
        _handle_keypress(self, key: int, uni: str)

        Type: method

        Description: when a key is pressed this function moves the caret,
            adds a character or deletes one or more characters

        Args:
            'key' (int): a pygame constant rapresenting the key pressed
            'uni' (str): the unicode (character) that the key writes

        Return type: None
        """
        ctrl_pressed = pygame.key.get_mods() & pygame.KMOD_CTRL
        if (key == pygame.K_BACKSPACE and not self.right_aligned) or \
           (key == pygame.K_DELETE and self.right_aligned):
            if ctrl_pressed: char_q = self.__find_word_break(True)
            else:            char_q = 1
            self.text = self.text[:max(0, self.__caret - char_q)] +\
                        self.text[self.__caret:]
            self.__caret -= char_q

        elif (key == pygame.K_DELETE and not self.right_aligned) or \
             (key == pygame.K_BACKSPACE and self.right_aligned):
            if ctrl_pressed: char_q = self.__find_word_break(False)
            else:            char_q = 1
            self.text = self.text[:self.__caret] +\
                        self.text[self.__caret + char_q:]

        elif key == pygame.K_LEFT:
            if ctrl_pressed: char_q = self.__find_word_break(True)
            else:            char_q = 1
            self.__caret -= char_q

        elif key == pygame.K_RIGHT:
            if ctrl_pressed: char_q = self.__find_word_break(False)
            else:            char_q = 1
            self.__caret += char_q

        elif (key == pygame.K_END and not self.right_aligned) or \
             (key == pygame.K_HOME and self.right_aligned):
            self.__caret = len(self.text)

        elif (key == pygame.K_HOME and not self.right_aligned) or \
             (key == pygame.K_END and self.right_aligned):
            self.__caret = 0

        elif key in (pygame.K_RETURN, pygame.K_ESCAPE):
            self.unfocus()
            return

        elif uni != "" and not ctrl_pressed:
            if self.allowed_chars and uni not in self.allowed_chars:
                return

            uni = self.char_subs.get(uni, uni)

            self.text = self.text[:self.__caret] + uni + self.text[self.__caret:]
            if self.right_aligned:
                self.__t_offset += len(uni)
            else:
                self.__caret += len(uni)

        self.__blink_timer = time.perf_counter()
        self._update_text()

    def _update_text(self) -> None:
        """Updates the text inside the label"""
        self.__caret = clamp(self.__caret, 0, len(self.text))

        # change the alignment of the text (left or right)
        if self.__t_offset < self.__caret:
            txt_w = self.__text_w(self.text[self.__t_offset:self.__caret])
            if txt_w > self.label.w:
                self.__t_offset = self.__caret
                self.label.alignment = RIGHT

        elif self.__t_offset > self.__caret:
            txt_w = self.__text_w(self.text[self.__caret:self.__t_offset])
            if txt_w > self.label.w:
                self.__t_offset = self.__caret
                self.label.alignment = LEFT

        # check for special cases
        if self.right_aligned:
            if self.label.alignment == RIGHT and \
               self.__text_w(self.text[:self.__t_offset]) < self.label.w:
               self.label.alignment = LEFT
               self.__t_offset = 0

            if self.label.alignment == LEFT and \
               self.__text_w(self.text) < self.label.w:
               self.label.alignment = RIGHT
               self.__t_offset = len(self.text)
        else:
            if self.label.alignment == LEFT and \
               self.__text_w(self.text[self.__t_offset:]) < self.label.w:
               self.label.alignment = RIGHT
               self.__t_offset = len(self.text)

            if self.label.alignment == RIGHT and \
               self.__text_w(self.text) < self.label.w:
               self.label.alignment = LEFT
               self.__t_offset = 0

        # set the text of the label
        if self.label.alignment == RIGHT:
            if self.__t_offset < self.__caret:
                self.__t_offset = self.__caret
            self.label.text = self.text[:self.__t_offset]

        elif self.label.alignment == LEFT:
            if self.__t_offset > self.__caret:
                self.__t_offset = self.__caret
            self.label.text = self.text[self.__t_offset:]

        else:
            self.label.text = self.text

    def draw(self, surface, *args, **kwargs) -> None:
        super().draw(surface, *args, **kwargs)

        if not self.__focused:
            return

        if (time.perf_counter() - self.__blink_timer) % 1 > 0.5:
            return

        if self.label.alignment == RIGHT:
            caret_x = self.label.r - self.__text_w(self.text[self.__caret:self.__t_offset])
        else:
            caret_x = self.label.l + self.__text_w(self.text[self.__t_offset:self.__caret])

        caret_x -= 1

        surface.blit(self.caret_img, (caret_x, self.label.u))
