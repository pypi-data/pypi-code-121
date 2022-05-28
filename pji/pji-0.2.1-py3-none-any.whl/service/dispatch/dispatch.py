import os
from abc import ABCMeta
from typing import Optional, Mapping

from hbutils.model import get_repr_info
from hbutils.string import truncate

from .global_ import GlobalConfigTemplate, GlobalConfig
from ..task import TaskMappingTemplate, TaskMapping


class _IDispatch(metaclass=ABCMeta):
    def __init__(self, global_, tasks):
        """
        :param global_: global config
        :param tasks: task mapping
        """
        self.__global = global_
        self.__tasks = tasks

    def __repr__(self):
        """
        :return: representation string
        """
        return get_repr_info(
            cls=self.__class__,
            args=[
                ('tasks', lambda: truncate(repr(tuple(sorted(self.__tasks.items.keys()))),
                                           width=64, show_length=True, tail_length=16),
                 lambda: self.__tasks),
            ]
        )


_KEY_MAPPING = {'global': 'global_'}


class DispatchTemplate(_IDispatch):
    def __init__(self, tasks, global_=None):
        """
        :param global_: global config template
        :param tasks: task mapping template
        """
        self.__global = GlobalConfigTemplate.loads(global_ or {})
        self.__tasks = TaskMappingTemplate.loads(tasks)
        _IDispatch.__init__(self, self.__global, self.__tasks)

    @property
    def global_(self) -> GlobalConfigTemplate:
        return self.__global

    @property
    def tasks(self) -> TaskMappingTemplate:
        return self.__tasks

    def __call__(self, scriptdir: str = None, environ: Optional[Mapping[str, str]] = None,
                 environ_after: Optional[Mapping[str, str]] = None, **kwargs):
        """
        generate dispatch object
        :param scriptdir: script directory (default is '.')
        :param environ: environment variable
        :param environ_after: force replace environment variable
        :param kwargs: other arguments
        :return: dispatch object
        """
        scriptdir = scriptdir or os.path.abspath(os.curdir)

        _global = self.__global(environ, environ_after, **kwargs)
        _tasks = self.__tasks(
            scriptdir=scriptdir,
            identification=_global.identification,
            resources=_global.resources,
            environ=_global.environ, **kwargs
        )

        return Dispatch(global_=_global, tasks=_tasks)

    @classmethod
    def loads(cls, data) -> 'DispatchTemplate':
        if isinstance(data, cls):
            return data
        elif isinstance(data, dict):
            return cls(**{_KEY_MAPPING.get(key, key): value for key, value in data.items()})
        else:
            raise TypeError('Json or {type} expected but {actual} found.'.format(
                type=cls.__name__, actual=repr(type(data).__name__)))


class Dispatch(_IDispatch):
    def __init__(self, global_, tasks):
        """
        :param global_: global config
        :param tasks: task mapping
        """
        self.__global = global_
        self.__tasks = tasks
        _IDispatch.__init__(self, self.__global, self.__tasks)

    @property
    def global_(self) -> GlobalConfig:
        return self.__global

    @property
    def tasks(self) -> TaskMapping:
        return self.__tasks

    def __call__(self, task_name: str, **kwargs):
        """
        run a task
        :param task_name: name of a task
        :return: result of task
        """
        return self.__tasks(task_name, **kwargs)
