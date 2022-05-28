import re
from abc import ABCMeta

from hbutils.model import get_repr_info
from hbutils.string import truncate

from ....control.model import Identification, ResourceLimit

_SECTION_NAME_PATTERN = re.compile('[a-zA-Z_][0-9a-zA-Z_]*')


def _check_section_name(name: str) -> str:
    """
    check section name valid or not
    :param name: section name
    :return: section name
    """
    if _SECTION_NAME_PATTERN.fullmatch(name):
        return name
    else:
        raise ValueError('Section name should match {pattern} but {actual} found.'.format(
            pattern=repr(_SECTION_NAME_PATTERN.pattern),
            actual=repr(name),
        ))


ENV_PJI_SECTION_NAME = 'PJI_SECTION_NAME'


class _ISection(metaclass=ABCMeta):
    def __init__(self, name: str, identification, resources, environ,
                 inputs, outputs, infos, commands):
        """
        :param name: name of section
        :param identification: identification used
        :param resources: resource limits
        :param environ: environment variables
        :param inputs: inputs
        :param outputs: outputs
        :param infos: infos
        :param commands: commands
        """
        self.__name = name
        self.__identification = identification
        self.__resources = resources
        self.__environ = environ

        self.__inputs = inputs
        self.__outputs = outputs
        self.__infos = infos
        self.__commands = commands

    def __repr__(self):
        """
        :return: get representation string
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
                ('inputs', lambda: repr(len(self.__inputs.items)),
                 lambda: self.__inputs and len(self.__inputs.items) > 0),
                ('outputs', lambda: repr(len(self.__outputs.items)),
                 lambda: self.__outputs and len(self.__outputs.items) > 0),
                ('infos', lambda: repr(len(self.__infos.items)),
                 lambda: self.__infos and len(self.__infos.items.keys()) > 0),
                ('commands', lambda: repr(len(self.__commands.commands)),
                 lambda: self.__commands and len(self.__commands.commands) > 0),
            ]
        )
