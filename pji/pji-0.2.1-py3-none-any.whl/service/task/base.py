import re
from abc import ABCMeta

from hbutils.model import get_repr_info
from hbutils.string import truncate

from ...control.model import Identification, ResourceLimit

_TASK_NAME_PATTERN = re.compile('[a-zA-Z_][a-zA-Z0-9_]*')


def _check_task_name(name: str) -> str:
    """
    check task name valid or not
    :param name: task name
    :return: task name
    """
    if _TASK_NAME_PATTERN.fullmatch(name):
        return name
    else:
        raise ValueError('Task name should match {pattern} but {actual} found.'.format(
            pattern=repr(_TASK_NAME_PATTERN.pattern),
            actual=repr(name),
        ))


ENV_PJI_TASK_NAME = 'PJI_TASK_NAME'


class _ITask(metaclass=ABCMeta):
    def __init__(self, name: str, identification=None, resources=None, environ=None, sections=None):
        """
        :param name: name of task
        :param identification: identification
        :param resources: resource limit
        :param environ: environment variables
        :param sections: sections
        """
        self.__name = name
        self.__identification = identification
        self.__resources = resources
        self.__environ = environ
        self.__sections = sections

    def __repr__(self):
        """
        :return: representation string
        """
        return get_repr_info(
            cls=self.__class__,
            args=[
                ('name', lambda: repr(self.__name)),
                ('identification',
                 lambda: truncate(repr(self.__identification), width=48, show_length=True, tail_length=16),
                 lambda: self.__identification and self.__identification != Identification.loads({})),
                ('resources', lambda: truncate(repr(self.__resources), width=64, show_length=True, tail_length=16),
                 lambda: self.__resources != ResourceLimit.loads({})),
                ('sections', lambda: truncate(repr(self.__sections), width=64, show_length=True, tail_length=16),
                 lambda: self.__sections),
            ]
        )
