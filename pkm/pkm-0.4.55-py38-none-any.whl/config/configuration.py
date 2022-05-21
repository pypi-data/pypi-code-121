from __future__ import annotations

import configparser
from abc import ABC, abstractmethod
from copy import copy
from pathlib import Path
from typing import Optional, Dict, Any, List, Sequence, Mapping, Iterator, Callable, TypeVar, Tuple, Type, cast, \
    MutableMapping, Generic, Iterable

from pkm.config import toml
from pkm.utils.commons import UnsupportedOperationException


class Configuration:

    def __init__(
            self, *,
            parent: Optional["Configuration"] = None,
            data: Optional[Dict[str, Any]] = None):
        self._parent = parent
        self._data: Dict[str, Any] = data if data is not None else {}

    def __getitem__(self, item: Sequence[str]) -> Any:
        if isinstance(item, str):
            item = toml.key2path(item)

        r = self._get(item)
        if r is None and self._parent:
            r = self._parent[item]
        return r

    def __contains__(self, item: Sequence[str]):
        return self[item] is not None

    def _get(self, path: Sequence[str]) -> Any:
        r = self._data
        for p in path:
            if r is None:
                return None
            if not isinstance(r, Mapping):
                raise ValueError(f"path: {path} passing through a terminal value {r} at '{p}'")

            r = r.get(p)

        return r

    def _subs_chain(self) -> Iterator["Configuration"]:
        result = []
        r = self
        while r is not None:
            result.append(r)
            r = r._parent

        return reversed(result)

    def collect(self, path: Sequence[str]) -> Any:
        if isinstance(path, str):
            path = toml.key2path(path)

        result = self[path]
        if isinstance(result, List):
            return [it for conf in self._subs_chain() for it in (conf._get(path) or [])]
        elif isinstance(result, Mapping):
            return {k: v for conf in self._subs_chain() for k, v in (conf._get(path).items() or {})}

        return result

    def with_parent(self, new_parent: Optional["Configuration"]) -> "Configuration":
        cp = copy(self)
        cp._parent = new_parent
        return cp

    def items(self) -> Iterable[Tuple[str, Any]]:
        return cast(Iterable[Tuple[str, Any]], self._data.items())


class MutableConfiguration(Configuration, ABC):
    def __setitem__(self, key: Sequence[str], value: Any):
        if isinstance(key, str):
            key = toml.key2path(key)

        self._set(key, value)

    def __delitem__(self, key: Sequence[str]):
        if isinstance(key, str):
            key = toml.key2path(key)

        self._del(key)

    @abstractmethod
    def save_to(self, path: Optional[Path] = None):
        ...

    def save(self) -> bool:
        self.save_to(None)
        return True

    def _set(self, path: Sequence[str], value: Any):
        r = self._data
        for p in path[:-1]:
            if not isinstance(r, MutableMapping):
                raise ValueError(f"path: {path} passing through a terminal value {r} at '{p}'")

            rp = r.get(p)
            if rp is None:
                r[p] = r = {}
            else:
                r = rp

        r[path[-1]] = value

    def get_or_put(self, key: Sequence[str], value_computer: Callable[[], Any]) -> Any:
        if isinstance(key, str):
            key = toml.key2path(key)

        result = self[key]
        if result is None:
            self[key] = result = value_computer()

        return result

    def _del(self, path: Sequence[str]):
        r = self._data
        for p in path[:-1]:
            if r is None:
                return

            if not isinstance(r, Mapping):
                raise ValueError(f"path: {path} passing through a terminal value {r} at '{p}'")

            r = r.get(p)

        if r is not None:
            del r[path[-1]]


_T = TypeVar('_T')
_C1R = TypeVar("_C1R", bound=Callable[[Any], Any])
_C1N = TypeVar("_C1N", bound=Callable[[Any], None])


