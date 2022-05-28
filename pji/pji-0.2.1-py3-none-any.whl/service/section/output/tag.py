import os
from abc import ABCMeta
from typing import Optional, Mapping, Callable

from hbutils.model import get_repr_info
from hbutils.string import env_template

from .base import FileOutputTemplate, FileOutput
from ...base import _check_workdir_file, _check_pool_tag, _process_environ
from ....utils import FilePool, wrap_empty


class _ITagFileOutput(metaclass=ABCMeta):
    def __init__(self, local: str, tag: str):
        """
        :param local: local path
        :param tag: pool tag
        """
        self.__local = local
        self.__tag = tag

    def __repr__(self):
        """
        :return: representation string
        """
        return get_repr_info(
            cls=self.__class__,
            args=[
                ('local', lambda: repr(self.__local)),
                ('tag', lambda: repr(self.__tag)),
            ]
        )


class TagFileOutputTemplate(FileOutputTemplate, _ITagFileOutput):
    def __init__(self, local: str, tag: str):
        """
        :param local: local path
        :param tag: pool tag
        """
        self.__local = local
        self.__tag = tag

        _ITagFileOutput.__init__(self, self.__local, self.__tag)

    @property
    def tag(self) -> str:
        return self.__tag

    @property
    def local(self) -> str:
        return self.__local

    def __call__(self, workdir: str, pool: FilePool,
                 environ: Optional[Mapping[str, str]] = None, **kwargs) -> 'TagFileOutput':
        """
        get tag file input object
        :param workdir: local work directory
        :param pool: file pool object
        :param environ: environment variables
        :return: tag file input object
        """
        environ = _process_environ(environ)
        _tag = _check_pool_tag(env_template(self.__tag, environ))
        _local = os.path.normpath(
            os.path.abspath(os.path.join(workdir, _check_workdir_file(env_template(self.__local, environ)))))

        return TagFileOutput(
            pool=pool, local=_local, tag=_tag,
        )


class TagFileOutput(FileOutput, _ITagFileOutput):
    def __init__(self, pool: FilePool, local: str, tag: str):
        """
        :param pool: file pool
        :param local: local path
        :param tag: pool tag
        """
        self.__pool = pool
        self.__local = local
        self.__tag = tag

        _ITagFileOutput.__init__(self, self.__local, self.__tag)

    @property
    def tag(self) -> str:
        return self.__tag

    @property
    def local(self) -> str:
        return self.__local

    def __call__(self, output_start: Optional[Callable[['TagFileOutput'], None]] = None,
                 output_complete: Optional[Callable[['TagFileOutput'], None]] = None, **kwargs):
        """
        execute this file output
        """
        wrap_empty(output_start)(self)
        self.__pool[self.__tag] = self.__local
        wrap_empty(output_complete)(self)
