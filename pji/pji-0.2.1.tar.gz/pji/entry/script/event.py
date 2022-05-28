from typing import Type, Optional, Callable

from ..event import _load_dispatch_getter as _load_dispatch_abstract_getter
from ..runner import DispatchRunner
from ...service import Dispatch


class _DefaultDispatchEventRunner(DispatchRunner):
    pass


def _load_dispatch_getter(filename: str = None, runner_class: Optional[Type[DispatchRunner]] = None) \
        -> Callable[..., Dispatch]:
    return _load_dispatch_abstract_getter(runner_class or _DefaultDispatchEventRunner, filename)
