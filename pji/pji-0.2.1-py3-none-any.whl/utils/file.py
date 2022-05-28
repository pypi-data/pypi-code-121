import os
import re
import shutil
import tempfile
from multiprocessing import Lock
from typing import Mapping, Optional

from pysyslimit import FilePermission, SystemUser, SystemGroup, chown, chmod

from .path import makedirs


def _auto_delete(filename: str):
    if os.path.isdir(filename):
        shutil.rmtree(filename, ignore_errors=True)
    else:
        os.remove(filename)


def _check_from_file(from_file: str):
    if not os.path.exists(from_file):
        raise FileNotFoundError('File {filename} not found.'.format(filename=repr(from_file)))
    if not os.access(from_file, os.R_OK):
        raise PermissionError('File {filename} unreadable.'.format(filename=repr(from_file)))


def _prepare_for_to_file(to_file: str, privilege=None, user=None, group=None):
    if os.path.exists(to_file):
        _auto_delete(to_file)
    _parent_path, _ = os.path.split(to_file)
    makedirs(_parent_path, privilege, user, group)


def auto_copy_file(from_file: str, to_file: str, privilege=None, user=None, group=None):
    privilege = FilePermission.loads(privilege) if privilege else None
    user = SystemUser.loads(user) if user else None
    group = SystemGroup.loads(group) if group else None

    _check_from_file(from_file)
    _prepare_for_to_file(to_file, privilege, user, group)
    if os.path.isdir(from_file):
        shutil.copytree(from_file, to_file)
    else:
        shutil.copyfile(from_file, to_file, follow_symlinks=True)

    if privilege:
        chmod(to_file, privilege, recursive=True)
    if user or group:
        chown(to_file, user, group, recursive=True)


def auto_link_file(from_file: str, to_file: str):
    _check_from_file(from_file)
    _prepare_for_to_file(to_file)
    os.symlink(from_file, to_file)


class FilePool:
    __FILE_NAME = 'file'
    __TAG_NAME_REGEXP = r'[a-zA-Z0-9_]+'

    def __init__(self, init: Optional[Mapping[str, str]] = None):
        self.__root_dir = tempfile.TemporaryDirectory()
        self.__file_dirs = {}

        self.__lock = Lock()
        self.__init_pool(init or {})

    def __init_pool(self, init: Mapping[str, str]):
        try:
            for tag, fdir in init.items():
                self.check_tag_name(tag)
                self.__create_tag_file(tag, fdir)
        except Exception as err:
            self.__close()
            raise err

    @classmethod
    def check_tag_name(cls, tag: str):
        if not re.fullmatch(cls.__TAG_NAME_REGEXP, tag):
            raise KeyError(
                'Tag name should only contains a-z, A-Z, 0-9 and _, but {actual} found.'.format(actual=repr(tag)))

    def __check_tag_exist(self, tag: str):
        if tag not in self.__file_dirs.keys():
            raise KeyError('Tag {tag} not exist.'.format(tag=repr(tag)))

    def __get_tag_file(self, tag: str) -> str:
        return os.path.join(self.__file_dirs[tag].name, self.__FILE_NAME)

    def __create_tag_file(self, tag: str, filename: str):
        self.__file_dirs[tag] = tempfile.TemporaryDirectory(dir=self.__root_dir.name)
        auto_copy_file(filename, self.__get_tag_file(tag))

    def __remove_tag_file(self, tag: str):
        self.__file_dirs[tag].cleanup()
        del self.__file_dirs[tag]

    def __export_tag_file(self, tag: str, filename: str, privilege=None, user=None, group=None):
        auto_copy_file(self.__get_tag_file(tag), filename, privilege, user, group)

    def __link_tag_file(self, tag: str, filename: str):
        auto_link_file(self.__get_tag_file(tag), filename)

    def __clear(self):
        try:
            for tag, fdir in self.__file_dirs.items():
                if os.path.exists(fdir.name):
                    fdir.cleanup()
        finally:
            for tag, fdir in list(self.__file_dirs.items()):
                if not os.path.exists(fdir.name):
                    del self.__file_dirs[tag]

    def __close(self):
        self.__clear()
        if os.path.exists(self.__root_dir.name):
            self.__root_dir.cleanup()

    def __getitem__(self, tag: str):
        with self.__lock:
            self.check_tag_name(tag)
            self.__check_tag_exist(tag)
            return self.__get_tag_file(tag)

    def __setitem__(self, tag, filename):
        with self.__lock:
            self.check_tag_name(tag)
            if tag in self.__file_dirs.keys():
                self.__remove_tag_file(tag)
            return self.__create_tag_file(tag, filename)

    def __delitem__(self, tag):
        with self.__lock:
            self.check_tag_name(tag)
            self.__check_tag_exist(tag)
            return self.__remove_tag_file(tag)

    def __contains__(self, tag):
        with self.__lock:
            return tag in self.__file_dirs

    def export(self, tag: str, filename: str, privilege=None, user=None, group=None):
        with self.__lock:
            return self.__export_tag_file(tag, filename, privilege, user, group)

    def link(self, tag: str, filename: str):
        with self.__lock:
            return self.__link_tag_file(tag, filename)

    def clear(self):
        with self.__lock:
            return self.__clear()

    def close(self):
        with self.__lock:
            return self.__close()

    def __enter__(self):
        with self.__lock:
            return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with self.__lock:
            self.__close()
