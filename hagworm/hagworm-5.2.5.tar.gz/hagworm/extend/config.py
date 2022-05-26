# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import dataclasses

from configparser import RawConfigParser

from .base import Utils


class HostType(str):

    @classmethod
    def decode(cls, val):

        if not val:
            return None

        host, port = val.split(r':', 2)
        return host.strip(), int(port.strip())


class JsonType(str):

    @classmethod
    def decode(cls, val):

        if not val:
            return None

        return Utils.json_decode(val)


class StrListType(str):

    @classmethod
    def decode(cls, val):
        return Utils.split_str(val)


class IntListType(str):

    @classmethod
    def decode(cls, val):
        return Utils.split_int(val)


class FloatListType(str):

    @classmethod
    def decode(cls, val):
        return Utils.split_float(val)


class Field:

    __slots__ = [r'section']

    def __init__(self, section):

        self.section = section


class _ConfigureMetaclass(type):
    """配置类元类，增加dataclass修饰
    """

    def __new__(mcs, name, bases, attrs):
        return dataclasses.dataclass(init=False, frozen=True)(
            type.__new__(mcs, name, bases, attrs)
        )


class Configure(metaclass=_ConfigureMetaclass):
    """配置类
    """

    __slots__ = [r'_parser']

    def __init__(self):

        super().__init__()

        self._set_attr(r'_parser', RawConfigParser())

    def _set_attr(self, name, value):
        super().__setattr__(name, value)

    def _init_options(self):

        for _name, _field in self.__dataclass_fields__.items():

            _type = _field.type
            _section = _field.default.section

            if _type is str:
                self._set_attr(_name, self._parser.get(_section, _name))
            elif _type is int:
                self._set_attr(_name, self._parser.getint(_section, _name))
            elif _type is float:
                self._set_attr(_name, self._parser.getfloat(_section, _name))
            elif _type is bool:
                self._set_attr(_name, self._parser.getboolean(_section, _name))
            else:
                self._set_attr(_name, _type.decode(self._parser.get(_section, _name)))

    def get_option(self, section, option):

        return self._parser.get(section, option)

    def get_options(self, section):

        parser = self._parser

        options = {}

        for option in parser.options(section):
            options[option] = parser.get(section, option)

        return options

    def set_options(self, section, **options):

        if not self._parser.has_section(section):
            self._parser.add_section(section)

        for option, value in options.items():
            self._parser.set(section, option, value)

        self._init_options()

    def read(self, files):

        self._parser.clear()
        self._parser.read(files, r'utf-8')

        self._init_options()

    def read_str(self, val):

        self._parser.clear()
        self._parser.read_string(val)

        self._init_options()

    def read_dict(self, val):

        self._parser.clear()
        self._parser.read_dict(val)

        self._init_options()
