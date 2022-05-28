import codecs
import os
from functools import partial
from typing import Type, Callable

from .runner import DispatchRunner
from ..service import DispatchTemplate, Dispatch
from ..utils import auto_load_json

_DEFAULT_FILENAME = 'pscript.yml'


def _load_dispatch_template(filename: str) -> DispatchTemplate:
    with codecs.open(filename, 'r') as file:
        _json = auto_load_json(file)

    return DispatchTemplate.loads(_json)


def _load_dispatch_getter(runner_class: Type[DispatchRunner], filename: str = None) \
        -> Callable[..., Dispatch]:
    filename = filename or _DEFAULT_FILENAME
    if os.path.isdir(filename):
        filename = os.path.join(filename, _DEFAULT_FILENAME)

    _dir, _ = os.path.split(os.path.normpath(os.path.abspath(filename)))

    return partial(runner_class(_load_dispatch_template(filename)), scriptdir=_dir)
