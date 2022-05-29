from __future__ import annotations
import json
from pathlib import Path
from typing import Callable, Literal, TypeVar, overload, Any
from ._json_class import JsonClass, _JSON_TEMPLATE, _JSON_MUTABLE
from ._json_attribute import JsonProperty

_C = TypeVar("_C")

@overload
def jsonclass(template_or_class: type[_C], template: dict[str, Any | None], mutable: bool = False) -> type[_C | JsonClass]:
    ...

@overload
def jsonclass(template_or_class: Literal[None], template: dict[str, Any | None], mutable: bool = False) -> Callable[[type[_C]], type[_C | JsonClass]]:
    ...
    
@overload
def jsonclass(template_or_class: dict[str, Any | None], template: Literal[None] = None, mutable: bool = False) -> Callable[[type[_C]], type[_C | JsonClass]]:
    ...

    
def jsonclass(template_or_class=None, template=None, mutable=False):
    """
    Create a json class with specified template.
    
    This decorator is an alternative of ``JsonClass`` inheritance. Generally this
    decorator will be used as following.
    
    >>> @jsonclass({...})
    >>> class C: ...
    
    >>> @jsonclass
    >>> class C: 
    >>>     __json_template__ = {...}

    Returns
    -------
    subclass of JsonClass
        An class that inherits the input class and ``JsonClass``.
    
    Excamples
    ---------
    >>> template = {..., {..., "xxx": "a"}}
    >>> @jsonclass(template)
    >>> class C:
    >>>     a: int
    >>> c = C()
    >>> c.a  # get some value
    """
    if isinstance(template_or_class, type):
        cls = template_or_class
    elif isinstance(template_or_class, dict):
        cls = None
        template = template_or_class
    elif template_or_class is None:
        cls = None
    else:
        raise TypeError
    
    def _func(cls_):
        nonlocal template, mutable
        template = getattr(cls, _JSON_TEMPLATE, template)
        mutable = getattr(cls, _JSON_MUTABLE, mutable)
        if not isinstance(template, dict):
            raise TypeError("`template` must be given as a dict.")
        ns = {_JSON_TEMPLATE: template, _JSON_MUTABLE: mutable}
        return type(cls_.__name__, (cls_, JsonClass), ns)
    
    return _func if cls is None else _func(cls)

class _dummy:
    """Dummy class for json class creation."""

def create_constructor(
    template: dict[str, Any | None],
    mutable: bool = False,
    name: str | None = None
) -> type[_dummy | JsonClass]:
    """
    Create a JsonClass in a simple way.
    
    Instead of defining a base class, this function uses a dummy class and create
    a constructor using a template dictionary only. As a result, typing of json
    properties will be lost.
    
    Parameters
    ----------
    template : dict
        JSON file template dictionary.
    mutable : bool, default is False
        Default mutability of properties.
    name : str, optional
        Name of the class. Automatically determined by default.
    
    Returns
    -------
    JsonClass subclass
        A class implemented with properties extracted from the template dictionary.
    
    See also
    --------
    :func:`create_loader`
    """
    cls = jsonclass(_dummy, template=template, mutable=mutable)
    if name is None:
        cls.__name__ = f"JsonClass{hex(id(cls))}"
    else:
        cls.__name__ = str(name)
    cls.__qualname__ = f"elegant_json.{cls.__name__}"
    cls.__module__ = "elegant_json"
    return cls

def create_loader(
    template: dict[str, Any | None],
    mutable: bool = False,
    name: str | None = None
):
    """
    Create a loader function in a simple way.
    
    Unlike :func:`create_constructor`, this function returns a loader function
    that takes file path as an input and returns a JsonClass object.
    
    Parameters
    ----------
    template : dict
        JSON file template dictionary.
    mutable : bool, default is False
        Default mutability of properties.
    name : str, optional
        Name of the class. Automatically determined by default.
    
    Returns
    -------
    Callable
        A loader function.
    
    See also
    --------
    :func:`create_constructor`
    """
    cls = create_constructor(template=template, mutable=mutable, name=name)
    # NOTE: simply this function can return `cls.load` but will not work if
    # new class has `load` property by chance.
    def load(path: str | Path | bytes, encoding: str | None = None):
        with open(path, mode="r", encoding=encoding) as f:
            js = json.load(f)
        return cls(js)  # type: ignore
    return load


def isformatted(obj, json_class: type[JsonClass]) -> bool:
    """
    Check if the input object is in ``json_class`` format.
    
    This function is free of error, as long as a ``JsonClass`` object is given as
    the second argument.
    """
    if not issubclass(json_class, JsonClass):
        raise TypeError("The second argument of `isformatted` must be a JsonClass.")
    if not isinstance(obj, dict):
        return False
    for name in json_class._json_properties:
        prop: JsonProperty = getattr(json_class, name)
        try:
            out: Any = obj
            for k in prop.keys():
                out = out[k]
        except (KeyError, IndexError):
            return False
    return True