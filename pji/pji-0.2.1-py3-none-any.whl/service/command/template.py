import os
from typing import Union, List, Optional

from hbutils.string import env_template

from .base import _ICommandBase, CommandMode
from .command import Command
from ..base import _check_workdir_position, _process_environ
from ...control.model import ResourceLimit, Identification


class CommandTemplate(_ICommandBase):
    __DEFAULT_WORKDIR = '.'
    __DEFAULT_MODE = CommandMode.COMMON

    def __init__(self, args: Union[str, List[str]], shell: bool = True,
                 workdir: Optional[str] = None, resources=None,
                 mode=None, stdin=None, stdout=None, stderr=None, **kwargs):
        """
        :param args: arguments
        :param shell: use shell mode
        :param workdir: work directory
        :param resources: resource limits
        :param mode: command mode value
        :param stdin: stdin file
        :param stdout: stdout file
        :param stderr: stderr file
        """
        if not isinstance(args, (str, list)):
            raise TypeError('Args should be str or list but {actual} found.'.format(actual=repr(type(args).__name__)))
        if shell and not isinstance(args, str):
            raise ValueError(
                'Args should be string when shell is true but {actual} found.'.format(actual=repr(type(args).__name__)))
        self.__args = args
        self.__shell = shell

        self.__workdir = str(workdir or self.__DEFAULT_WORKDIR)
        self.__resources = ResourceLimit.loads(resources or {})

        self.__mode = CommandMode.loads(mode or self.__DEFAULT_MODE)
        self.__stdin = stdin
        self.__stdout = stdout
        self.__stderr = stderr

        self.__kwargs = kwargs
        _ICommandBase.__init__(self, self.__args, self.__shell, self.__workdir,
                               None, self.__resources, self.__mode, **self.__kwargs)

    @property
    def args(self) -> Union[str, List[str]]:
        return self.__args

    @property
    def shell(self) -> bool:
        return self.__shell

    @property
    def workdir(self) -> str:
        return self.__workdir

    @property
    def resources(self) -> ResourceLimit:
        return self.__resources

    @property
    def mode(self) -> CommandMode:
        return self.__mode

    @property
    def stdin(self):
        return self.__stdin

    @property
    def stdout(self):
        return self.__stdout

    @property
    def stderr(self):
        return self.__stderr

    def __tuple(self):
        return self.__args, self.__shell, self.__workdir, self.__resources, \
               self.__mode, self.__stdin, self.__stdout, self.__stdout

    def __eq__(self, other):
        """
        check equality
        :param other: another command template object
        :return:
        """
        if other is self:
            return True
        elif isinstance(other, self.__class__):
            return self.__tuple() == other.__tuple()
        else:
            return False

    def __hash__(self):
        """
        get hash value of object
        :return: hash value
        """
        return hash(self.__tuple())

    def __call__(self, identification=None, resources=None, workdir=None, environ=None, **kwargs) -> Command:
        """
        get command object from template
        :param identification: identification
        :param resources: resource limits
        :param workdir: work directory
        :param environ: environment variables
        :return: command object
        """
        environ = _process_environ(environ)
        _identification = Identification.loads(identification or {})
        _resources = ResourceLimit.merge(ResourceLimit.loads(resources or {}), self.__resources)
        _workdir = os.path.normpath(
            os.path.join(workdir or '.', _check_workdir_position(env_template(self.__workdir, environ))))
        _stdin = os.path.normpath(os.path.join(_workdir, env_template(self.__stdin, environ))) \
            if isinstance(self.__stdin, str) else self.__stdin
        _stdout = os.path.normpath(os.path.join(_workdir, env_template(self.__stdout, environ))) \
            if isinstance(self.__stdout, str) else self.__stdout
        _stderr = os.path.normpath(os.path.join(_workdir, env_template(self.__stderr, environ))) \
            if isinstance(self.__stderr, str) else self.__stderr

        return Command(
            args=self.__args, shell=self.__shell,
            workdir=_workdir, environ=environ,
            identification=_identification, resources=_resources,
            mode=self.__mode, stdin=_stdin, stdout=_stdout, stderr=_stderr,
            **{
                key: env_template(value, environ) if isinstance(value, str) else value
                for key, value in self.__kwargs.items()
            }
        )

    @classmethod
    def loads(cls, data) -> 'CommandTemplate':
        """
        load command template from data
        :param data: raw data
        :return: command template object
        """
        if isinstance(data, cls):
            return data
        elif isinstance(data, dict):
            return cls(**data)
        elif isinstance(data, str):
            return cls(args=data)
        elif isinstance(data, (list, tuple)):
            return cls(args=list(data), shell=False)
        else:
            raise TypeError('Json or {type} expected but {actual} found.'.format(
                type=cls.__name__, actual=repr(type(data).__name__)))
