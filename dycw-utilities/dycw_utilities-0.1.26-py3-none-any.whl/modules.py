from collections.abc import Callable
from collections.abc import Iterator
from importlib import import_module
from pkgutil import walk_packages
from types import ModuleType
from typing import Any
from typing import Optional
from typing import Union


def yield_modules(
    module: ModuleType, /, *, recursive: bool = False
) -> Iterator[ModuleType]:
    """Yield all the modules under a package. Optionally, recurse into
    sub-packages.
    """

    name = module.__name__
    try:
        path = module.__path__
    except AttributeError:
        yield module
    else:
        for info in walk_packages(path):
            imported = import_module(f"{name}.{info.name}")
            if (is_pkg := info.ispkg) and recursive:
                yield from yield_modules(imported, recursive=recursive)
            elif not is_pkg:
                yield imported


def yield_module_contents(
    module: ModuleType,
    /,
    *,
    recursive: bool = False,
    type: Optional[Union[type, tuple[type, ...]]] = None,
    predicate: Optional[Callable[[Any], bool]] = None,
) -> Iterator[Any]:
    """Yield all the modules under a package. Optionally, recurse into
    sub-packages.
    """

    for mod in yield_modules(module, recursive=recursive):
        for name in dir(mod):
            obj = getattr(mod, name)
            if ((type is None) or isinstance(obj, type)) and (
                (predicate is None) or predicate(obj)
            ):
                yield obj
