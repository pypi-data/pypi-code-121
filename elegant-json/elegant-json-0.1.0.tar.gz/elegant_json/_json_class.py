from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Iterable

from ._json_attribute import Attr

_JSON_TEMPLATE = "__json_template__"
_JSON_MUTABLE = "__json_mutable__"

def _iter_dict(d: dict[str, Any | None], keys: list[str | int]) -> Iterable[tuple[Any | None, list[str | int]]]:
    for k, v in d.items():
        next_keys = keys + [k]
        if isinstance(v, (list, tuple)):
            yield from  _iter_list(v, next_keys)
        elif isinstance(v, dict):
            yield from  _iter_dict(v, next_keys)
        else:
            yield v, next_keys

def _iter_list(l: Iterable[Any | None], keys: list[str | int]) -> Iterable[tuple[Any | None, list[str | int]]]:
    for k, v in enumerate(l):
        next_keys = keys + [k]
        if isinstance(v, (list, tuple)):
            yield from  _iter_list(v, next_keys)
        elif isinstance(v, dict):
            yield from  _iter_dict(v, next_keys)
        else:
            yield v, next_keys


class JsonClassMeta(type):
    """The metaclass of JsonClass."""
    
    __json_template__: dict[str, Any | None] = {}
    __json_mutable__: bool = False
    _json_properties: frozenset[str]

    def __new__(
        cls: type,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwds,
    ) -> JsonClassMeta:
        
        _js_temp = namespace.get(_JSON_TEMPLATE, {})
        _mutable = namespace.get(_JSON_MUTABLE, False)
        _annot = namespace.get("__annotations__", {})
        props = set()
        
        for attr, keys in _iter_dict(_js_temp, []):
            if isinstance(attr, Attr):
                if attr.name is None:
                    attr_name = keys[-1]
                    if not isinstance(attr_name, str):
                        raise TypeError(
                            "Attr objects in a list need `name` argument."
                        )
                    attr.name = attr_name
                if not attr.mutability_given:
                    attr.mutable = _mutable
                
                if attr.annotation is None:
                    attr.annotation = _annot.get(attr.name)
                
            else:
                continue
            
            # check name collision
            if attr.name in props:
                raise ValueError(f"Name collision in attributes: {attr.name!r}.")
            props.add(attr.name)
            
            # convert into a json-property
            prop = attr.to_property(keys)
            namespace[attr.name] = prop
        
        jcls: JsonClassMeta = type.__new__(cls, name, bases, namespace, **kwds)
        jcls._json_properties = frozenset(props)
        
        return jcls


class JsonClass(metaclass=JsonClassMeta):
    """The base class of json class."""
    
    def __init__(self, d: dict[str, Any | None], /):
        if not isinstance(d, dict):
            raise TypeError(
                f"Input of {self.__class__.__name__} must be a dict, got {type(d)}"
            )
        self._json = d
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} object>"
    
    @property
    def json(self) -> dict[str, Any | None]:
        """Return the original json dictionary."""
        return self._json
    
    @classmethod
    def load(cls, path: str | Path | bytes, encoding: str | None = None):
        """Load a json file and create a json class from it."""
        with open(path, mode="r", encoding=encoding) as f:
            js = json.load(f)
        return cls(js)
    
    @classmethod
    def loads(cls, s: str | bytes):
        """Deserialize input string and create a json class from it."""
        js: dict[str, Any | None] = json.loads(s)
        return cls(js)

    def dump(self, path: str | Path | bytes, encoding: str | None = None) -> None:
        """Save json object in a file."""
        with open(path, mode="w", encoding=encoding) as f:
            json.dump(self.json, f)
        return None

    def attr_asdict(self) -> dict[str, Any | None]:
        """Summarize JsonClass properties into a dict."""
        return {
            name: getattr(self, name)
            for name in self.__class__._json_properties
        }

    def attr_astuple(self) -> tuple[Any | None, ...]:
        """Summarize JsonClass properties into a tuple."""
        return tuple(
            getattr(self, jprop_name) 
            for jprop_name in self.__class__._json_properties
        )