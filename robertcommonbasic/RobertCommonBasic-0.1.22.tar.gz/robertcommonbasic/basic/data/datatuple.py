import ast
import copy
import inspect
import json
import re

from datetime import datetime
from enum import Enum, EnumMeta
from typing import (Any, Callable, List, Mapping, NamedTuple, Optional, TextIO, Tuple, Type, Union)
from bson import ObjectId

import numpy as np
import pandas as pd

from ..validation import input as input_checker
from ..error.utils import InputDataError


class _MISSING_TYPE:
    def __bool__(self):
        return False

    def __getattribute__(self, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError:
            return MISSING

    def __getitem__(self, name: str) -> Any:
        return self.__getattribute__(name)


MISSING = _MISSING_TYPE()


class Field:
    def __init__(self,
                 default: Union[Any, _MISSING_TYPE] = MISSING,
                 default_factory: Union[Callable, _MISSING_TYPE] = MISSING,
                 metadata: Mapping[str, Any] = None,
                 tags: List[str] = []):
        if metadata is None:
            metadata = {}
        self.default = default
        self.default_factory = default_factory
        self.metadata = metadata
        self.tags = tags
        return


def field(default: Union[Any, _MISSING_TYPE] = MISSING,
          default_factory: Union[Callable, _MISSING_TYPE] = MISSING,
          metadata: Mapping[str, Any] = None,
          tags: List[str] = []) -> Any:
    if metadata is None:
        metadata = {}
    if default is not MISSING and default_factory is not MISSING:
        raise ValueError('cannot specify both default and default_factory')
    return Field(default=default,
                 default_factory=default_factory,
                 metadata=metadata,
                 tags=tags)


def is_union_type(t) -> bool:
    return getattr(t, '__origin__', None) is Union


def union_expander(func):
    def _union_expander(t,
                        expand_union: bool = False,
                        *args,
                        **kwargs) -> Optional[Type]:
        if expand_union and is_union_type(t):
            t_l = t.__args__
            rv_list = []
            for t_c in t_l:
                rv = func(t_c, *args, **kwargs)
                if rv:
                    return rv
            return None
        return func(t, *args, **kwargs)

    return _union_expander


@union_expander
def is_enum_type(t) -> bool:
    if getattr(t, '__class__', None) is EnumMeta:
        return t


def is_enum_value(enum_cls, v) -> bool:
    try:
        enum_cls(v)
    except ValueError:
        return False
    return True


def is_enum_key(enum_cls, k) -> bool:
    return getattr(enum_cls, k, MISSING) is not MISSING


@union_expander
def is_list_type(t) -> Type:
    if getattr(t, '__origin__', None) is List:
        return t.__args__[0]
    else:
        return None


@union_expander
def is_numeric_type(t) -> Optional[Type]:
    if t in [int, float]:
        return True


@union_expander
def is_datatuple_type(t: Type) -> Optional[Type]:
    if inspect.isclass(t) and issubclass(t, DataTuple):
        return t


class NumericDataRange(NamedTuple):
    max: Union[int, float, None]
    min: Union[int, float, None]

    def check_value(self, value: Union[int, float]):
        if self.max is not None and value > self.max:
            raise InputDataError(f'value={value} must less than {self.max}')
        if self.min is not None and value < self.min:
            raise InputDataError(f'value={value} must greater than {self.min}')


TIME_FORMAT_META = 'time_format'


class DataTuple:
    __annotations__: dict = {}
    _field_data: dict = {}

    def __new__(cls,
                init_default: bool = True,
                skip_init: bool = False,
                **kwargs):
        # special annotation parse
        cls.__annotations__ = {
            k[2:-2] if k.startswith('__') and k.endswith('__') else k: v
            for k, v in cls.__annotations__.items()
        }
        if skip_init:
            return super().__new__(cls, **kwargs)
        else:
            return cls.from_dict(kwargs, init_default=init_default)

    @classmethod
    def load_json_str(cls, s: str) -> Union[list, dict, str]:
        assert isinstance(s, str)
        try:
            s = json.loads(s)
        except Exception:
            try:
                s = ast.literal_eval(s)
            except Exception:
                pass
        return s

    def parse_dict(self, attribute_name: str, attribute_type: Any,
                   attribute_value: Any) -> Any:
        value: Any
        if attribute_type is type(None):
            if not attribute_value:
                value = None
            else:
                raise InputDataError(
                    '{attribute_name}:{attribute_value} is not None')
        elif attribute_type is int:
            value = input_checker.ensure_not_none_int(attribute_name,
                                                      attribute_value)
        elif attribute_type is str:
            value = input_checker.ensure_not_none_str(attribute_name,
                                                      attribute_value)
        elif attribute_type is ObjectId:
            value = input_checker.ensure_not_none_objid(
                attribute_name, attribute_value)
        elif attribute_type is float:
            value = input_checker.ensure_not_none_float(
                attribute_name, attribute_value)
        elif attribute_type is bool:
            value = input_checker.ensure_not_none_bool(attribute_name,
                                                       attribute_value)
        elif attribute_type is datetime:
            time_format = self.get_attribute_field_metadata_by_key(
                attribute_name, TIME_FORMAT_META) or '%Y-%m-%d %H:%M:%S'
            value = input_checker.ensure_not_none_datetime(
                attribute_name, attribute_value, time_format)
        elif is_list_type(attribute_type):
            list_attribute_type = is_list_type(attribute_type)
            assert list_attribute_type
            if isinstance(attribute_value, str):
                attribute_value = self.load_json_str(attribute_value)
            if not isinstance(attribute_value, list):
                raise InputDataError(f'{attribute_value} is not list')
            value = [
                self.parse_dict('', list_attribute_type, item)
                for item in attribute_value
            ]
        elif is_enum_type(attribute_type):
            value = MISSING
            try:
                if attribute_value is None and None in [
                        v.value for v in attribute_type.__members__.values()
                ]:
                    value = attribute_type(None)
                else:
                    value = input_checker.ensure_not_none_enum(
                        attribute_name, attribute_value, attribute_type)
            except:
                try:
                    value = input_checker.ensure_not_none_enum(
                        attribute_name, int(attribute_value), attribute_type)
                except:
                    try:
                        value = input_checker.ensure_not_none_enum(
                            attribute_name, str(int(attribute_value)),
                            attribute_type)
                    except:
                        pass
            if value == MISSING:
                raise InputDataError(
                    f'can not parse enum type={attribute_type}, attribute_value={attribute_value}'
                )
        elif is_datatuple_type(attribute_type):
            if isinstance(attribute_value, str):
                attribute_value = self.load_json_str(attribute_value)
            if attribute_type is DataTuple:
                if not inspect.isclass(attribute_value) or not issubclass(
                        attribute_value, DataTuple):
                    raise InputDataError(
                        f'attribute_value={attribute_value} must be the subclass of Datatuple'
                    )
                return attribute_value
            elif issubclass(attribute_value.__class__, DataTuple):
                value = attribute_value
            elif isinstance(attribute_value, dict):
                # noinspection PyArgumentList
                value = attribute_type(init_default=self.init_default,
                                       **attribute_value)
            elif isinstance(attribute_value, str):
                value = attribute_type(init_default=self.init_default,
                                       **json.loads(attribute_value or '{}'))
            else:
                raise InputDataError(f'{attribute_value} is not dict')
        elif is_union_type(attribute_type):
            attribute_type_list = attribute_type.__args__
            value = MISSING
            for attribute_type in attribute_type_list:
                try:
                    value = self.parse_dict(attribute_name, attribute_type,
                                            attribute_value)
                except InputDataError:
                    continue
                if value is not MISSING:
                    break
            if value is MISSING:
                raise InputDataError(
                    f'{attribute_value} is not vaild type for union type {attribute_type_list}'
                )
        elif attribute_type is dict:
            if isinstance(attribute_value, dict):
                value = attribute_value
            elif isinstance(attribute_value, str):
                try:
                    value = ast.literal_eval(attribute_value) or {}
                    assert isinstance(value, dict)
                except:
                    raise InputDataError(
                        f'can not parse string={attribute_value} to dict')
            else:
                raise InputDataError(f'{attribute_value} is not dict')
        elif attribute_type is Any:
            value = attribute_value
        else:
            value = attribute_value
        # check data range if attribute type is numeric
        if is_numeric_type(attribute_type):
            data_range = self.get_attribute_field_metadata_by_key(
                attribute_name, 'data_range', ensure=False)
            if data_range:
                NumericDataRange(**data_range).check_value(value)
        return value

    def save_attribute_field_data(self,
                                  attribute_name: str,
                                  attribute_field: Optional[Field] = None):
        if attribute_field:
            self._field_data[attribute_name] = attribute_field
        else:
            attribute_data = getattr(self, attribute_name, None)
            if attribute_data and isinstance(attribute_data, Field):
                self._field_data[attribute_name] = getattr(
                    self, attribute_name)

    def get_attribute_field_data(self, attribute_name: str) -> Field:
        return self._field_data.get(attribute_name) or Field()

    def get_attribute_field_metadata_by_key(self,
                                            attribute_name: str,
                                            metadata_key: str,
                                            default: Any = MISSING,
                                            ensure=True) -> Any:
        field_data = self.get_attribute_field_data(attribute_name)
        if not field_data:
            raise InputDataError(f'no field data {attribute_name}')
        try:
            if default is not MISSING:
                return field_data.metadata.get(metadata_key, default)
            else:
                return field_data.metadata.get(metadata_key)
        except Exception:
            if ensure:
                raise InputDataError(
                    f'{attribute_name} metadata must include {metadata_key}')
            else:
                return None

    @classmethod
    def from_dict(cls,
                  d: dict,
                  init_default: bool = True,
                  ignore_error=False,
                  **kwargs):
        instance = cls(skip_init=True)
        instance.init_default = init_default
        for attribute_name in instance.__annotations__.keys():
            instance.save_attribute_field_data(attribute_name)
            value = MISSING
            if attribute_name in d and d[attribute_name] is not MISSING:
                value = d[attribute_name]
            else:
                field_data = instance.get_attribute_field_data(attribute_name)
                if field_data.default is not MISSING and init_default:
                    value = field_data.default
                elif field_data.default_factory is not MISSING and init_default:
                    value = field_data.default_factory()
            try:
                setattr(instance, attribute_name, value)
            except:
                if not ignore_error:
                    raise
        return instance

    def _update_by_dict(self, obj):
        assert isinstance(obj, dict)
        for attribute_name, attribute_value in obj.items():
            if attribute_name in self.__annotations__:
                setattr(self, attribute_name, attribute_value)

    def update(self, obj: Union[dict, 'DataTuple']):
        if isinstance(obj, dict):
            self._update_by_dict(obj)
        elif isinstance(obj, DataTuple):
            self._update_by_dict(obj.to_json())
        else:
            raise InputDataError(f'can not update with {obj}')
        return self

    def parse_json_auto(self,
                        attribute_value: Any,
                        parse_any_objid: bool = False) -> Any:
        if is_enum_type(attribute_value.__class__):
            value = attribute_value.value
        elif isinstance(attribute_value, ObjectId) and parse_any_objid:
            value = str(attribute_value)
        elif isinstance(attribute_value, list):
            value = [
                self.parse_json_auto(v, parse_any_objid)
                for v in attribute_value
            ]
        elif isinstance(attribute_value, dict):
            value = {
                k: self.parse_json_auto(v, parse_any_objid)
                for k, v in attribute_value.items()
            }
        elif isinstance(attribute_value, DataTuple):
            value = attribute_value.to_json()
        else:
            value = attribute_value
        return value

    def parse_json(self,
                   attribute_name: str,
                   attribute_type: Any,
                   attribute_value: Any = MISSING,
                   recursive_func: Optional[callable] = None,
                   parse_any_objid: bool = True,
                   **kwargs):
        value = MISSING
        recursive_func = recursive_func if recursive_func else self.parse_json
        if attribute_value is MISSING:
            attribute_value = getattr(self, attribute_name)
            if attribute_value is MISSING:
                return attribute_value
        if attribute_type in (int, float, str, bool, dict, type(None)):
            value = attribute_value
        elif attribute_type == Any:
            value = self.parse_json_auto(attribute_value,
                                         parse_any_objid=parse_any_objid)
        elif attribute_type is ObjectId:
            value = input_checker.ensure_not_none_objid_str(
                attribute_name, attribute_value)
        elif attribute_type is datetime:
            attribute_value: datetime
            time_format = self.get_attribute_field_metadata_by_key(
                attribute_name, TIME_FORMAT_META) or '%Y-%m-%d %H:%M:%S'
            value = attribute_value.strftime(time_format)
        elif is_list_type(attribute_type):
            list_attribute_type = attribute_type.__args__[0]
            if not isinstance(attribute_value, list):
                raise InputDataError(f'{attribute_value} is not list')
            value = [
                recursive_func(attribute_name,
                               list_attribute_type,
                               item,
                               recursive_func=recursive_func,
                               parse_any_objid=parse_any_objid,
                               **kwargs) for item in attribute_value
            ]
        elif is_enum_type(attribute_type):
            try:
                return attribute_value.value
            except:
                raise InputDataError(
                    f'attribute_value={attribute_value} is not enum type of {attribute_type}'
                )
        elif inspect.isclass(attribute_type) and issubclass(
                attribute_type, DataTuple):
            if attribute_type is DataTuple:
                if not inspect.isclass(attribute_value) or not issubclass(
                        attribute_value, DataTuple):
                    raise InputDataError(
                        f'attribute_value={attribute_value} must be the subclass of Datatuple'
                    )
                value = attribute_value
            elif issubclass(attribute_value.__class__, DataTuple):
                func_name = recursive_func.__name__
                recursive_func_datatuple = getattr(attribute_value, func_name,
                                                   None)
                if recursive_func_datatuple:
                    value = attribute_value.to_dict(
                        parser=recursive_func_datatuple,
                        parse_any_objid=parse_any_objid,
                        **kwargs)
                else:
                    raise Exception(
                        f'Can not use {func_name} on datatuple {attribute_value.__class__.__name__}'
                    )
        elif is_union_type(attribute_type):
            attribute_type_list = attribute_type.__args__
            for attribute_type in attribute_type_list:
                try:
                    value = recursive_func(attribute_name,
                                           attribute_type,
                                           attribute_value,
                                           recursive_func=recursive_func,
                                           parse_any_objid=parse_any_objid,
                                           **kwargs)
                except:
                    continue
                if value is not MISSING:
                    break
        else:
            value = MISSING
        return value

    def to_dict(self,
                parser: Optional[callable] = None,
                attributes: Optional[List[str]] = None,
                tags: Optional[List[str]] = None,
                default: Any = MISSING,
                parse_any_objid: bool = False,
                **kwargs) -> dict:
        d = {}
        if tags:
            attributes = self.get_attribute_names(tags=tags)
        for attribute_name, attribute_type in self.__annotations__.items():
            if attributes and attribute_name not in attributes:
                continue
            if getattr(self, attribute_name) is not MISSING and not isinstance(
                    getattr(self, attribute_name), Field):
                if parser:
                    attribute_value = parser(attribute_name,
                                             attribute_type,
                                             tags=tags,
                                             default=default,
                                             parse_any_objid=parse_any_objid,
                                             **kwargs)
                else:
                    attribute_value = getattr(self, attribute_name)
                if attribute_value is not MISSING:
                    d[attribute_name] = attribute_value
            elif getattr(self,
                         attribute_name) is MISSING and default is not MISSING:
                d[attribute_name] = default
        return d

    def to_json(self,
                attributes: Optional[List[str]] = None,
                tags: Optional[List[str]] = None,
                default: Any = MISSING,
                **kwargs) -> dict:
        return self.to_dict(parser=self.parse_json,
                            attributes=attributes,
                            tags=tags,
                            default=default,
                            parse_any_objid=True,
                            **kwargs)

    def to_tuple(self,
                 attributes: Optional[List[str]] = None,
                 tags: Optional[List[str]] = None,
                 default: Any = MISSING,
                 json_to_string: bool = False,
                 **kwargs) -> tuple:
        j = self.to_json(attributes=attributes,
                         tags=tags,
                         default=default,
                         **kwargs)
        t_l = [(k, v) for k, v in j.items()]
        t_l = sorted(t_l, key=lambda t: attributes.index(t[0]))
        t = tuple(
            json.dumps(t[1], ensure_ascii=False) if json_to_string and (
                isinstance(t[1], list) or isinstance(t[1], dict)) else t[1]
            for t in t_l)
        return t

    def parse_bson(self,
                   attribute_name,
                   attribute_type,
                   attribute_value=MISSING,
                   recursive_func: Optional[callable] = None,
                   parse_any_objid: bool = False,
                   **kwargs):
        recursive_func = recursive_func if recursive_func else self.parse_bson
        if attribute_value is MISSING:
            attribute_value = getattr(self, attribute_name, None)
        if attribute_type in (ObjectId, datetime):
            value = attribute_value
        else:
            value = self.parse_json(attribute_name,
                                    attribute_type,
                                    attribute_value=attribute_value,
                                    recursive_func=recursive_func,
                                    parse_any_objid=parse_any_objid,
                                    **kwargs)
        return value

    def to_bson(self,
                attributes: Optional[str] = None,
                default: Any = MISSING,
                **kwargs) -> dict:
        return self.to_dict(parser=self.parse_bson,
                            attributes=attributes,
                            default=default,
                            **kwargs)

    def ensure_attributes(self,
                          ensure_attributes: Optional[List[str]] = None,
                          exclude_attributes: Optional[List[str]] = None):
        if ensure_attributes:
            for attribute_name in ensure_attributes:
                if getattr(self, attribute_name) is MISSING:
                    raise InputDataError(
                        f'{self.to_json()} not have attribute={attribute_name}'
                    )
        if exclude_attributes:
            for attribute_name in exclude_attributes:
                if getattr(self, attribute_name) is not MISSING:
                    delattr(self, attribute_name)
        return

    def __str__(self) -> str:
        attribute_str = ', '.join(
            [f'{k}={repr(v)}' for k, v in self.to_json().items()])
        return f'{self.__class__.__name__}({attribute_str})'

    def __setattr__(self, attribute_name: str, attribute_value: Any):
        if attribute_name in self.__annotations__:
            if attribute_value is not MISSING:
                attribute_type = self.__annotations__[attribute_name]
                attribute_value = self.parse_dict(attribute_name,
                                                  attribute_type,
                                                  attribute_value)
            super().__setattr__(attribute_name, attribute_value)
        else:
            super().__setattr__(attribute_name, attribute_value)

    def __getattribute__(self, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError:
            if name not in super().__getattribute__('__annotations__'):
                raise AttributeError(
                    f'error attribute={name} not in annotations')
            else:
                return MISSING

    def __getitem__(self, name: str) -> Any:
        return self.__getattribute__(name)

    def __setitem__(self, attribute_name: str, attribute_value: Any):
        self.__setattr__(attribute_name, attribute_value)

    def __eq__(self, other: Any):
        if self.__class__ == other.__class__:
            for attribute_name in self.__annotations__.keys():
                if not getattr(self, attribute_name, MISSING) == getattr(
                        other, attribute_name, MISSING):
                    return False
            return True
        else:
            return False

    @classmethod
    def get_attribute_names(cls, tags: List[str] = [], **kwargs) -> List[str]:
        attribute_names = []
        if not tags:
            return list(cls.__annotations__.keys())
        for attribute_name, attribute_field in cls.__dict__.items():
            if attribute_field and isinstance(
                    attribute_field, Field) and set(tags).intersection(
                        set(attribute_field.tags)):
                attribute_names.append(attribute_name)
            else:
                continue
        return attribute_names

    def filter_attributes(self,
                          tags: Optional[List[str]] = None,
                          attributes: Optional[List[str]] = None,
                          recursive: bool = True,
                          **kwargs):
        if attributes:
            remain_attributes = set(attributes).intersection(
                set(self.get_attribute_names(tags=tags)))
        else:
            remain_attributes = set(self.get_attribute_names(tags=tags))
        attributes_remove = set(
            self.get_attribute_names()).difference(remain_attributes)
        for attr in attributes_remove:
            self[attr] = MISSING
        if recursive:
            for attr in remain_attributes:
                attr_type = self.__annotations__[attr]
                list_element_type = is_list_type(attr_type, expand_union=True)
                if list_element_type and self[attr]:
                    for i, v in enumerate(self[attr]):
                        self[attr][i].filter_attributes(tags=tags,
                                                        recursive=recursive)
                if is_datatuple_type(attr_type, expand_union=True) and self[attr]:
                    self[attr].filter_attributes(tags=tags,
                                                 recursive=recursive)


DEFAULT_SUPPORTED_LANG = ['en', 'zh']


class MultiLangData(DataTuple):
    langs: List[str]
    data_type: DataTuple


class MultiLangDataTuple(DataTuple):
    @classmethod
    def combine_lang_key(cls, attribute_name: str, lang: str) -> str:
        return f'{attribute_name}.{lang}'

    @classmethod
    def parse_lang_key(cls,
                       lang_key: str,
                       ignore_error=False) -> Tuple[str, Optional[str]]:
        attribute_name = lang_key
        lang = None
        m = re.match(r'(\w+).(\w+)', lang_key)
        if m:
            attribute_name_parsed = m.group(1)
            lang_parsed = m.group(2)
            attribute_type = cls.__annotations__.get(attribute_name_parsed)
            if inspect.isclass(attribute_type) and issubclass(
                    attribute_type, MultiLangData):
                if lang_parsed not in attribute_type.langs and not ignore_error:
                    raise InputDataError(
                        f'lang={lang_parsed} is not supported with attribute_type={attribute_type}'
                    )
                else:
                    attribute_name = attribute_name_parsed
                    lang = lang_parsed
        return attribute_name, lang

    @classmethod
    def from_dict(cls,
                  d: dict,
                  init_default: bool = True,
                  ignore_error: bool = False,
                  expand_lang: bool = False,
                  **kwargs):
        if expand_lang:
            for k, v in copy.deepcopy(d).items():
                attribute_name, lang = cls.parse_lang_key(
                    k, ignore_error=ignore_error)
                if attribute_name and lang:
                    attribute_dict = d.get(attribute_name)
                    if attribute_dict:
                        attribute_dict[lang] = v
                    else:
                        d[attribute_name] = {lang: v}
                    d.pop(k, None)
        instance = super().from_dict(d=d,
                                     init_default=init_default,
                                     ignore_error=ignore_error,
                                     **kwargs)
        return instance

    def parse_dict(self, attribute_name: str, attribute_type: Any,
                   attribute_value: Any) -> Any:
        if inspect.isclass(attribute_type) and \
                issubclass(attribute_type, MultiLangData) and \
                isinstance(attribute_value, str):
            value = self.load_json_str(attribute_value)
            if isinstance(value, str):
                value = attribute_type(
                    **{lang: attribute_value
                       for lang in attribute_type.langs})
                return value
        value = super().parse_dict(attribute_name=attribute_name,
                                   attribute_type=attribute_type,
                                   attribute_value=attribute_value)
        return value

    @staticmethod
    def is_multi_lang_type(attribute_type):
        if inspect.isclass(attribute_type) and issubclass(
                attribute_type, MultiLangData):
            return True
        elif getattr(attribute_type, '__origin__', None) is Union:
            for attribute_type_child in attribute_type.__args__:
                if inspect.isclass(attribute_type_child) and issubclass(
                        attribute_type_child, MultiLangData):
                    return True

    def to_dict(self,
                parser: Optional[callable] = None,
                attributes: Optional[List[str]] = None,
                default: Any = MISSING,
                expand_lang: bool = False,
                **kwargs) -> dict:
        d = super().to_dict(parser=parser,
                            attributes=attributes,
                            default=default,
                            **kwargs)
        if expand_lang:
            for attribute_name, attribute_type in self.__annotations__.items():
                if self.is_multi_lang_type(
                        attribute_type) and attribute_name in d:
                    attribute_value = d[attribute_name]
                    if isinstance(attribute_value, dict):
                        for lang, item in attribute_value.items():
                            d[self.combine_lang_key(attribute_name,
                                                    lang)] = item
                        d.pop(attribute_name, None)
        return d

    @classmethod
    def get_attribute_names(cls,
                            expand_lang: bool = False,
                            **kwargs) -> List[str]:
        attribute_names = super().get_attribute_names(**kwargs)
        if expand_lang:
            for attribute_name, attribute_type in cls.__annotations__.items():
                if inspect.isclass(attribute_type) and issubclass(
                        attribute_type,
                        MultiLangData) and attribute_name in attribute_names:
                    attribute_names.remove(attribute_name)
                    attribute_names.extend([
                        f'{attribute_name}.{lang}'
                        for lang in attribute_type.langs
                    ])
        return attribute_names


def multi_lang(data_type: Any, langs: List[str] = ['en', 'zh']):
    langs = input_checker.ensure_not_none_list_of(
        'langs', langs, input_checker.ensure_not_none_str)

    class MultiLangDataGen(MultiLangData):
        def __new__(cls, **kwargs):
            cls.__annotations__ = {lang: data_type for lang in langs}
            return super().__new__(cls, **kwargs)

        def to_dict(self,
                    parser: Optional[callable] = None,
                    attributes: Optional[List[str]] = None,
                    default: Any = MISSING,
                    lang: str = None,
                    **kwargs) -> dict:
            j = super().to_dict(parser=parser,
                                attributes=attributes,
                                default=default)
            if isinstance(j, dict):
                if default is not MISSING:
                    for l in self.__annotations__.keys():
                        if l not in j:
                            j[l] = default
                for l in dict(j).keys():
                    if l not in self.langs:
                        j.pop(l, None)
            if not isinstance(j, dict) or not lang:
                return j
            elif lang and lang in self.langs:
                return j.get(lang, None)
            elif lang and lang not in self.langs:
                raise InputDataError(
                    f'input lang is not supported, must in {self.langs}')

    MultiLangDataGen.langs = langs
    MultiLangDataGen.data_type = data_type
    return MultiLangDataGen


def datatuples_to_json(datatuples: List[DataTuple], **kwargs) -> List[dict]:
    j = [datatuple.to_json(**kwargs) for datatuple in datatuples]
    return j


def datatuples_to_bson(datatuples: List[DataTuple], **kwargs) -> List[dict]:
    b = [datatuple.to_bson(**kwargs) for datatuple in datatuples]
    return b


def datatuples_to_pandas(datatuples: List[DataTuple],
                         **kwargs) -> Optional[pd.DataFrame]:
    if not datatuples:
        return
    j = datatuples_to_json(datatuples, **kwargs)
    df = pd.DataFrame(j)
    return df


def parse_datatuple_df_for_export(datatuples: List[DataTuple],
                                  default: Any = MISSING,
                                  columns: Optional[List[str]] = None,
                                  **kwargs) -> Optional[pd.DataFrame]:
    df = datatuples_to_pandas(datatuples=datatuples, default=default, **kwargs)
    attribute_names = datatuples[0].get_attribute_names(**kwargs)
    if not columns:
        columns = attribute_names
    else:
        columns = np.intersect1d(columns, attribute_names)
    columns_not_exists = np.setdiff1d(columns, df.columns)
    for column in columns_not_exists:
        df[column] = np.NaN
    return df


def df_to_datatuples(datatuple_class: DataTuple,
                     df: pd.DataFrame,
                     init_default: bool = True,
                     ignore_error: bool = False,
                     **kwargs) -> List[DataTuple]:
    # drop nan
    data = {
        k1: {k: v
             for k, v in v1.items() if v == v and v is not None}
        for k1, v1 in df.T.to_dict().items()
    }
    datatuples = [
        datatuple_class.from_dict(d,
                                  init_default=init_default,
                                  ignore_error=ignore_error,
                                  **kwargs) for d in data.values()
    ]
    return datatuples


class SheetType(Enum):
    csv = 'csv'
    excel = 'excel'


def datatuples_to_sheet(datatuples: List[DataTuple],
                        path: Optional[str] = None,
                        io: Optional[TextIO] = None,
                        default: Any = MISSING,
                        columns: Optional[List[str]] = None,
                        sheet_name: Optional[str] = None,
                        sheet_type: SheetType = SheetType.csv,
                        excel_writer: Optional[pd.ExcelWriter] = None,
                        encoding: str = 'utf-8-sig',
                        **kwargs):
    sheet_type = input_checker.ensure_not_none_enum('sheet_type', sheet_type,
                                                    SheetType)
    df = parse_datatuple_df_for_export(datatuples=datatuples,
                                       default=default,
                                       columns=columns,
                                       **kwargs)
    if not isinstance(df, pd.DataFrame) or df.empty:
        return
    if not path and not io:
        raise InputDataError('datatuple_to_csv: must input path or io')
    if sheet_type == SheetType.csv:
        df.to_csv(path or io, index=False)
    elif sheet_type == SheetType.excel:
        if not excel_writer:
            excel_writer = pd.ExcelWriter(path or io, engine='xlsxwriter')
        if sheet_name:
            df.to_excel(excel_writer,
                        sheet_name=sheet_name,
                        index=False,
                        encoding=encoding)
        else:
            df.to_excel(excel_writer, index=False, encoding=encoding)
        if excel_writer:
            excel_writer.save()
    else:
        raise NotImplementedError()


def datatuples_read_sheet(datatuple_class: DataTuple,
                          path: Optional[str] = None,
                          io: Optional[TextIO] = None,
                          init_default: bool = True,
                          ignore_error: bool = False,
                          engine: str = 'openpyxl',
                          sheet_name: Optional[str] = None,
                          sheet_type: SheetType = SheetType.csv,
                          **kwargs) -> List[DataTuple]:
    if sheet_type == SheetType.csv:
        df = pd.read_csv(path or io)
    elif sheet_type == SheetType.excel:
        if sheet_name:
            df = pd.read_excel(path or io,
                               engine=engine,
                               sheet_name=sheet_name)
        else:
            df = pd.read_excel(path or io, engine=engine)
    else:
        raise NotImplementedError()
    return df_to_datatuples(datatuple_class=datatuple_class,
                            df=df,
                            init_default=init_default,
                            ignore_error=ignore_error,
                            **kwargs)

