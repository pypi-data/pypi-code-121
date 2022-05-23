# coding=utf-8
from __future__ import absolute_import, division, print_function

import os

from suanpan import g
from suanpan import path as spath
from suanpan import runtime
from suanpan.log import logger
from suanpan.storage import base
from suanpan.utils import pbar as spbar


class Storage(base.Storage):
    def __init__(
        self,
        localTempStore=base.Storage.DEFAULT_TEMP_DATA_STORE,
        localGlobalStore=base.Storage.DEFAULT_GLOBAL_DATA_STORE,
        **kwargs,
    ):
        super().__init__(
            delimiter=os.sep,
            tempStore=localTempStore,
            globalStore=localGlobalStore,
            **kwargs,
        )

    def download(
        self, key, path=None, progress=None, quiet=not g.debug
    ):  # pylint: disable=unused-argument
        url = self.storageUrl(key)
        tmppath = self.getPathInTempStore(key)
        path = path or tmppath

        if not quiet:
            logger.debug(f"Downloading: {url} -> {path}")

        with spbar.one(
            total=1, disable=quiet, desc="Downloading", progress=progress,
        ) as pbar:
            if path == tmppath:
                pbar.update(1)
                pbar.set_description("Nothing to do")
            else:
                spath.copy(tmppath, path)
                pbar.update(1)
                pbar.set_description("Downloaded")
            return path

    def upload(
        self, key, path=None, progress=None, quiet=not g.debug
    ):  # pylint: disable=unused-argument
        url = self.storageUrl(key)
        tmppath = self.getPathInTempStore(key)
        path = path or tmppath

        if not quiet:
            logger.debug(f"Uploading: {path} -> {url}")

        with spbar.one(
            total=1, disable=quiet, desc="Uploading", progress=progress,
        ) as pbar:
            if path == tmppath:
                pbar.update(1)
                pbar.set_description("Nothing to do")
            else:
                spath.copy(path, tmppath)
                pbar.update(1)
                pbar.set_description("Uploaded")
            return path

    def copy(
        self, src, dist, progress=None, quiet=not g.debug
    ):  # pylint: disable=unused-argument
        srcurl = self.storageUrl(src)
        disturl = self.storageUrl(dist)
        srcpath = self.getPathInTempStore(src)
        distpath = self.getPathInTempStore(dist)

        if not quiet:
            logger.debug(f"Copying: {srcurl} -> {disturl}")

        with spbar.one(
            total=1, disable=quiet, desc="Copying", progress=progress,
        ) as pbar:
            spath.copy(srcpath, distpath)
            pbar.update(1)
            pbar.set_description("Copied")
            return dist

    def remove(
        self, key, progress=None, quiet=not g.debug
    ):  # pylint: disable=unused-argument
        url = self.storageUrl(key)
        path = self.getPathInTempStore(key)

        if not quiet:
            logger.debug(f"Removing: {url}")

        with spbar.one(
            total=1, disable=quiet, desc="Removing", progress=progress,
        ) as pbar:
            spath.remove(path)
            pbar.update(1)
            pbar.set_description("Removed")
            return key

    def walk(self, key):
        path = self.getPathInTempStore(key)
        for root, folders, files in runtime.saferun(os.walk, default=iter(()))(path):
            root = self.completePath(spath.replaceBasePath(path, key, root)[0])
            folders = [self.storagePathJoin(root, folder) for folder in folders]
            files = [self.storagePathJoin(root, file) for file in files]
            yield root, folders, files

    def listAll(self, key):
        path = self.getPathInTempStore(key)
        return (self.storagePathJoin(key, item) for item in os.listdir(path))

    def listFolders(self, key):
        return (item for item in self.listAll(key) if self.isFolder(item))

    def listFiles(self, key):
        return (item for item in self.listAll(key) if self.isFile(item))

    def isFolder(self, key):
        folder = self.getPathInTempStore(key)
        return os.path.isdir(folder)

    def isFile(self, key):
        file = self.getPathInTempStore(key)
        return os.path.isfile(file)

    def storagePathJoin(self, *paths):
        return self.localPathJoin(*paths)

    def storageRelativePath(self, path, basepath):
        return self.localRelativePath(path, basepath)

    def storageUrl(self, key):
        return "file://" + self.getPathInTempStore(key)

    def getStorageMd5(self, key):
        return self.getLocalMd5(self.getPathInTempStore(key))

    def getStorageSize(self, key):
        return self.getLocalSize(self.getPathInTempStore(key))
