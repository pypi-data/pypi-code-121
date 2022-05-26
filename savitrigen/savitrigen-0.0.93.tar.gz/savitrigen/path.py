import pathlib
import contextlib
import logging
import typing
from shutil import copy
from string import Template
from multipledispatch import dispatch

class PathlibWrapper(object):
    def __init__(self):
        self.logger = logging.getLogger('path')
        self.parent_dir = None

    def _get_path(self, path) -> pathlib.Path:
        if isinstance(path, pathlib.Path):
            return path
        return pathlib.Path(path)

    @contextlib.contextmanager
    def change_dir(self, new_dir:str):
        previous_dir = self.parent_dir
        self.parent_dir = new_dir

        try:
            yield
        finally:
            self.parent_dir = previous_dir

    def make_dir(self, dirname:str) -> pathlib.Path:
        self.logger.info('MKDIR %s', dirname)
        path = self._get_path(dirname)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def copy_file(self, src:str, dest:str) -> pathlib.Path:
        res = copy(src, '{}/{}'.format(self.parent_dir, dest))
        return self._get_path(res)

    def _write_file(self, fname:str, content:str) -> pathlib.Path:
        self.logger.info('WRITE %s', fname)
        path = self._get_path(fname)
        path.write_bytes(content.encode())
        return path

    @dispatch(str, str)
    def write_file(self, *args, **kwargs) -> pathlib.Path:
        return self._write_file(*args, **kwargs)

    @dispatch(str, Template, dict)
    def write_file(self, fname:str, template:Template, replacements:dict) -> pathlib.Path:
        return self._write_file(fname, template.substitute(**replacements))

    @dispatch(str, Template, dict, dict)
    def write_file(self, fname:str, template:Template, fallback:dict, replacements:dict) -> pathlib.Path:
        return self._write_file(fname, template.substitute(fallback, **replacements))
