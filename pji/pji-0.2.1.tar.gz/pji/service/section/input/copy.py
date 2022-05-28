import os
from abc import ABCMeta
from typing import Optional, Mapping, Callable

from hbutils.model import get_repr_info
from hbutils.string import env_template, truncate
from pysyslimit import FilePermission

from .base import FileInputTemplate, FileInput, _load_privilege, _apply_privilege_and_identification
from ...base import _check_os_path, _check_workdir_file, _process_environ
from ....control.model import Identification
from ....utils import auto_copy_file, wrap_empty


class _ICopyFileInput(metaclass=ABCMeta):
    def __init__(self, file: str, local: str, privilege, identification):
        """
        :param file: file path
        :param local: local path
        :param privilege: local privilege
        :param identification: local path identification
        """
        self.__file = file
        self.__local = local
        self.__privilege = privilege
        self.__identification = identification

    def __repr__(self):
        """
        :return: representation string
        """
        return get_repr_info(
            cls=self.__class__,
            args=[
                ('file', lambda: repr(self.__file)),
                ('local', lambda: repr(self.__local)),
                ('privilege', lambda: repr(self.__privilege.sign), lambda: self.__privilege is not None),
                ('identification',
                 lambda: truncate(repr(self.__identification), width=48, show_length=True, tail_length=16),
                 lambda: self.__identification and self.__identification != Identification.loads({})),
            ]
        )


class CopyFileInputTemplate(FileInputTemplate, _ICopyFileInput):
    def __init__(self, file: str, local: str, privilege=None, identification=None):
        """
        :param file: file path
        :param local: local path
        :param privilege: local path privilege
        :param identification: local path identification
        """
        self.__file = file
        self.__local = local
        self.__privilege = _load_privilege(privilege)
        self.__identification = Identification.loads(identification)

        _ICopyFileInput.__init__(self, self.__file, self.__local, self.__privilege, self.__identification)

    @property
    def file(self) -> str:
        return self.__file

    @property
    def local(self) -> str:
        return self.__local

    @property
    def privilege(self) -> Optional[FilePermission]:
        return self.__privilege

    # noinspection DuplicatedCode
    def __call__(self, scriptdir: str, workdir: str, identification=None,
                 environ: Optional[Mapping[str, str]] = None, **kwargs) -> 'CopyFileInput':
        """
        generate copy file input object from extension information
        :param scriptdir: script directory
        :param workdir: work directory
        :param identification: identification
        :param environ: environment variable
        :return: copy file input object
        """
        environ = _process_environ(environ)
        _file = os.path.normpath(
            os.path.abspath(os.path.join(scriptdir, _check_os_path(env_template(self.__file, environ)))))
        _local = os.path.normpath(
            os.path.abspath(os.path.join(workdir, _check_workdir_file(env_template(self.__local, environ)))))
        _identification = Identification.merge(Identification.loads(identification), self.__identification)

        return CopyFileInput(
            file=_file, local=_local,
            privilege=self.__privilege,
            identification=_identification,
        )


class CopyFileInput(FileInput, _ICopyFileInput):
    def __init__(self, file: str, local: str,
                 privilege: Optional[FilePermission],
                 identification: Optional[Identification]):
        """
        :param file: file path
        :param local: local path
        :param privilege: local path privilege
        :param identification: identification
        """
        self.__file = file
        self.__local = local
        self.__privilege = privilege
        self.__identification = identification

        _ICopyFileInput.__init__(self, self.__file, self.__local, self.__privilege, self.__identification)

    @property
    def file(self) -> str:
        return self.__file

    @property
    def local(self) -> str:
        return self.__local

    @property
    def privilege(self) -> Optional[FilePermission]:
        return self.__privilege

    def __call__(self, input_start: Optional[Callable[['CopyFileInput'], None]] = None,
                 input_complete: Optional[Callable[['CopyFileInput'], None]] = None, **kwargs):
        """
        execute this copy event
        """
        wrap_empty(input_start)(self)
        auto_copy_file(self.__file, self.__local, self.__privilege, self.__identification.user,
                       self.__identification.group)
        _apply_privilege_and_identification(self.__local, self.__privilege, self.__identification)
        wrap_empty(input_complete)(self)
