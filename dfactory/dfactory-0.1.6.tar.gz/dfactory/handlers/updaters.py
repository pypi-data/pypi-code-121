# -*- coding: utf-8 -*-

"""
Updater is a class to update item
"""
import abc
import re
from typing import Dict, Tuple, List

from dfactory.core import Handler
from .keymatcher import KeyMatcher


class Updater(Handler):
    """
    data updater，负责的工作是根据配置更新相应的字段
    负责处理具体的问题是:
    1、哪些字段需要更新
        1.1 字段确定： 静态确定，动态确定（需要根据值来确定）
        1.2 字段数目: 单个，多个
    2、怎么更新对应的字段
        2.1 静态依赖：只依赖自身的值
        2.2 动态依赖：其他字段的值

    """

    def __init__(self, key_matcher=None):
        """
        constructor
        :param key_matcher: dict or KeyMatcher object
        """
        self.key_matcher = key_matcher

    def iter_update_keys(self, item: Dict) -> Tuple[str, Dict]:
        """
        获取需要改动的key
        :param item: 被更新的对象
        :return: key which need to modify and data for updating value
        """
        if isinstance(self.key_matcher, dict):
            for key, value in self.key_matcher.items():
                yield key, {"value": value}
        else:
            for key, value in self.key_matcher.iter(item):
                yield key, value

    @abc.abstractmethod
    def get_new_value(self, item: Dict, key: str, options: Dict) -> object:
        """
        get new value for the specify key
        :param item: item
        :param key: field to update
        :param options: extra data
        :return: new value for the specified key
        """
        raise NotImplementedError('virtual function called')

    def log_empty_value(self, item, key):
        """log value when item[key] is empty"""

    def handle(self, item: dict) -> dict:
        item_copy = item.copy()
        for key, opt in self.iter_update_keys(item):
            value = self.get_new_value(item, key, opt)
            if value is None:
                self.log_empty_value(item, key)
                continue
            item_copy[key] = value
        return item_copy

    def load_data(self, cfg: dict):
        self.key_matcher = KeyMatcher.from_dict(cfg)


class RegexUpdater(Updater):
    """update field with regex"""

    def __init__(self, key_matcher=None, **kwargs):
        """
        initializing function
        :param key_matcher: a Match, what items need to update
        :param pattern: update pattern
        :param field: field to update
        :param flags: regex pattern flag, default 0
        :param replace: regex replacement of the update field
        """
        Updater.__init__(self, key_matcher)
        self.regex = re.compile(kwargs.get("pattern"), flags=kwargs.get("flag", 0)) \
            if "pattern" in kwargs else None
        self.field = kwargs.get("field", "")
        self.replace = kwargs.get("replace", "")

    def get_new_value(self, item: Dict, key: str, options: Dict) -> object:
        """
        make new value for specified key
        :param item: item to update
        :param key: key to update
        :param options: update options
        :return: None if no update otherwise new value of the required field
        """
        value = item.get(key if self.field is None else self.field)
        if value is None:
            return None
        return self.regex.sub(self.replace, value)

    def load_data(self, cfg: dict):
        super().load_data(cfg)
        self.regex = re.compile(cfg['pattern'], cfg.get('flag', 0))
        self.field = cfg['field']
        self.replace = cfg['replace']


class CombineUpdater(Updater):
    """an updater to combine two field"""

    def __init__(self, key_matcher=None, format_str: str = None,
                 key: str = None, mapper: Dict[str, str] = None):
        Updater.__init__(self, key_matcher)
        self.format = format_str
        self.key = key
        self.mapper = mapper

    def get_new_value(self, item: Dict, key: str, options: Dict) -> object:
        return self.format.format_map({"src": item[key], "dst": self.mapper.get(item[self.key])})

    def load_data(self, cfg: dict):
        super().load_data(cfg)
        self.format = cfg['format']
        self.key = cfg['key']
        self.mapper = cfg['mapper']


class FormatUpdater(Updater):
    """format updater, update field with new format"""

    def __init__(self, key_matcher, pattern: str, keys: List[str] = None):
        Updater.__init__(self, key_matcher)
        self.pattern = pattern
        self.keys = keys

    def get_new_value(self, item: Dict, key: str, options: Dict) -> object:
        return self.pattern.format_map({k: item[k] for k in self.keys})

    def load_data(self, cfg: dict):
        super().load_data(cfg)
        self.pattern = cfg['pattern']
        self.keys = cfg['keys']


class MapperUpdater(Updater):
    """
    字典更新类，负责的工作是根据配置更新相应的字段
    负责处理具体的问题是:
    1、哪些字段需要更新
        1.1 字段确定： 静态确定，动态确定（需要根据值来确定）
        1.2 字段数目: 单个，多个
    2、怎么更新对应的字段
        2.1 静态依赖：只依赖自身的值
        2.2 动态依赖：其他字段的值

    """

    def __init__(self, key_matcher, key_dependence: Dict, value_maps: Dict):
        """

        :param key_matcher: key matcher, describe what keys to update or add
        :param key_dependence: describe how to get value from value_maps
        :param value_maps: value maps
        """
        Updater.__init__(self, key_matcher)
        self.key_depends = key_dependence
        self.value_maps = value_maps

    def get_new_value_on_single_key(self, key, item: Dict):
        """new value for single key"""
        dep_key = self.key_depends[key]['key']
        item_key = self.key_depends[key].get('item_key', key)
        values = self.value_maps[dep_key]
        search_value = item[item_key] if \
            self.key_depends[key].get("type", "value") == "value" else item_key
        return values.get(search_value)

    def get_new_value_on_multiple_keys(self, keys, item: Dict, options: Dict):
        """get new value from multiple key"""
        raise NotImplementedError('not implement yet')

    def get_new_value(self, item: Dict, key: str, options: Dict) -> object:
        """
        get new value for the specify key
        :param item: item
        :param key: field to update
        :param options:
        :return:
        """
        if key not in self.key_depends:
            return options.get('value')
        if isinstance(self.key_depends[key]['key'], str):
            return self.get_new_value_on_single_key(key, item)
        return self.get_new_value_on_multiple_keys(key, item, options)

    def log_empty_value(self, item, key):
        print(f"{item.get(key)} depends on key item[{key}]{self.key_depends.get(key)} got None")

    def load_data(self, cfg: dict):
        super().load_data(cfg)
        self.key_depends = cfg['dependence']
        self.value_maps = cfg['value_maps']
