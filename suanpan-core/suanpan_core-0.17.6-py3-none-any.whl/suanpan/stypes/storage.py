import abc
import os
import typing as t
from suanpan import g


class StorageT(object):
    tempStore: t.Annotated[str, 'the folder to save tmp files']
    globalStore: t.Annotated[str, 'the folder to save global files']
    delimiter = t.Annotated[str, 'default is os.sep']

    @abc.abstractmethod
    def download(self, key, path=None, progress=None, bucketOrBucketName=None, ignores=None, quiet=not g.debug):
        """download a file from remote storage, oss or minio

        Arguments:
            key: the file `key` in storage
            path: save file to `path`
            progress: print a progress bar
            bucketOrBucketName: a bucket instance or bucket name
            ignores: ignore file names
            quiet: if False, logging download message
        """
        ...

    @abc.abstractmethod
    def upload(self, key, path=None, progress=None, bucketOrBucketName=None, ignores=None, quiet=not g.debug):
        """upload a file to remote storage, oss or minio

        Arguments:
            key: the file `key` in storage
            path: upload file from `path`
            progress: print a progress bar
            bucketOrBucketName: a bucket instance or bucket name
            ignores: ignore file names
            quiet: if False, logging upload message
        """
        ...

    @abc.abstractmethod
    def copy(self, name, dist, progress=None, bucketOrBucketName=None, quiet=not g.debug):
        """copy a file or folder from `name` to `dist` in remote storage, oss or minio

        Arguments:
            name: the source file or folder `name` in storage
            dist: the destination of copy
            progress: print a progress bar
            bucketOrBucketName: a bucket instance or bucket name
            quiet: if False, logging upload message
        """
        ...

    @abc.abstractmethod
    def remove(self, key, progress=None, delimiter=None, bucketOrBucketName=None, quiet=not g.debug):
        """remove a file or folder from in remote storage, oss or minio

        Arguments:
            key: the file `key` to remove
            progress: print a progress bar
            delimiter: delimiter of path
            bucketOrBucketName: a bucket instance or bucket name
            quiet: if False, logging upload message
        """
        ...

    @abc.abstractmethod
    def walk(self, key, delimiter=None, bucketOrBucketName=None):
        """Generate the file names in a directory tree by walking the tree.

        Arguments:
            key: the path `key` to walk
            delimiter: delimiter of path
            bucketOrBucketName: a bucket instance or bucket name
        """
        ...

    @abc.abstractmethod
    def listAll(self, key, delimiter=None, bucketOrBucketName=None):
        """Return a list containing the names of the entries in the directory given by path.

        Arguments:
            key: the path `key` to list
            delimiter: delimiter of path
            bucketOrBucketName: a bucket instance or bucket name
        """
        ...

    @abc.abstractmethod
    def listFolders(self, key, delimiter=None, bucketOrBucketName=None):
        """Return a list containing the names of the folders in the directory given by path.

        Arguments:
            key: the path `key` to list
            delimiter: delimiter of path
            bucketOrBucketName: a bucket instance or bucket name
        """
        ...

    @abc.abstractmethod
    def listFiles(self, key, delimiter=None, bucketOrBucketName=None):
        """Return a list containing the names of the files in the directory given by path.

        Arguments:
            key: the path `key` to list
            delimiter: delimiter of path
            bucketOrBucketName: a bucket instance or bucket name
        """
        ...

    @property
    def appStoreKey(self):
        return self.storagePathJoin("studio", g.userId, g.appId)

    @property
    def appDataStoreKey(self):
        return self.storagePathJoin("studio", g.userId, "share", g.appId)

    @property
    def appConfigsStoreKey(self):
        return self.storagePathJoin("studio", g.userId, "configs", g.appId)

    @property
    def appTmpStoreKey(self):
        return self.storagePathJoin("studio", g.userId, "tmp", g.appId)

    @property
    def appLogsStoreKey(self):
        return self.storagePathJoin("studio", g.userId, "logs", g.appId)

    @property
    def nodeStoreKey(self):
        return self.storagePathJoin("studio", g.userId, g.appId, g.nodeId)

    @property
    def nodeDataStoreKey(self):
        return self.storagePathJoin("studio", g.userId, "share", g.appId, g.nodeId)

    @property
    def nodeConfigsStoreKey(self):
        return self.storagePathJoin("studio", g.userId, "configs", g.appId, g.nodeId)

    @property
    def nodeLogsStoreKey(self):
        return self.storagePathJoin("studio", g.userId, "logs", g.appId, g.nodeId)

    @property
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
        path = os.path.join(*paths)
        return self.toLocalPath(path)

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
        return path[len(base):] if path.startswith(base) else path
