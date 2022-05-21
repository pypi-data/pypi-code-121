# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import ahocorasick


class StrUtils:

    SAFE_STRING_BASE = r'2346789BCEFGHJKMPQRTVWXY'

    FULL_WIDTH_CHAR_MAPPING = {chr(num): chr(num - 0xfee0) for num in range(0xff01, 0xff5f)}
    FULL_WIDTH_CHAR_MAPPING[chr(0x3000)] = chr(0x20)
    FULL_WIDTH_CHAR_MAPPING[chr(0x3001)] = chr(0x2c)
    FULL_WIDTH_CHAR_MAPPING[chr(0x3002)] = chr(0x2e)
    FULL_WIDTH_CHAR_MAPPING[chr(0x2018)] = chr(0x27)
    FULL_WIDTH_CHAR_MAPPING[chr(0x2019)] = chr(0x27)
    FULL_WIDTH_CHAR_MAPPING[chr(0x201c)] = chr(0x22)
    FULL_WIDTH_CHAR_MAPPING[chr(0x201d)] = chr(0x22)

    HALF_WIDTH_CHAR_MAPPING = {val: key for key, val in FULL_WIDTH_CHAR_MAPPING.items()}

    # 转换成半角字符
    @classmethod
    def to_half_width(cls, value):
        return value.translate(
            value.maketrans(cls.FULL_WIDTH_CHAR_MAPPING)
        )

    # 转换成全角字符
    @classmethod
    def to_full_width(cls, value):
        return value.translate(
            value.maketrans(cls.HALF_WIDTH_CHAR_MAPPING)
        )


class TextFinder:

    def __init__(self):

        self._automaton = ahocorasick.Automaton()

    def init_words(self, words):

        self._automaton.clear()

        for val in words:
            self._automaton.add_word(val, val)

        self._automaton.make_automaton()

    def find_all(self, content):

        return tuple(self._automaton.iter_long(content))

    def replace_all(self, content, _chars=r'*'):

        words = {item[1] for item in self.find_all(content)}

        for key in words:
            content = content.replace(key, _chars * len(key))

        return content
