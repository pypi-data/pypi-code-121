from abc import ABCMeta
from typing import Mapping

from hbutils.model import get_repr_info

from .task import Task
from .template import TaskTemplate
from ...utils import duplicates


class _ITaskMapping(metaclass=ABCMeta):
    def __init__(self, tasks):
        """
        :param tasks: tasks ot task templates
        """
        self.__tasks = tasks

    def __repr__(self):
        """
        :return: representation string
        """
        return get_repr_info(
            cls=self.__class__,
            args=[
                ('tasks', lambda: repr(tuple(self.__tasks.keys())))
            ]
        )


class TaskMappingTemplate(_ITaskMapping):
    def __init__(self, *tasks):
        _tasks = [TaskTemplate.loads(_item) for _item in (tasks or [])]
        _duplicated_names = duplicates([_item.name for _item in _tasks])
        if _duplicated_names:
            raise KeyError(
                'Duplicated name for task mapping - {names}'.format(names=repr(sorted(list(_duplicated_names)))))

        self.__tasks = {_task.name: _task for _task in _tasks}
        _ITaskMapping.__init__(self, self.__tasks)

    @property
    def items(self) -> Mapping[str, TaskTemplate]:
        return self.__tasks

    def __iter__(self):
        return self.items.__iter__()

    def __call__(self, scriptdir: str, identification=None, resources=None, environ=None, **kwargs) -> 'TaskMapping':
        _tasks = [_task(
            scriptdir=scriptdir,
            identification=identification,
            resources=resources,
            environ=environ,
        ) for _task in self.__tasks.values()]
        _duplicated_names = duplicates([_item.name for _item in _tasks])
        if _duplicated_names:
            raise KeyError(
                'Duplicated name for task mapping - {names}'.format(names=repr(sorted(list(_duplicated_names)))))

        return TaskMapping(*_tasks)

    @classmethod
    def loads(cls, data) -> 'TaskMappingTemplate':
        if isinstance(data, cls):
            return data
        elif isinstance(data, dict):
            return cls(*[TaskTemplate.loads((_name, _value)) for _name, _value in data.items()])
        elif isinstance(data, (list, tuple)):
            return cls(*data)
        elif isinstance(data, TaskTemplate):
            return cls(data)
        else:
            raise TypeError('Json, array or {type} expected but {actual} found.'.format(
                type=cls.__name__, actual=repr(type(data).__name__)))


class TaskMapping(_ITaskMapping):
    def __init__(self, *tasks: Task):
        self.__tasks = {_task.name: _task for _task in tasks}
        _ITaskMapping.__init__(self, self.__tasks)

    @property
    def items(self) -> Mapping[str, Task]:
        return self.__tasks

    def __iter__(self):
        return self.items.__iter__()

    def __call__(self, task_name: str, **kwargs):
        if task_name not in self.__tasks.keys():
            raise KeyError('Task {task} not found.'.format(task=repr(task_name)))
        return self.__tasks[task_name](**kwargs)
