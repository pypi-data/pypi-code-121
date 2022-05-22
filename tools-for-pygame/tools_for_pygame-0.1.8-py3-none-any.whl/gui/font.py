#!/usr/bin/env python3

from typing import List, Optional

import pygame

from tools_for_pygame.mathf import Size
from tools_for_pygame.color import GRAY
from tools_for_pygame.type_hints import _col_type
pygame.init()


class Font:
    """
    Font

    Type: class

    Description: an alternative font class, to create fonts from images

    Args:
        'image' (pygame.Surface): the characters of the font, side by
            side, see usage for more
        'chars_order' (str): the order in which the characters are
            inside the image
        'chars_widths' (list[int]): the width in pixel for each
            character (the order is determined by 'chars_order')
        'size' (int?): the initial size of the font, if not set the size
            is 1:1 scale the size of the image of the single character
        'line_size' (int?): the height of a single line, if set to None,
            it's the height of the image

    Attrs:
        'chars' (dict): a dictionary containing the character's string
            as the key and the base image and the width as a tuple
        'cache' (dict): a dict containing already created char sets
        'line_size' (int): see 'line_size' in args, here it has always a
            value, it cannot be None

    Methods:
        - get_linesize()
        - size(text)
        - render(text, antialias, color, background)

    Usage:
        To create a font, firs create an image with the characters all
        side to side and with some space between them (it's not added
        automatically).
        The first character should always be adjacent to the left border.
        The width of each character should be its actual width with some
        white space.
        Any space that is not included in the widths is used to create a
        'nochar' character, that is used when the character of the
        string given to be rendered is not defined.
        Anti aliasing means replacing all tonalities of gray with a
        mid-tone between the background color and the text color. If
        the text color is black, it will be invisible. The same applies
        to the background.
    """
    def __init__(self,
                 image: pygame.Surface,
                 chars_order: str,
                 chars_widths: List[int],
                 size: Optional[int] = None,
                 line_size: Optional[int] = None):

        if len(chars_order) != len(chars_widths):
            raise ValueError("chars_order and chars_widths must have "
                             "the same length") from None

        self.chars = {}
        self.cache = {}

        if size is not None and size != 0:
            size_mul = size / image.get_height()
            new_size = Size(image.get_size()) * size_mul
            image = pygame.transform.scale(image, new_size.int())
        else:
            size_mul = 1

        y = 0
        h = image.get_height()

        for ch, w_idx in zip(chars_order, range(len(chars_widths))):
            x = int(sum(chars_widths[:w_idx]) * size_mul)
            w = int(chars_widths[w_idx] * size_mul)
            rect = pygame.Rect(x, y, w, h)
            self.chars[ch] = (image.subsurface(rect), w)

        nochar_x = int(sum(chars_widths) * size_mul)
        nochar_w = image.get_width() - nochar_x
        self.chars["nochar"] = (image.subsurface(nochar_x, y, nochar_w, h), nochar_w)
        if line_size is not None:
            self.line_size = line_size
        else:
            self.line_size = h

    def get_linesize(self) -> int:
        """Returns 'line_size', added to conform to pygame.font.Font"""
        return self.line_size

    def size(self, text: str) -> tuple:
        """Returns the width and height of the string 'text'"""
        tot_width = sum(
            self.chars.get(i, self.chars["nochar"])[1]
            for i in str(text)
        )

        return tot_width, self.line_size

    def __get_charset(self,
                      aa: bool = False,
                      text_c: _col_type = (1, 1, 1),
                      bg_c: Optional[_col_type] = None) -> dict:
        key = (aa, text_c, bg_c)
        chars = self.cache.get(key, None)

        if chars is not None:
            return chars

        if bg_c is None: bg_c = (0, 0, 0)

        text_c = pygame.Color(text_c)
        bg_c = pygame.Color(bg_c)

        new_chars = self.chars.copy()

        for i in new_chars:
            surf = new_chars[i][0].convert_alpha()
            char_pixel_arr = pygame.PixelArray(surf.copy())
            if aa:
                for j in range(255, -1, -1):
                    if bg_c == (0, 0, 0):
                        text_c.a = j
                        char_pixel_arr.replace(GRAY(j), text_c)
                        continue
                    char_pixel_arr.replace(GRAY(j), bg_c.lerp(text_c, j / 255))
            else:
                char_pixel_arr.replace((0, 0, 0), bg_c)
                char_pixel_arr.replace((255, 255, 255), text_c)
            char_img = char_pixel_arr.surface.copy()
            char_img.unlock()
            new_chars[i] = (char_img, new_chars[i][1])
        self.cache[key] = new_chars
        return new_chars

    def render(self,
               text: str,
               antialias: bool = False,
               color: _col_type = (1, 1, 1),
               background: Optional[_col_type] = None) -> pygame.Surface:
        """
        render(test, antialias=False, color=(1, 1, 1), background=None)

        Type: method

        Description: returns a surface with the text rendered on top

        Args:
            'text' (str): the text to render
            'antialias' (bool): if anti aliasing should be applied
            'color' (pygame.color.Color): the color of the text
            'background' (pygame.color.Color): the color of the background

        Return type: pygame.Surface
        """
        image = pygame.Surface(self.size(text), flags=pygame.SRCALPHA)
        image.set_colorkey((0, 0, 0))
        text = str(text)
        current_x = 0

        charset = self.__get_charset(antialias, color, background)

        for ch in text:
            char_img = charset.get(ch, charset["nochar"])[0]
            image.blit(char_img, (current_x, 0))
            current_x += self.chars.get(ch, self.chars["nochar"])[1]

        return image