class _ComputedConfigValue(Generic[_T]):

    def __init__(self, func: Callable[[Any], _T], dependency_keys: Tuple[str, ...]):
        self._func = func
        self._dependency_keys = tuple(toml.key2path(key) for key in dependency_keys)
        self.__doc__ = func.__doc__
        self._setter = None

    def __set_name__(self, owner: Type, name):
        if not issubclass(owner, Configuration):
            raise ValueError(
                "computed_config_value decorator can only be applied on methods of configuration derivatives")
        self._attr = f"__computed_{name}"
        self._stamp_attr = f"__computed_{name}_stamp"
        self._configuration = owner

    def modifier(self, func: _C1N) -> _C1N:
        self._setter = func
        return func

    def __set__(self, instance, value: _T):
        if instance is None or self._setter is None:
            raise UnsupportedOperationException('immutable field')

        self._setter(instance, value)
        setattr(instance, self._stamp_attr, None)

    def __get__(self, instance, owner) -> _T:
        if instance is None:
            return self

        new_stamp = tuple(id(instance[d]) for d in self._dependency_keys)
        try:
            old_stamp = getattr(instance, self._stamp_attr)
            if old_stamp == new_stamp:
                return getattr(instance, self._attr)
        except AttributeError:
            ...

        new_value = self._func(instance)
        setattr(instance, self._attr, new_value)
        setattr(instance, self._stamp_attr, new_stamp)
        return new_value


def computed_based_on(*based_on_keys: str) -> Callable[[Callable[[Any], _T]], _ComputedConfigValue[_T]]:
    def _computed(func: Callable[[Any], Any]):
        return _ComputedConfigValue(func, based_on_keys)

    return _computed


class FileConfiguration(MutableConfiguration, ABC):
    def __init__(self, *, path: Optional[Path], parent: Optional["Configuration"] = None,
                 data: Optional[Dict[str, Any]] = None):
        super().__init__(parent=parent, data=data)
        self._path = path

    def exists_on_disk(self) -> bool:
        return self._path.exists()

    @abstractmethod
    def generate_content(self) -> str:
        ...

    def save_to(self, path: Optional[Path] = None):
        path = path or self._path
        path.parent.mkdir(exist_ok=True, parents=True)
        path.write_text(self.generate_content())

    def exists(self) -> bool:
        return self._path.exists()

    @property
    def path(self) -> Path:
        return self._path


class TomlFileConfiguration(FileConfiguration):

    def __init__(self, *, path: Optional[Path], parent: Optional["Configuration"] = None,
                 data: Optional[Dict[str, Any]] = None, dumps: Optional[Callable] = None):
        super().__init__(path=path, parent=parent, data=data)
        self._dumps = dumps

    def generate_content(self) -> str:
        dumps = self._dumps or toml.dumps
        return dumps(self._data)

    @classmethod
    def load(cls, file: Path, parent: Optional[Configuration] = None) -> "TomlFileConfiguration":
        data, dumps = toml.load(file) if file.exists() else ({}, None)
        return cls(path=file, parent=parent, data=data, dumps=dumps)


class InMemConfiguration(MutableConfiguration):

    def save_to(self, path: Optional[Path] = None):
        pass

    @classmethod
    def load(cls, data: Dict[str, Any], parent: Optional[Configuration]) -> "InMemConfiguration":
        return cls(parent=parent, data=data)


class _CaseSensitiveConfigParser(configparser.ConfigParser):
    optionxform = staticmethod(str)


class IniFileConfiguration(FileConfiguration):
    def generate_content(self) -> str:
        class StringWriter:
            def __init__(self):
                self.v: List[str] = []

            def write(self, s: str):
                self.v.append(s)

        sw = StringWriter()
        cp = _CaseSensitiveConfigParser()

        for key_or_section, value_or_content in self._data.items():
            if isinstance(value_or_content, Mapping):
                cp.add_section(key_or_section)
                for key, value in value_or_content.items():
                    cp.set(key_or_section, key, str(value))
            else:
                cp.set("", key_or_section, value_or_content)

        cp.write(sw)
        return ''.join(sw.v)

    @classmethod
    def load(cls, file: Path) -> "IniFileConfiguration":
        data = {}
        if file.exists():
            cp = _CaseSensitiveConfigParser()
            cp.read(str(file))
            for section_name, section_values in cp.items():
                if section_name and section_name != cp.default_section:
                    data[section_name] = {**section_values}
                else:
                    data.update(section_values)

        return cls(path=file, data=data)
