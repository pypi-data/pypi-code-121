import os
from functools import partial
from typing import Mapping, Optional

from hbutils.string import env_template

from .base import _ISection, _check_section_name, ENV_PJI_SECTION_NAME
from .section import Section
from ..info import SectionInfoMappingTemplate
from ..input import FileInputCollectionTemplate
from ..output import FileOutputCollectionTemplate
from ...base import _process_environ, _check_os_path
from ...command import CommandCollectionTemplate
from ....control.model import Identification, ResourceLimit
from ....utils import FilePool


class SectionTemplate(_ISection):
    def __init__(self, name: str, commands,
                 identification=None, resources=None, environ=None,
                 inputs=None, outputs=None, infos=None, info_dump=None):
        """
        :param name: section name
        :param commands: commands
        :param identification: identification
        :param resources: resource limits
        :param environ: environment variables (${ENV} supported)
        :param inputs: input collection template
        :param outputs: output collection template
        :param infos: information collection template
        :param info_dump: information result dump
        """
        self.__name = name
        self.__commands = CommandCollectionTemplate.loads(commands)

        self.__identification = Identification.loads(identification)
        self.__resources = ResourceLimit.loads(resources)
        self.__environ = _process_environ(environ)

        self.__inputs = FileInputCollectionTemplate.loads(inputs)
        self.__outputs = FileOutputCollectionTemplate.loads(outputs)
        self.__infos = SectionInfoMappingTemplate.loads(infos)
        self.__info_dump = info_dump

        _ISection.__init__(self, self.__name, self.__identification, self.__resources,
                           self.__environ, self.__inputs, self.__outputs, self.__infos, self.__commands)

    @property
    def name(self) -> str:
        return self.__name

    @property
    def commands(self) -> CommandCollectionTemplate:
        return self.__commands

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
    def inputs(self) -> FileInputCollectionTemplate:
        return self.__inputs

    @property
    def outputs(self) -> FileOutputCollectionTemplate:
        return self.__outputs

    @property
    def infos(self) -> SectionInfoMappingTemplate:
        return self.__infos

    @property
    def info_dump(self) -> str:
        return self.__info_dump

    def __call__(self, scriptdir: str, pool: Optional[FilePool] = None,
                 identification=None, resources=None, environ=None, **kwargs) -> Section:
        """
        generate section object
        :param scriptdir: script directory
        :param pool: file pool
        :param identification: identification
        :param resources: resource limits
        :param environ: environment variables
        :param kwargs: any other arguments
        :return: section object
        """
        if 'workdir' in kwargs.keys():
            raise KeyError('Workdir is not allowed to pass into section template.')

        environ = dict(_process_environ(self.__environ, environ, enable_ext=True))
        _name = _check_section_name(env_template(self.__name, environ))
        environ[ENV_PJI_SECTION_NAME] = _name

        _identification = Identification.merge(Identification.loads(identification), self.__identification)
        _resources = ResourceLimit.merge(ResourceLimit.loads(resources), self.__resources)
        _info_dump = os.path.normpath(
            os.path.abspath(os.path.join(scriptdir, _check_os_path(
                env_template(self.__info_dump, environ))))) if self.__info_dump else None

        arguments = dict(kwargs)
        arguments.update(
            scriptdir=scriptdir,
            pool=pool,
            environ=environ,
            identification=_identification,
            resources=_resources,
        )

        return Section(
            name=_name,
            identification=_identification, resources=_resources, environ=environ,
            commands_getter=partial(self.__commands, **arguments),
            inputs_getter=partial(self.__inputs, **arguments),
            outputs_getter=partial(self.__outputs, **arguments),
            infos_getter=partial(self.__infos, **arguments),
            info_dump=_info_dump,
        )

    @classmethod
    def loads(cls, data) -> 'SectionTemplate':
        """
        load section template from data
        :param data: raw data
        :return: section template object
        """
        if isinstance(data, cls):
            return data
        elif isinstance(data, dict):
            return cls(**data)
        else:
            raise TypeError('Json or {type} expected but {actual} found.'.format(
                type=cls.__name__, actual=repr(type(data).__name__)))
