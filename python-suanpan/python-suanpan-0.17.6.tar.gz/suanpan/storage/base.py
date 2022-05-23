# coding=utf-8
from __future__ import absolute_import, print_function

import abc
import os
import tempfile
import zipfile
import pathlib

from suanpan import g
from suanpan import path as spath
from suanpan.log import logger
from suanpan.objects import HasName
from suanpan.utils import functional


class Storage(HasName):
    __metaclass__ = abc.ABCMeta

    DEFAULT_TEMP_DATA_STORE = tempfile.gettempdir()
    DEFAULT_GLOBAL_DATA_STORE = "/global"
    DEFAULT_IGNORE_KEYWORDS = ("__MACOSX", ".DS_Store")
    CONTENT_MD5 = "Content-MD5"
    PBAR_FORMAT = "{l_bar}{bar}"

    def __init__(
        self,
        delimiter=os.sep,
        tempStore=DEFAULT_TEMP_DATA_STORE,
        globalStore=DEFAULT_GLOBAL_DATA_STORE,
        **kwargs,
    ):  # pylint: disable=unused-argument
        self.delimiter = delimiter
        self.tempStore = tempStore
        self.globalStore = globalStore

    @abc.abstractmethod
    def download(self, name, path, progress=None, **kwargs):
        pass

    @abc.abstractmethod
    def upload(self, name, path, progress=None, **kwargs):
        pass

    @abc.abstractmethod
    def copy(self, name, dist, progress=None, **kwargs):
        pass

    @abc.abstractmethod
    def remove(self, name, progress=None, **kwargs):
        pass

    @abc.abstractmethod
    def walk(self, folder, **kwargs):
        pass

    @abc.abstractmethod
    def listAll(self, folder, **kwargs):
        pass

    @abc.abstractmethod
    def listFolders(self, folder, **kwargs):
        pass

    @abc.abstractmethod
    def listFiles(self, folder, **kwargs):
        pass

    @abc.abstractmethod
    def isFolder(self, path, **kwargs):
        pass

    @abc.abstractmethod
    def isFile(self, path, **kwargs):
        pass

    def compress(self, zipFilePath, path, ignores=DEFAULT_IGNORE_KEYWORDS):
        compressFunc = self.compressFolder if os.path.isdir(path) else self.compressFile
        return compressFunc(zipFilePath, path, ignores=ignores)

    def compressFolder(self, zipFilePath, folderPath, ignores=DEFAULT_IGNORE_KEYWORDS):
        if folderPath in ignores:
            logger.debug(f"Ignore compressing folder: {folderPath} -> {zipFilePath}")
            return zipFilePath

        logger.debug(f"Compressing folder: {folderPath} -> {zipFilePath}")
        with zipfile.ZipFile(zipFilePath, "w") as zip:
            for root, _, files in os.walk(folderPath):
                for file in files:
                    filePath = os.path.join(root, file)
                    zip.write(
                        filePath, arcname=self.localRelativePath(filePath, folderPath)
                    )
        logger.debug(f"Compressed folder: {folderPath} -> {zipFilePath}")
        return zipFilePath

    def compressFile(self, zipFilePath, filePath, ignores=DEFAULT_IGNORE_KEYWORDS):
        if filePath in ignores:
            logger.debug(f"Ignore compressing File: {filePath} -> {zipFilePath}")
            return zipFilePath

        logger.debug(f"Compressing File: {filePath} -> {zipFilePath}")
        with zipfile.ZipFile(zipFilePath, "w") as zip:
            _, filename = os.path.split(filePath)
            zip.write(filePath, arcname=filename)
        logger.debug(f"Compressed File: {filePath} -> {zipFilePath}")
        return zipFilePath

    def extract(self, zipFilePath, distPath, ignores=DEFAULT_IGNORE_KEYWORDS):
        logger.debug(f"Extracting zip: {zipFilePath} -> {distPath}")
        with zipfile.ZipFile(zipFilePath, "r") as zip:
            zip.extractall(distPath)
        self.removeIgnores(distPath, ignores=ignores)
        logger.debug(f"Extracted zip: {zipFilePath} -> {distPath}")

    @functional.lazyproperty
    def appStoreKey(self):
        return self.storagePathJoin("studio", g.userId, g.appId)

    @functional.lazyproperty
    def appDataStoreKey(self):
        return self.storagePathJoin("studio", g.userId, "share", g.appId)

    @functional.lazyproperty
    def appConfigsStoreKey(self):
        return self.storagePathJoin("studio", g.userId, "configs", g.appId)

    @functional.lazyproperty
    def appTmpStoreKey(self):
        return self.storagePathJoin("studio", g.userId, "tmp", g.appId)

    @functional.lazyproperty
    def appLogsStoreKey(self):
        return self.storagePathJoin("studio", g.userId, "logs", g.appId)

    @functional.lazyproperty
    def nodeStoreKey(self):
        return self.storagePathJoin("studio", g.userId, g.appId, g.nodeId)

    @functional.lazyproperty
    def nodeDataStoreKey(self):
        return self.storagePathJoin("studio", g.userId, "share", g.appId, g.nodeId)

    @functional.lazyproperty
    def nodeConfigsStoreKey(self):
        return self.storagePathJoin("studio", g.userId, "configs", g.appId, g.nodeId)

    @functional.lazyproperty
    def nodeLogsStoreKey(self):
        return self.storagePathJoin("studio", g.userId, "logs", g.appId, g.nodeId)

    @functional.lazyproperty
    def componentsStoreKey(self):
        return self.storagePathJoin("studio", g.userId, "component")

    def getKeyInAppStore(self, *paths):
        return self.storagePathJoin(self.appStoreKey, *paths)

    def getKeyInAppDataStore(self, *paths):
        return self.storagePathJoin(self.appDataStoreKey, *paths)

    def getKeyInAppConfigsStore(self, *paths):
        return self.storagePathJoin(self.appConfigsStoreKey, *paths)

    def getKeyInAppTmpStore(self, requestID, *paths):
        return self.storagePathJoin(self.appTmpStoreKey, requestID, *paths)

    def getKeyInAppLogsStore(self, *paths):
        return self.storagePathJoin(self.appLogsStoreKey, *paths)

    def getKeyInNodeStore(self, *paths):
        return self.storagePathJoin(self.nodeStoreKey, *paths)

    def getKeyInNodeDataStore(self, *paths):
        return self.storagePathJoin(self.nodeDataStoreKey, *paths)

    def getKeyInNodeConfigsStore(self, *paths):
        return self.storagePathJoin(self.nodeConfigsStoreKey, *paths)

    def getKeyInNodeTmpStore(self, requestID, *paths):
        return self.storagePathJoin(self.appTmpStoreKey, requestID, g.nodeId, *paths)

    def getKeyInNodeLogsStore(self, *paths):
        return self.storagePathJoin(self.nodeLogsStoreKey, *paths)

    def getKeyInComponentDataStore(self, componentId, *paths):
        return self.storagePathJoin(self.componentsStoreKey, componentId, *paths)

    def getPathInTempStore(self, *path):
        return self.localPathJoin(self.tempStore, *path)

    def getPathInAppStore(self, *paths):
        return self.getPathInTempStore(self.getKeyInAppStore(*paths))

    def getPathInAppDataStore(self, *paths):
        return self.getPathInTempStore(self.getKeyInAppDataStore(*paths))

    def getPathInAppConfigsStore(self, *paths):
        return self.getPathInTempStore(self.getKeyInAppConfigsStore(*paths))

    def getPathInAppTmpStore(self, requestID, *paths):
        return self.getPathInTempStore(self.getKeyInAppTmpStore(requestID, *paths))

    def getPathInAppLogsStore(self, *paths):
        return self.getPathInTempStore(self.getKeyInAppLogsStore(*paths))

    def getPathInNodeDataStore(self, *paths):
        return self.getPathInTempStore(self.getKeyInNodeDataStore(*paths))

    def getPathInNodeConfigsStore(self, *paths):
        return self.getPathInTempStore(self.getKeyInNodeConfigsStore(*paths))

    def getPathInNodeTmpStore(self, requestID, *paths):
        return self.getPathInTempStore(self.getKeyInNodeLogsStore(requestID, *paths))

    def getPathInNodeLogsStore(self, *paths):
        return self.getPathInTempStore(self.getKeyInNodeLogsStore(*paths))

    def getPathInGlobalStore(self, *path):
        return self.localPathJoin(self.globalStore, *path)

    def getPathInGlobalDataStore(self, *paths):
        return self.getPathInGlobalStore("data", *paths)

    def getPathInGlobalConfigsStore(self, *paths):
        return self.getPathInGlobalStore("configs", *paths)

    def completePath(self, path, delimiter=None):
        delimiter = delimiter or self.delimiter
        return path if path.endswith(delimiter) else path + delimiter

    def toLocalPath(self, path, delimiter=None):
        delimiter = delimiter or self.delimiter
        return str(path).replace(delimiter, os.sep)

    def toStoragePath(self, path, delimiter=None):
        delimiter = delimiter or self.delimiter
        return str(path).replace(os.sep, delimiter)

    def localPathJoin(self, *paths):
        p = pathlib.Path(*paths).absolute()
        path = str(p)
        if isinstance(p, pathlib.WindowsPath):
            if len(path) > 200:
                path = "\\\\?\\" + str(p)
        return path

    def storagePathJoin(self, *paths):
        path = os.path.join(*[self.toLocalPath(path) for path in paths])
        return self.toStoragePath(path)

    def localRelativePath(self, path, base):
        return self._relativePath(path, base, delimiter=os.sep)

    def storageRelativePath(self, path, base, delimiter=None):
        delimiter = delimiter or self.delimiter
        return self._relativePath(path, base, delimiter=delimiter)

    def _relativePath(self, path, base, delimiter):
        base = base if base.endswith(delimiter) else base + delimiter
        return path[len(base) :] if path.startswith(base) else path

    @abc.abstractmethod
    def getStorageMd5(self, name, **kwargs):
        pass

    def getLocalMd5(self, path, **kwargs):  # pylint: disable=unused-argument
        return spath.md5(path) if os.path.isfile(path) else None

    def checkMd5(self, md5a, md5b, **kwargs):  # pylint: disable=unused-argument
        return md5a if md5a == md5b and md5a is not None else False

    @abc.abstractmethod
    def getStorageSize(self, name, **kwargs):  # pylint: disable=unused-argument
        pass

    def getLocalSize(self, path, **kwargs):  # pylint: disable=unused-argument
        return os.path.getsize(path)

    def storageUrl(self, path, **kwargs):  # pylint: disable=unused-argument
        return "storage://" + path

    def removeIgnores(self, path, ignores=None):
        ignores = ignores or self.DEFAULT_IGNORE_KEYWORDS

        def _ignore(_path):
            spath.remove(_path)
            logger.debug(f"Removed ignored: {_path}")
            return _path

        def _getIgnores(path):
            for root, folders, files in os.walk(path):
                for folder in folders:
                    if folder in ignores:
                        yield os.path.join(root, folder)
                for file in files:
                    if file in ignores:
                        yield os.path.join(root, file)

        return [_ignore(_path) for _path in _getIgnores(path)]

    def pathSplit(self, path, delimiter=None):
        delimiter = delimiter or self.delimiter
        return path.split(delimiter)

    def pathSplitExt(self, path, extDelimiter="."):
        return path.rsplit(extDelimiter, 1)

    def basename(self, path, delimiter=None):
        return self.pathSplit(path, delimiter=delimiter)[-1]
