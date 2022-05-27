import hashlib

import backoff
import requests


class UrlIO:
    def __init__(self, cache_files: bool = True):
        self.routes = {}
        self.cache_files = cache_files

    @backoff.on_exception(backoff.expo, requests.HTTPError, max_tries=5)
    def read(self, path, **kwargs):
        return requests.get(path, **kwargs).content

    def write(self, path, content):
        raise PermissionError("Cannot write data with UrlIO")

    def copy(self, src, dst, *args, **kwargs):
        raise PermissionError("Cannot copy data with UrlIO")

    def remove(self, path):
        raise PermissionError("Cannot delete data with UrlIO")

    def move(self, src, dst, *args, **kwargs):
        raise PermissionError("Cannot move data with UrlIO")

    def make_dirs(self, path, exist_ok=True):
        pass

    def isfile(self, path):
        raise PermissionError("Cannot move check if file with UrlIO")

    def stat_object(self, path):
        raise PermissionError("Cannot stat_object data with UrlIO")

    def walk(self, path, prefix=None, recursive=True, include_object=False, exclude_hidden=False, **kwargs):
        raise PermissionError("Cannot walk data with UrlIO")

    def get_md5(self, path):
        return self.calculate_md5(path)

    def calculate_md5(self, path):
        digest = hashlib.md5(self.read(path)).hexdigest()
        return digest
