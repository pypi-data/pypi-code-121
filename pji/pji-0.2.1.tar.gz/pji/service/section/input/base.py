from abc import ABCMeta, abstractmethod
from typing import Optional

from pysyslimit import chown, chmod
from pysyslimit.models.permission.full import FileUserPermission, FilePermission, FileGroupPermission, FileOtherPermission

from ....control.model import Identification


def _load_privilege(privilege=None) -> Optional[FilePermission]:
    """
    load privilege information from data
    :param privilege: raw privilege data
    :return: privilege object or None
    """
    if privilege is not None:
        try:
            _privilege = FilePermission.loads(privilege)
        except (TypeError, ValueError):
            _privilege = FilePermission(
                FileUserPermission.loads(privilege),
                FileGroupPermission.loads('---'),
                FileOtherPermission.loads('---'),
            )
    else:
        _privilege = None

    return _privilege


def _apply_privilege_and_identification(filename: str, privilege=None, identification=None):
    """
    Apply privilege and identification for file
    :param filename: file path
    :param privilege: file privilege
    :param identification: file identification
    """
    if privilege is not None:
        chmod(filename, privilege, recursive=True)
    if identification is not None:
        _ident = Identification.merge(Identification.load_from_file(filename), identification)
        chown(filename, _ident.user, _ident.group, recursive=True)


class FileInputTemplate(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, *args, **kwargs) -> 'FileInput':
        raise NotImplementedError


class FileInput(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, **kwargs):
        raise NotImplementedError
