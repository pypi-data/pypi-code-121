from abc import ABCMeta
from typing import List, Tuple, Optional, Callable

from hbutils.model import get_repr_info

from .base import ENV_PJI_COMMAND_INDEX
from .command import Command
from .template import CommandTemplate
from ..base import _process_environ
from ...control.model import RunResult
from ...utils import wrap_empty


class _ICommandCollection(metaclass=ABCMeta):
    def __init__(self, commands):
        """
        :param commands: commands
        """
        self.__commands = commands

    def __repr__(self):
        """
        :return: representation string
        """
        return get_repr_info(
            cls=self.__class__,
            args=[
                ('commands', lambda: len(self.__commands))
            ]
        )


class CommandCollectionTemplate(_ICommandCollection):
    def __init__(self, *commands: CommandTemplate):
        """
        :param commands: tuple of command templates
        """
        self.__commands = [CommandTemplate.loads(item) for item in commands]

        _ICommandCollection.__init__(self, self.__commands)

    @property
    def commands(self) -> List[CommandTemplate]:
        return list(self.__commands)

    def __call__(self, identification=None, resources=None, workdir=None, environ=None,
                 **kwargs) -> 'CommandCollection':
        """
        generate command collection
        :param identification: identification
        :param resources: resource limits
        :param workdir: work directory
        :param environ: environment variables
        :return: command collection
        """
        environ = _process_environ(environ)

        def _env_with_id(index_):
            _env = dict(environ)
            _env[ENV_PJI_COMMAND_INDEX] = str(index_)
            return _env

        return CommandCollection(*[item(
            identification, resources, workdir, _env_with_id(index), **kwargs
        ) for index, item in enumerate(self.__commands)])

    @classmethod
    def loads(cls, data) -> 'CommandCollectionTemplate':
        """
        load command collection template from data
        :param data: raw data
        :return: command collection template object
        """
        if isinstance(data, cls):
            return data
        elif isinstance(data, CommandTemplate):
            return cls(data)
        elif isinstance(data, (list, tuple)):
            return cls(*data)
        elif isinstance(data, dict):
            return cls(CommandTemplate.loads(data))
        else:
            raise TypeError('List or {type} expected but {actual} found.'.format(
                type=cls.__name__, actual=repr(type(data).__name__)))


_COLLECTION_RESULT = Tuple[bool, List[RunResult]]


class CommandCollection(_ICommandCollection):
    def __init__(self, *commands: Command):
        """
        :param commands: tuple of commands
        """
        self.__commands = commands

        _ICommandCollection.__init__(self, self.__commands)

    @property
    def commands(self) -> List[Command]:
        return list(self.__commands)

    def __call__(self, command_collection_start: Optional[Callable[['CommandCollection'], None]] = None,
                 command_collection_complete: Optional[
                     Callable[['CommandCollection', _COLLECTION_RESULT], None]] = None,
                 **kwargs) -> _COLLECTION_RESULT:
        """
        execute multiple commands one by one
        :return: success or not, list of results
        """
        wrap_empty(command_collection_start)(self)
        _results = []
        _success = True
        for index, cmd in enumerate(self.__commands):
            result = cmd(**kwargs)
            _results.append(result)
            if not result.ok:
                _success = False
                break

        _return = (_success, _results)
        wrap_empty(command_collection_complete)(self, _return)
        return _return
