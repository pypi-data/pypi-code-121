#!/usr/bin/env python3

from typing import Union, Optional, Any

import pygame

from .font import Font
from .gui_element import GUIElement
from tools_for_pygame.constants import LEFT, RIGHT, CENTER, NO_AA, BOLD, ITALIC, UNDERLINE
from tools_for_pygame.element import AniElement
from tools_for_pygame.mathf import Pos
from tools_for_pygame.type_hints import _col_type


class Label(GUIElement):
    """
    Label(GUIElement)

    Type: class

    Description: flexible text label that supports both
        pygame.font.Font and pgt.gui.Font, new lines and alignments

    Args:
        'text' (str): the text of the label
        'text_size' (int): the size of the text, applied only if the
            font is given by the name
        'color' (pygame.color.Color): the color of the text
        'bg_color' (pygame.color.Color): the color of the background of
            the text
        'font' (pgt.gui.Font, pygame.font.Font, str): if given a string
            pygame.font.SysFont is called and 'text_size' is applied
        'style' (int): any combination of pgt.NO_AA (no anti aliasing),
            pgt.BOLD, pgt.UNDERLINE and pgt.ITALIC. Only the first one
            works with pgt.font.Font
        'alignment' (int): alignment of the text, can be pgt.LEFT,
            pgt.RIGHT and pgt.CENTER
        'line_height' (int): the height of a single line of text, if not
            set get_linesize() is used
        'adapt_to_width' (bool): if the text should be adapted to the
            width of the label. If a line is too long it's broken up
            into words, if the first word is too long, it's broken up
            into the single characters
        'exceed_size' (bool): if the image with the text should exceed
            the size of the label
        'auto_size' (bool): if the size of the label should be changed
            to match the size of the text

    Attrs:
        'font' (pygame.font.Font, pgt.gui.Font): the label's font
        'pygame_font' (bool): whether the label is using
            pygame.font.Font or not
        'adapt_width' (bool): see 'adapt_width' in args
        'exceed_size' (bool): see 'exceed_size' in args
        'alignment' (int): see 'alignment' in args
        'auto_size' (bool): see 'auto_size' in args
        'color' (pygame.color.Color): see 'color' in args
        'bg_color' (pygame.color.Color): see 'bg_color' in args
        'bold' (bool): whether the text is bold or not
        'italic' (bool): whether the text is italic or not
        'underlined' (bool): whether the text is underlined or not
        'text' (str): the text of the label
    """
    def __init__(self,
                 text: str = "",
                 text_size: int = 20,
                 color: _col_type = None,
                 bg_color: _col_type = None,
                 font: Union[Font, pygame.font.Font, str] = None,
                 style: int = 0,
                 alignment: int = LEFT,
                 line_height: Optional[int] = None,
                 adapt_to_width: bool = False,
                 exceed_size: bool = True,
                 auto_size: bool = False,
                 *args, **kwargs):

        super().__init__(*args, **kwargs)

        self._aa = not (style & NO_AA)

        if isinstance(font, pygame.font.Font):
            self.font = font
            self.pygame_font = True
        elif isinstance(font, Font):
            self.font = font
            self.pygame_font = False
        else:
            try:
                self.font = pygame.font.Font(font, text_size)
            except FileNotFoundError:
                self.font = pygame.font.SysFont(font, text_size)
            self.pygame_font = True

        if BOLD & style and self.pygame_font:
            self.font.set_bold(True)
        if ITALIC & style and self.pygame_font:
            self.font.set_italic(True)
        if UNDERLINE & style and self.pygame_font:
            self.font.set_underline(True)

        self.__text = text
        self.adapt_width = adapt_to_width
        self.exceed_size = exceed_size
        self.alignment = alignment
        self.auto_size = auto_size

        if color is None: color = (1, 1, 1)
        self.color = color
        self.bg_color = bg_color

        if not (0 <= self.alignment <= CENTER):
            self.alignment = LEFT

        if line_height is None:
            self._line_h = self.font.get_linesize()
        else:
            self._line_h = line_height

        self.text = text

    @property
    def bold(self):
        if not self.pygame_font: return False
        return self.font.get_bold()
    @bold.setter
    def bold(self, value):
        if not self.pygame_font: return
        self.font.set_bold(value)

    @property
    def italic(self):
        if not self.pygame_font: return False
        return self.font.get_italic()
    @italic.setter
    def italic(self, value):
        if not self.pygame_font: return
        self.font.set_italic(value)

    @property
    def underline(self):
        if not self.pygame_font: return False
        return self.font.get_underline()
    @underline.setter
    def underline(self, value):
        if not self.pygame_font: return
        self.font.set_underline(value)

    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, text: Any):
        self.__text = str(text)

        lines = self.__text.split("\n")
        if lines[-1] == "": del lines[-1]

        if self.adapt_width:
            new_lines = []
            for line in lines:
                words = line.split(" ")
                current_text = words[0]
                prev_text = words[0]

                while self.__check_size(prev_text) and len(prev_text) > 1:
                    new_line = prev_text[0]
                    prev_text = prev_text[1:]
                    while prev_text and not self.__check_size(new_line + prev_text[0]):
                        new_line += prev_text[0]
                        prev_text = prev_text[1:]
                    new_lines.append(new_line)

                for word in words[1:]:
                    current_text += " " + word
                    if self.__check_size(current_text):
                        new_lines.append(prev_text)
                        while self.__check_size(word) and len(word) > 1:
                            new_line = word[0]
                            word = word[1:]
                            while word and not self.__check_size(new_line + word[0]):
                                new_line += word[0]
                                word = word[1:]
                            new_lines.append(new_line)
                        current_text = word
                        prev_text = word
                        continue

                    prev_text = current_text

                if self.font.size(current_text)[0] > self.size.w:
                    new_lines.append(prev_text)
                else:
                    new_lines.append(current_text)
            lines = new_lines

        if not lines: lines = [""]

        if self.exceed_size:
            width = max([self.font.size(i)[0] for i in lines])
            height = self._line_h * len(lines)
            new_image = pygame.Surface((width, height), flags=pygame.SRCALPHA)
        else:
            new_image = pygame.Surface(self.size, flags=pygame.SRCALPHA)
        new_image.set_colorkey((0, 0, 0))

        for l_no, i in enumerate(lines):
            line = self.font.render(i, self._aa, self.color, self.bg_color)

            y = self._line_h * l_no
            if self.alignment == LEFT:
                new_image.blit(line, (0, y))
            elif self.alignment == RIGHT:
                x = new_image.get_width() - self.font.size(i)[0]
                new_image.blit(line, (x, y))
            else:
                x = (new_image.get_width() - self.font.size(i)[0]) // 2
                new_image.blit(line, (x, y))

        if self.alignment == LEFT or self.auto_size:
            self.img_offset = Pos(0)
        elif self.alignment == RIGHT:
            self.img_offset = Pos(self.size.w - new_image.get_width(), 0)
        else:
            self.img_offset = Pos((self.size.w - new_image.get_width()) / 2, 0)

        self.change_image(new_image)

    def __check_size(self, text) -> bool:
        return self.font.size(text)[0] > self.size.w

    def rotate(self, *args, **kwargs) -> None:
        if self.auto_size:
            super().rotate(*args, **kwargs)
        else:
            prev_size = self.size.copy()
            super().rotate(*args, **kwargs)
            self.size = prev_size


class AniLabel(Label, AniElement):
    pass
