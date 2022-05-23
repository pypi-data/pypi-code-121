# coding=utf-8
from __future__ import absolute_import, print_function

import os
import time

from suanpan import error
from suanpan.log import logger
from suanpan.storage import storage


class ModelLoader(object):
    def __init__(self, storagePath, version="latest"):
        self.storagePath = storagePath
        self.localPath = storage.getPathInTempStore(self.storagePath)
        self.initVersion = version

        self.useLatestVersion = self.initVersion == "latest"
        if not self.useLatestVersion:
            logger.info(
                f"Model is set to use a specific version: {self.initVersion}, model reload will not be necessary"
            )

        self.version = self.latestVersion if self.useLatestVersion else self.initVersion

        self.path = None
        self.updatedTime = None

        self.download(self.version)

    @property
    def latestVersion(self):
        return max(self.allVersions)

    @property
    def allVersions(self):
        return [
            int(folder.rstrip(storage.delimiter).split(storage.delimiter)[-1])
            for folder in storage.listFolders(self.storagePath)
        ]

    def overdue(self, duration):
        return time.time() - self.updatedTime >= duration

    def download(self, version=None):
        version = version or self.version
        versionString = str(version)
        storagePath = storage.storagePathJoin(self.storagePath, versionString)
        localPath = storage.localPathJoin(self.localPath, versionString)

        if not os.path.isdir(localPath):
            storage.download(storagePath, localPath)

        self.updatedTime = time.time()
        self.version = version
        self.path = localPath

        return self.path

    def reload(self, duration=None):
        if not self.useLatestVersion:
            logger.info(
                f"Model is set to use a specific version: {self.initVersion}, model reload is disabled"
            )
            return False

        if duration and not self.overdue(duration):
            logger.info(f"Model reload is not overdue, interval: {duration}s")
            return False

        latestVersion = self.latestVersion
        if latestVersion <= self.version:
            logger.info(f"No new model(s) found, version: {self.version}")
            return False

        logger.info(f"New model(s) found, use latest version: {latestVersion}")
        self.download(latestVersion)
        return True

    def reset(self, version):
        if version == self.version:
            logger.info(f"No need to reset, version matched: {self.version}")
            return False

        if version not in self.allVersions:
            raise error.ModelError(
                f"The version: {version} specified is not a valid model version"
            )

        self.download(version)
        return True


class Model(object):
    def __init__(self):
        self._loader = None
        self.model = None

    def setLoader(self, *args, **kwargs):
        self._loader = ModelLoader(*args, **kwargs)
        self.load(self.path)
        return self

    def loadFrom(self, *args, **kwargs):
        return self.setLoader(*args, **kwargs)

    @property
    def loader(self):
        if self._loader is None:
            raise error.ModelError("Model loader has not beed set.")
        return self._loader

    @property
    def version(self):
        return self.loader.version

    @property
    def latestVersion(self):
        return self.loader.latestVersion

    @property
    def path(self):
        return self.loader.path

    def reload(self, duration=None):
        if self.loader.reload(duration=duration):
            self.load(self.path)

    def rollback(self):
        if len(self.loader.allVersions) == 1:
            logger.info("Current model has only one version, could not rollback")
            return False

        if self.loader.reset(self.version - 1):
            self.load(self.path)
            return True

        return False

    def load(self, path):
        raise NotImplementedError("Method not implemented!")

    def save(self, path):
        raise NotImplementedError("Method not implemented!")

    def prepare(self):
        raise NotImplementedError("Method not implemented!")

    def train(self, data):
        raise NotImplementedError("Method not implemented!")

    def evaluate(self):
        raise NotImplementedError("Method not implemented!")

    def predict(self, features):
        raise NotImplementedError("Method not implemented!")
