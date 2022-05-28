import warnings
from typing import Mapping

from hbutils.string import env_template

from .base import _ITask, _check_task_name, ENV_PJI_TASK_NAME
from .task import Task
from ..base import _process_environ
from ..section import SectionCollectionTemplate
from ...control.model import Identification, ResourceLimit


class TaskTemplate(_ITask):
    def __init__(self, name: str, identification=None, resources=None, environ=None, sections=None):
        """
        :param name: name of task
        :param identification: identification
        :param resources: resource limit
        :param environ: environment variables
        :param sections: section templates
        """
        self.__name = name
        self.__identification = Identification.loads(identification)
        self.__resources = ResourceLimit.loads(resources)
        self.__environ = _process_environ(environ)
        self.__sections = SectionCollectionTemplate.loads(sections)

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
    def sections(self) -> SectionCollectionTemplate:
        return self.__sections

    def __call__(self, scriptdir: str, identification=None, resources=None, environ=None, **kwargs) -> 'Task':
        """
        generate task object
        :param scriptdir: script directory
        :param identification: identification
        :param resources: resource limit
        :param environ: environment variables
        :param kwargs: other arguments
        :return: task object
        """
        environ = dict(_process_environ(self.__environ, environ, enable_ext=True))
        _name = _check_task_name(env_template(self.__name, environ))
        environ[ENV_PJI_TASK_NAME] = _name

        _identification = Identification.merge(Identification.loads(identification), self.__identification)
        _resources = ResourceLimit.merge(ResourceLimit.loads(resources), self.__resources)

        return Task(
            name=_name,
            identification=_identification, resources=_resources, environ=environ,
            sections=self.__sections(
                scriptdir=scriptdir,
                identification=_identification,
                resources=_resources,
                environ=environ, **kwargs
            )
        )

    @classmethod
    def loads(cls, data) -> 'TaskTemplate':
        """
        load task template object from raw data
        :param data: raw data
        :return: task template object
        """
        if isinstance(data, cls):
            return data
        elif isinstance(data, dict):
            return cls(**data)
        elif isinstance(data, tuple):
            _name, _data = data
            if isinstance(_data, dict):
                if 'name' in _data:
                    warnings.warn(RuntimeWarning(
                        'Name found in {name} \'s second value, it will be ignored.'.format(name=repr(_name))))
                _data['name'] = _name
                return cls(**_data)
            else:
                raise TypeError('Second value of task tuple should be a dict but {actual} found.'.format(
                    actual=repr(type(_data).__name__)))
        else:
            raise TypeError('Json or {type} expected but {actual} found.'.format(
                type=cls.__name__, actual=repr(type(data).__name__)))
