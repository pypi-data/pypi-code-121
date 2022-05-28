import os
from abc import ABCMeta
from fnmatch import filter as fnfilter
from typing import Optional, Mapping, Union

from hbutils.model import get_repr_info
from hbutils.string import truncate

from ..base import _process_environ
from ...control.model import Identification, ResourceLimit


class _IGlobalConfig(metaclass=ABCMeta):
    def __init__(self, identification, resources, environ, use_sys_env):
        """
        :param identification: identification
        :param resources: resource limits
        :param environ: environment variable
        :param use_sys_env: use environment variables from local environ
        """
        self.__identification = identification
        self.__resources = resources
        self.__environ = environ
        self.__use_sys_env = use_sys_env

    def __repr__(self):
        """
        :return: get representation string
        """
        return get_repr_info(
            cls=self.__class__,
            args=[
                ('identification',
                 lambda: truncate(repr(self.__identification), width=48, show_length=True, tail_length=16),
                 lambda: self.__identification and self.__identification != Identification.loads({})),
                ('resources', lambda: truncate(repr(self.__resources), width=64, show_length=True, tail_length=16),
                 lambda: self.__resources and self.__resources != ResourceLimit.loads({})),
                ('environ',
                 lambda: truncate(repr(self.__environ), width=64, show_length=True, tail_length=16),
                 lambda: self.__environ),
                ('use_sys_env', lambda: truncate(repr(self.__use_sys_env), width=64, show_length=True, tail_length=16),
                 lambda: self.__use_sys_env is not None),
            ]
        )


def _process_use_sys_env(use_sys_env) -> Union[set, bool]:
    if isinstance(use_sys_env, (list, tuple, set)):
        return set(use_sys_env)
    elif isinstance(use_sys_env, bool) or use_sys_env is None:
        return not not use_sys_env
    else:
        raise TypeError(
            'Bool or list expected but {actual} found for use_sys_env.'.format(actual=repr(type(use_sys_env).__name__)))


def _load_local_environ(use_sys_env) -> Mapping[str, str]:
    use_sys_env = _process_use_sys_env(use_sys_env)
    _current_env = dict(os.environ)
    if isinstance(use_sys_env, set):
        _keys = set()
        for pattern in use_sys_env:
            _keys |= set(fnfilter(list(_current_env.keys()), pattern))
        return {key: value for key, value in _current_env.items() if key in _keys}
    else:
        return _current_env if use_sys_env else {}


class GlobalConfigTemplate(_IGlobalConfig):
    def __init__(self, identification=None, resources=None, environ=None, use_sys_env=None):
        """
        :param identification: identification
        :param resources: resource limits
        :param environ: environment variable
        :param use_sys_env: use environment variables from local environ
        """
        self.__identification = Identification.loads(identification)
        self.__resources = ResourceLimit.loads(resources)
        self.__environ = _process_environ(environ)
        self.__use_sys_env = _process_use_sys_env(use_sys_env)
        _IGlobalConfig.__init__(self, self.__identification, self.__resources, self.__environ, self.__use_sys_env)

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
    def use_sys_env(self) -> Union[set, bool]:
        return self.__use_sys_env

    def __call__(self, environ: Optional[Mapping[str, str]] = None,
                 environ_after: Optional[Mapping[str, str]] = None, **kwargs) -> 'GlobalConfig':
        """
        generate global config
        :param environ: environment variable
        :param environ_after:
        :param kwargs: other arguments
        :return: global config
        """
        _environ = _load_local_environ(self.__use_sys_env)
        _environ = _process_environ(environ, _environ, enable_ext=True)
        _environ = _process_environ(self.__environ, _environ, enable_ext=True)
        _environ = _process_environ(environ_after, _environ, enable_ext=True)

        return GlobalConfig(
            identification=self.__identification,
            resources=self.__resources, environ=_environ,
        )

    @classmethod
    def loads(cls, data) -> 'GlobalConfigTemplate':
        """
        load global config template from data
        :param data: raw data
        :return: global config template
        """
        data = data or {}
        if isinstance(data, cls):
            return data
        elif isinstance(data, dict):
            return cls(**data)
        else:
            raise TypeError('Json or {type} expected but {actual} found.'.format(
                type=cls.__name__, actual=repr(type(data).__name__)))


class GlobalConfig(_IGlobalConfig):
    def __init__(self, identification, resources, environ):
        """
        :param identification: identification
        :param resources: resource limits
        :param environ: environment variable
        """
        self.__identification = identification
        self.__resources = resources
        self.__environ = environ
        _IGlobalConfig.__init__(self, self.__identification, self.__resources, self.__environ, None)

    @property
    def identification(self) -> Identification:
        return self.__identification

    @property
    def resources(self) -> ResourceLimit:
        return self.__resources

    @property
    def environ(self) -> Mapping[str, str]:
        return self.__environ

    def __call__(self):
        """
        get global config information
        :return:
        """
        return self.__identification, self.__resources, self.__environ
