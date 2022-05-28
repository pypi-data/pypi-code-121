import os

from pysyslimit import FilePermission, SystemUser, SystemGroup, chmod, chown


def is_absolute_path(path: str) -> bool:
    """
    check if a path is absolute path
    :param path: path
    :return: True if it is an relative path
    """
    return os.path.isabs(path)


def is_relative_path(path: str) -> bool:
    """
    check if a path is relative path
    :param path: path
    :return: True if it is an relative path
    """
    return not os.path.isabs(path)


def is_inner_relative_path(path: str, allow_root: bool = True) -> bool:
    """
    check if a path is relative path
    :param path: path
    :param allow_root: allow path to be root path (.) it self
    :return: True if it is an relative path
    """
    if is_relative_path(path):
        segments = os.path.normpath(path).split(os.sep)
        if not allow_root and segments == ['.']:
            return False
        else:
            return segments[0] != '..'
    else:
        return False


def makedirs(path: str, privilege=None, user=None, group=None):
    """
    Quick make directories with privileges
    :param path: file path
    :param privilege: privileges, not set when none
    :param user: user, not set when none
    :param group: group, not set when none
    """
    path = os.path.normpath(path)
    privilege = FilePermission.loads(privilege) if privilege else None
    user = SystemUser.loads(user) if user else None
    group = SystemGroup.loads(group) if group else None

    if not os.path.exists(path):
        _upper_path, _file = os.path.split(path)
        if _file:
            makedirs(_upper_path or '.', privilege, user, group)
        else:  # this path is the root path, just like '/' or 'path'
            raise FileNotFoundError('Base dir {dir} not found.'.format(dir=repr(_upper_path or _file)))

        os.makedirs(path, exist_ok=True)
        if privilege:
            chmod(path, privilege)
        if user or group:
            chown(path, user, group)
    else:
        if not os.path.isdir(path):
            raise NotADirectoryError('File {file} is not a directory.'.format(file=repr(path)))
