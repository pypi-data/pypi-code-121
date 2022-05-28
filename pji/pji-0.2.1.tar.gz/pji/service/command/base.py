import os
from enum import unique, IntEnum
from typing import Union, List, Optional

from hbutils.model import get_repr_info
from hbutils.string import truncate

from ...control.model import ResourceLimit, Identification


@unique
class CommandMode(IntEnum):
    COMMON = 1
    TIMING = 2
    MUTUAL = 3

    @classmethod
    def loads(cls, value) -> 'CommandMode':
        """
        Load CommandMode from value
        :param value: raw value
        :return: CommandMode object
        """
        if isinstance(value, cls):
            return value
        elif isinstance(value, str):
            if value.upper() in cls.__members__.keys():
                return cls.__members__[value.upper()]
            else:
                raise KeyError('Unknown command mode - {actual}.'.format(actual=repr(value)))
        elif isinstance(value, int):
            _mapping = {v.value: v for k, v in cls.__members__.items()}
            if value in _mapping.keys():
                return _mapping[value]
            else:
                raise ValueError('Unknown command mode value - {actual}'.format(actual=repr(value)))
        else:
            raise TypeError('Int, str or {cls} expected but {actual} found.'.format(
                cls=cls.__name__,
                actual=repr(type(value).__name__)
            ))


ENV_PJI_COMMAND_INDEX = 'PJI_COMMAND_INDEX'


class _ICommandBase:
    def __init__(self, args: Union[str, List[str]], shell: bool = True, workdir: Optional[str] = None,
                 identification=None, resources=None, mode=None, **kwargs):
        """
        :param args: arguments
        :param shell: use shell mode
        :param workdir: work directory
        :param identification: identification used
        :param resources: resource limits
        :param mode: command mode value
        """
        self.__args = args
        self.__shell = shell
        self.__workdir = workdir
        self.__identification = identification
        self.__resources = resources
        self.__mode = mode
        self.__kwargs = kwargs

    def __repr__(self):
        """
        :return: get representation string
        """
        return get_repr_info(
            cls=self.__class__,
            args=[
                ('args', lambda: truncate(repr(self.__args), width=48, show_length=True, tail_length=16)),
                ('shell', lambda: repr(self.__shell)),
                ('mode', lambda: self.__mode.name),
                ('workdir', lambda: repr(self.__workdir),
                 lambda: os.path.normpath(self.__workdir) != os.path.normpath('.')),
                ('identification',
                 lambda: truncate(repr(self.__identification), width=48, show_length=True, tail_length=16),
                 lambda: self.__identification and self.__identification != Identification.loads({})),
                ('resources', lambda: truncate(repr(self.__resources), width=64, show_length=True, tail_length=16),
                 lambda: self.__resources and self.__resources != ResourceLimit.loads({})),
                *[(key, lambda: repr(value)) for key, value in self.__kwargs.items()]
            ]
        )
