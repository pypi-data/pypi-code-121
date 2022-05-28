import codecs
import json
import tempfile
from typing import Mapping, Callable, Tuple, List, Any, Optional

from pysyslimit import chown, chmod

from .base import _ISection
from ..info import SectionInfoMapping
from ..input import FileInputCollection
from ..output import FileOutputCollection
from ...base import _process_environ
from ...command import CommandCollection
from ....control.model import Identification, ResourceLimit, RunResult
from ....utils import wrap_empty

_DEFAULT_WORKDIR = '.'
_SECTION_RESULT = Tuple[bool, List[RunResult], Mapping[str, Any]]


class Section(_ISection):
    def __init__(self, name: str,
                 commands_getter: Callable[..., CommandCollection],
                 identification: Identification, resources: ResourceLimit, environ,
                 inputs_getter: Callable[..., FileInputCollection],
                 outputs_getter: Callable[..., FileOutputCollection],
                 infos_getter: Callable[..., SectionInfoMapping],
                 info_dump: Optional[str]):
        """
        :param name: name of section
        :param commands_getter: command collection getter
        :param identification: identification
        :param resources: resource limits
        :param environ: environment variables
        :param inputs_getter: input collection getter
        :param outputs_getter: output collection getter
        :param infos_getter: information collection getter
        """
        self.__name = name
        self.__commands_getter = commands_getter

        self.__identification = identification
        self.__resources = resources
        self.__environ = _process_environ(environ)

        self.__inputs_getter = inputs_getter
        self.__outputs_getter = outputs_getter
        self.__infos_getter = infos_getter
        self.__info_dump = info_dump

        _ISection.__init__(self, self.__name, self.__identification,
                           self.__resources, self.__environ,
                           self.__inputs_getter(workdir=_DEFAULT_WORKDIR),
                           self.__outputs_getter(workdir=_DEFAULT_WORKDIR),
                           self.__infos_getter(workdir=_DEFAULT_WORKDIR),
                           self.__commands_getter(workdir=_DEFAULT_WORKDIR))

    @property
    def name(self) -> str:
        return self.__name

    @property
    def commands_getter(self) -> Callable[..., CommandCollection]:
        return self.__commands_getter

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
    def inputs_getter(self) -> Callable[..., FileInputCollection]:
        return self.__inputs_getter

    @property
    def outputs_getter(self) -> Callable[..., FileOutputCollection]:
        return self.__outputs_getter

    @property
    def infos_getter(self) -> Callable[..., SectionInfoMapping]:
        return self.__infos_getter

    @property
    def info_dump(self) -> Optional[str]:
        return self.__info_dump

    def __call__(self, section_start: Optional[Callable[['Section'], None]] = None,
                 section_complete: Optional[Callable[['Section', _SECTION_RESULT], None]] = None,
                 info_dump_start: Optional[Callable[['Section', Mapping[str, Any]], None]] = None,
                 info_dump_complete: Optional[Callable[['Section', Mapping[str, Any]], None]] = None,
                 **kwargs) -> _SECTION_RESULT:
        """
        run section
        :return: success or not, result list, information
        """
        wrap_empty(section_start)(self)
        with tempfile.TemporaryDirectory() as workdir:
            chmod(workdir, 'r-x------')
            if self.__identification:
                chown(workdir, user=self.__identification.user, group=self.__identification.group)

            self.__inputs_getter(workdir=workdir)(**kwargs)
            _success, _results = self.__commands_getter(workdir=workdir)(**kwargs)
            if _success:
                self.__outputs_getter(workdir=workdir)(**kwargs)
            _info = self.__infos_getter(workdir=workdir)(**kwargs)
            if self.__info_dump:
                wrap_empty(info_dump_start)(self, _info)
                with codecs.open(self.__info_dump, 'w') as cf:
                    json.dump(_info, cf, indent=4, sort_keys=True)
                wrap_empty(info_dump_complete)(self, _info)

            _return = (_success, _results, _info)

        wrap_empty(section_complete)(self, _return)
        return _return
