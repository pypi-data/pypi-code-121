import codecs
import os
import warnings
from abc import ABCMeta
from typing import Optional, Mapping, Tuple

from hbutils.model import get_repr_info
from hbutils.string import env_template

from .base import SectionInfoTemplate, SectionInfo
from ...base import _check_pool_tag, _check_workdir_file, _process_environ
from ....utils import FilePool


class _ITagSectionInfo(metaclass=ABCMeta):
    def __init__(self, tag: str, file: Optional[str]):
        """        
        :param tag: file pool tag 
        :param file: sub file of dir
        """
        self.__tag = tag
        self.__file = file

    def __repr__(self):
        """
        :return: representation string 
        """
        return get_repr_info(
            cls=self.__class__,
            args=[
                ('tag', lambda: repr(self.__tag)),
                ('file', lambda: repr(self.__file), lambda: self.__file is not None)
            ]
        )


class TagSectionInfoTemplate(SectionInfoTemplate, _ITagSectionInfo):
    def __init__(self, tag: str, file: Optional[str] = None):
        """        
        :param tag: file pool tag 
        :param file: sub file of dir
        """
        self.__tag = tag
        self.__file = file

        _ITagSectionInfo.__init__(self, self.__tag, self.__file)

    @property
    def tag(self) -> str:
        return self.__tag

    @property
    def file(self) -> str:
        return self.__file

    def __call__(self, pool: FilePool, environ: Optional[Mapping[str, str]] = None, **kwargs) -> 'TagSectionInfo':
        """
        get tag info info object
        :param pool: file pool object
        :param environ: environment variables
        :return: tag info info object
        """
        environ = _process_environ(environ)
        _tag = _check_pool_tag(env_template(self.__tag, environ))
        if self.__file is not None:
            _file = os.path.normpath(_check_workdir_file(env_template(self.__file, environ)))
        else:
            _file = None

        return TagSectionInfo(pool=pool, tag=_tag, file=_file)


class TagSectionInfo(SectionInfo, _ITagSectionInfo):
    def __init__(self, pool: FilePool, tag: str, file: Optional[str] = None):
        """
        :param pool: file pool
        :param tag: file pool tag 
        :param file: sub file of dir
        """
        self.__pool = pool
        self.__tag = tag
        self.__file = file

        _ITagSectionInfo.__init__(self, self.__tag, self.__file)

    @property
    def tag(self) -> str:
        return self.__tag

    @property
    def file(self) -> str:
        return self.__file

    def __call__(self, **kwargs) -> Tuple[bool, Optional[str]]:
        """
        execute this info info
        """

        def _result_func():
            _tagged_file = self.__pool[self.__tag]
            if os.path.isdir(_tagged_file):
                if self.__file is None:
                    raise RuntimeError('Tag {tag} represent a dir but file is empty.'.format(tag=repr(self.__tag)))
                else:
                    _output_file = os.path.join(_tagged_file, self.__file)
            else:
                if self.__file is not None:
                    warnings.warn(RuntimeWarning(
                        'Tag {tag} represent a file, {file} data item will be ignored.'.format(tag=repr(self.__tag),
                                                                                               file=repr('file'))))
                _output_file = _tagged_file

            with codecs.open(_output_file, 'r') as f:
                return f.read()

        try:
            return True, _result_func()
        except (KeyError, RuntimeError):
            return False, None
