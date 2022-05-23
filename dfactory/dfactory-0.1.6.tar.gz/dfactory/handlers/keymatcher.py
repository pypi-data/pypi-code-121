# -*- coding: utf-8 -*-

"""
 a group of match the tell if match by key
"""
import abc
import re
from typing import Dict, List

from dfactory.core import LoaderMixin
from dfactory.core.utils import import_class


class KeyMatcher(LoaderMixin):
    """
    KeyMatcher is a class to describe some rules to check whether
    an item match these rules
    """

    @abc.abstractmethod
    def iter(self, item: Dict):
        """
        do check  with rules
        :param item: item to check
        :return: True if item match rules otherwise False
        """
        raise NotImplementedError("virtual function called")

    @staticmethod
    def from_dict(cfg: dict):
        """load a KeyMatcher from config"""
        cfg_class = import_class(cfg["class"])
        if cfg_class is not None and issubclass(cfg_class, KeyMatcher):
            obj = cfg_class()
            return obj
        return None


class ListKeyMatcher(KeyMatcher):
    """
    match if object has one of the keys
    """

    def __init__(self, keys: List[str] = None):
        self.keys = keys

    def iter(self, item: Dict):
        for key in self.keys:
            yield key, None

    def load_data(self, cfg: dict):
        """new ListKeyMatcher"""
        self.keys = cfg["keys"]


class RegexKeyMatcher(KeyMatcher):
    """
    regex key matcher
    """

    def __init__(self, regex: str = None):
        self.pattern = re.compile(regex) if regex is not None else None

    def iter(self, item: Dict):
        for key in item.keys():
            if self.pattern.match(key):
                yield key, None

    def load_data(self, cfg: dict):
        self.pattern = re.compile(cfg["regex"], cfg.get("flag", 0))


class FormatKeyMatcher(KeyMatcher):
    """
    format key matcher
    """

    def __init__(self, format_str: str = None, keys: List[str] = None):
        self.format_str = format_str
        self.keys = keys

    def iter(self, item: Dict):
        yield self.format_str.format_map({k: item[k] for k in self.keys}), None

    def load_data(self, cfg: dict):
        self.format_str = cfg["format"]
        self.keys = cfg["keys"]
