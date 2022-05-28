from typing import Mapping, Optional, Callable, Any

from .base import _ITask
from ..section import SectionCollection
from ...control.model import Identification, ResourceLimit
from ...utils import wrap_empty


class Task(_ITask):
    def __init__(self, name: str, identification, resources, environ, sections):
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

        _ITask.__init__(self, self.__name, self.__identification, self.__resources, self.__environ, self.__sections)

    @property
    def name(self) -> str:
        return self.__name

    @property
    def identification(self) -> Identification:
        return self.__identification

    @property
    def resources(self) -> ResourceLimit:
        return self.__resources

    @property
    def environ(self) -> Mapping[str, str]:
        return self.__environ

    @property
    def sections(self) -> SectionCollection:
        return self.__sections

    def __call__(self, task_start: Optional[Callable[['Task'], None]] = None,
                 task_complete: Optional[Callable[['Task', Any], None]] = None,
                 **kwargs):
        """
        run this task
        :return: return value of this task
        """
        wrap_empty(task_start)(self)
        _return = self.__sections(**kwargs)
        wrap_empty(task_complete)(self, _return)
        return _return
