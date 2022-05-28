from typing import Optional, Mapping, Type

from .event import _load_dispatch_getter
from ..runner import DispatchRunner


def load_pji_script(script: str, runner_class: Optional[Type[DispatchRunner]] = None):
    """
    load pji script from script file
    :param script: script file or dir
    :param runner_class: runner class for executing
    :return: script getter (pass in environ and environ_after before use it)
    """
    _dispatch_getter = _load_dispatch_getter(script, runner_class)

    def _run_task(task_name: str,
                  environ: Optional[Mapping[str, str]] = None,
                  environ_after: Optional[Mapping[str, str]] = None):
        return _dispatch_getter(
            environ=environ,
            environ_after=environ_after,
        )(task_name)

    return _run_task
