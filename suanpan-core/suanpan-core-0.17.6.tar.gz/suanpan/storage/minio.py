# coding=utf-8
from __future__ import absolute_import, division, print_function

import functools
import os
from threading import Thread

from lostc import collection as lcc

import minio.error
from minio import Minio
from minio.commonconfig import CopySource
from suanpan import api, asyncio, g
from suanpan import path as spath
from suanpan import runtime
from suanpan.log import logger
from suanpan.storage import base
from suanpan.utils import pbar as spbar


class Storage(base.Storage):
    def __init__(
        self,
        minioAccessKey=None,
        minioSecretKey=None,
        minioBucketName="suanpan",
        minioEndpoint="minio-serivce.default:9000",
        minioSecure=True,
        minioDelimiter="/",
        minioTempStore=base.Storage.DEFAULT_TEMP_DATA_STORE,
        minioGlobalStore=base.Storage.DEFAULT_GLOBAL_DATA_STORE,
        **kwargs,
    ):
        super().__init__(
            delimiter=minioDelimiter,
            tempStore=minioTempStore,
            globalStore=minioGlobalStore,
            **kwargs,
        )

        self.bucketName = minioBucketName
        self.bucket = minioBucketName
        self.endpoint, self.secure = self._analyzeEndpoint(minioEndpoint, minioSecure)
        self.refreshAccessKey(accessKey=minioAccessKey, secretKey=minioSecretKey)

    def _analyzeEndpoint(self, endpoint, secure=False):
        httpsPrefix = "https://"
        if endpoint.startswith(httpsPrefix):
            return endpoint[len(httpsPrefix) :], True

        httpPrefix = "http://"
        if endpoint.startswith(httpPrefix):
            return endpoint[len(httpPrefix) :], False

        return endpoint, secure

    def autoRefreshToken(self, func):
        @functools.wraps(func)
        def _dec(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except minio.error.S3Error as e:
                if e.code == "AccessDenied":
                    logger.warning("Minio access denied, refreshing access key.")
                    self.refreshAccessKey()
                    return func(*args, **kwargs)
                raise e

        return _dec

    def refreshAccessKey(self, accessKey=None, secretKey=None):
        if accessKey and secretKey:
            self.accessKey = accessKey
            self.secretKey = secretKey
        else:
            data = api.oss.getToken()
            self.accessKey = data["Credentials"]["AccessKeyId"]
            self.secretKey = data["Credentials"]["AccessKeySecret"]

        self.client = Minio(
            self.endpoint,
            access_key=self.accessKey,
            secret_key=self.secretKey,
            secure=self.secure,
        )
        return self.accessKey, self.secretKey

    @runtime.retry(stop_max_attempt_number=3)
    def download(
        self,
        key,
        path=None,
        progress=None,
        bucket=None,
        ignores=None,
        quiet=not g.debug,
    ):
        ignores = ignores or self.DEFAULT_IGNORE_KEYWORDS
        downloadFunction = (
            self.downloadFile
            if self.isFile(key, bucket=bucket)
            else self.downloadFolder
        )
        return downloadFunction(
            key, path, progress=progress, bucket=bucket, ignores=ignores, quiet=quiet
        )

    def downloadFolder(
        self,
        key,
        path=None,
        progress=None,
        bucket=None,
        delimiter=None,
        ignores=None,
        quiet=not g.debug,
    ):
        bucket = bucket or self.bucket
        ignores = ignores or self.DEFAULT_IGNORE_KEYWORDS
        delimiter = delimiter or self.delimiter
        path = os.path.abspath(path) if path else self.getPathInTempStore(key)
        url = self.storageUrl(key, bucket=bucket)

        if not quiet:
            logger.info(f"Downloading folder: {url} -> {path}")

        if self.basename(key) in ignores:
            with spbar.one(
                total=1, desc="Downloading", disable=quiet, progress=progress
            ) as pbar:
                pbar.update(1)
                pbar.set_description("Ignored")
                return path

        downloads = {
            file: self.localPathJoin(path, self.storageRelativePath(file, key))
            for _, _, files in self.walk(key, delimiter=delimiter, bucket=bucket)
            for file in files
        }

        # Download from minio
        _run = functools.partial(
            self.downloadFile, bucket=bucket, ignores=ignores, quiet=True
        )
        asyncio.starmap(
            _run, downloads.items(), pbar=quiet, desc="Downloading", progress=progress,
        )
        # Remove ignores
        self.removeIgnores(path, ignores=ignores)
        # Remove rest files and folders
        files = (
            self.localPathJoin(root, file)
            for root, _, files in os.walk(path)
            for file in files
        )
        restFiles = [file for file in files if file not in downloads.values()]
        asyncio.map(
            spath.remove, restFiles, pbar=quiet, desc="Removing Rest Files",
        )
        # only if the `path` folder is getPathInTempStore, try to clear it
        if path == self.getPathInTempStore(key):
            spath.removeEmptyFolders(path)
        if not quiet:
            logger.debug(f"Removed empty folders in: {path}")
        # End
        return path

    def downloadFile(
        self,
        key,
        path=None,
        progress=None,
        bucket=None,
        ignores=None,
        quiet=not g.debug,
    ):
        bucket = bucket or self.bucket
        ignores = ignores or self.DEFAULT_IGNORE_KEYWORDS
        path = os.path.abspath(path) if path else self.getPathInTempStore(key)
        url = self.storageUrl(key, bucket=bucket)
        fileSize = self.getStorageSize(key, bucket=bucket)

        if not quiet:
            logger.info(f"Downloading file: {url} -> {path}")

        with spbar.one(
            total=fileSize, desc="Downloading", disable=quiet, progress=progress
        ) as pbar:
            if self.basename(key) in ignores:
                pbar.update(fileSize)
                pbar.set_description("Ignored")
                return path

            objectMd5 = self.getStorageMd5(key, bucket=bucket)
            fileMd5 = self.getLocalMd5(path)
            if self.checkMd5(objectMd5, fileMd5, bucket=bucket):
                pbar.update(fileSize)
                pbar.set_description("Existed")
                return path

            spath.safeMkdirsForFile(path)
            self.autoRefreshToken(self.client.fget_object)(bucket, key, path)

            pbar.update(fileSize)
            pbar.set_description("Downloaded")

            return path

    @runtime.retry(stop_max_attempt_number=3)
    def upload(
        self,
        name,
        path=None,
        progress=None,
        bucket=None,
        ignores=None,
        quiet=not g.debug,
    ):
        bucket = bucket or self.bucket
        ignores = ignores or self.DEFAULT_IGNORE_KEYWORDS
        uploadFunction = self.uploadFolder if os.path.isdir(path) else self.uploadFile
        return uploadFunction(
            name, path, progress=progress, bucket=bucket, ignores=ignores, quiet=quiet
        )

    def uploadFolder(
        self,
        key,
        path=None,
        progress=None,
        bucket=None,
        ignores=None,
        quiet=not g.debug,
    ):
        bucket = bucket or self.bucket
        ignores = ignores or self.DEFAULT_IGNORE_KEYWORDS
        path = os.path.abspath(path) if path else self.getPathInTempStore(key)
        url = self.storageUrl(key, bucket=bucket)

        if not quiet:
            logger.debug(f"Uploading folder: {path} -> {url}")

        if self.basename(key) in ignores:
            with spbar.one(
                total=1, desc="Uploading", disable=quiet, progress=progress
            ) as pbar:
                pbar.update(1)
                pbar.set_description("Ignored")
                return path

        files = (
            os.path.join(root, file)
            for root, _, files in os.walk(path)
            for file in files
        )
        uploads = {
            file: self.storagePathJoin(key, self.localRelativePath(file, path))
            for file in files
        }

        if not uploads:
            if not quiet:
                logger.warning(f"Uploading empty folder: {path}")
        else:
            # Upload files to oss
            uploadItems = [
                (objectName, filePath) for filePath, objectName in uploads.items()
            ]
            _run = functools.partial(
                self.uploadFile, bucket=bucket, ignores=ignores, quiet=True
            )
            asyncio.starmap(_run, uploadItems, pbar="Uploading")

        # Remove rest files
        localFiles = set(self.localRelativePath(file, path) for file in uploads.keys())
        remoteFiles = set(
            self.storageRelativePath(file, key)
            for _, _, files in self.walk(key, bucket=bucket)
            for file in files
        )
        restFiles = [
            self.storagePathJoin(key, file) for file in remoteFiles - localFiles
        ]
        _run = functools.partial(self.remove, bucket=bucket, quiet=True)
        asyncio.map(
            _run, restFiles, pbar=quiet, desc="Removing Rest Files", progress=progress,
        )
        # End
        return path

    def uploadFile(
        self,
        key,
        path=None,
        progress=None,
        bucket=None,
        ignores=None,
        quiet=not g.debug,
    ):
        bucket = bucket or self.bucket
        ignores = ignores or self.DEFAULT_IGNORE_KEYWORDS
        path = os.path.abspath(path) if path else self.getPathInTempStore(key)
        url = self.storageUrl(key, bucket=bucket)
        fileSize = os.path.getsize(path)

        if not quiet:
            logger.info(f"Uploading file: {path} -> {url}")

        with spbar.one(
            total=fileSize, desc="Uploading", disable=quiet, progress=progress
        ) as pbar:
            if self.basename(key) in ignores:
                pbar.update(fileSize)
                pbar.set_description("Ignored")
                return path

            objectMd5 = self.getStorageMd5(key, bucket=bucket)
            fileMd5 = self.getLocalMd5(path)
            if self.checkMd5(objectMd5, fileMd5):
                pbar.update(fileSize)
                pbar.set_description("Existed")
                return path

            self.autoRefreshToken(self.client.fput_object)(
                bucket,
                key,
                path,
                progress=Progress(pbar),
                metadata={self.CONTENT_MD5: fileMd5},
            )

            pbar.set_description("Uploaded")
            return path

    @runtime.retry(stop_max_attempt_number=3)
    def copy(self, src, dist, progress=None, bucket=None, quiet=not g.debug):
        bucket = bucket or self.bucket
        copyFunction = (
            self.copyFile if self.isFile(src, bucket=bucket) else self.copyFolder
        )
        return copyFunction(src, dist, progress=progress, bucket=bucket, quiet=quiet)

    def copyFolder(
        self, src, dist, progress=None, bucket=None, delimiter=None, quiet=not g.debug,
    ):
        bucket = bucket or self.bucket
        delimiter = delimiter or self.delimiter
        src = self.completePath(src)
        dist = self.completePath(dist)
        srcurl = self.storageUrl(src, bucket=bucket)
        disturl = self.storageUrl(dist, bucket=bucket)

        if not quiet:
            logger.info(f"Copying folder: {srcurl} -> {disturl}")

        copyItems = [
            (file, file.replace(src, dist))
            for _, _, files in self.walk(src, delimiter=delimiter, bucket=bucket)
            for file in files
        ]
        _run = functools.partial(self.copyFile, bucket=bucket, quiet=True)
        asyncio.starmap(
            _run, copyItems, pbar=quiet, desc="Copying", progress=progress,
        )
        return dist

    def copyFile(self, src, dist, progress=None, bucket=None, quiet=not g.debug):
        bucket = bucket or self.bucket
        fileSize = self.getStorageSize(src, bucket=bucket)
        srcurl = self.storageUrl(src, bucket=bucket)
        disturl = self.storageUrl(dist, bucket=bucket)

        if not quiet:
            logger.info(f"Copying file: {srcurl} -> {disturl}")

        with spbar.one(
            total=fileSize, desc="Copying", disable=quiet, progress=progress
        ) as pbar:
            objectMd5 = self.getStorageMd5(src, bucket=bucket)
            distMd5 = self.getStorageMd5(dist, bucket=bucket)
            if self.checkMd5(objectMd5, distMd5):
                pbar.update(fileSize)
                pbar.set_description("Existed")
                return dist

            # sourcePath = self.delimiter + self.storagePathJoin(bucket, src)
            self.autoRefreshToken(self.client.copy_object)(bucket, dist, CopySource(bucket, src))
            pbar.update(fileSize)
            pbar.set_description("Copied")
            return dist

    @runtime.retry(stop_max_attempt_number=3)
    def remove(
        self, key, progress=None, delimiter=None, bucket=None, quiet=not g.debug
    ):
        delimiter = delimiter or self.delimiter
        bucket = bucket or self.bucket
        removeFunc = (
            self.removeFile if self.isFile(key, bucket=bucket) else self.removeFolder
        )
        return removeFunc(key, delimiter=delimiter, bucket=bucket, quiet=quiet)

    def removeFolder(
        self, key, progress=None, delimiter=None, bucket=None, quiet=not g.debug
    ):
        delimiter = delimiter or self.delimiter
        bucket = bucket or self.bucket
        key = self.completePath(key)

        if not quiet:
            logger.info(f"Removing folder: {key}")

        removes = [
            objectName
            for _, _, files in self.walk(key, bucket=bucket, delimiter=delimiter)
            for objectName in files
        ]
        _run = functools.partial(
            self.removeFile, delimiter=delimiter, bucket=bucket, quiet=True
        )
        asyncio.map(
            _run,
            removes,
            pbar=quiet or not removes,
            desc="Removing",
            progress=progress,
        )
        return key

    def removeFile(
        self, key, progress=None, delimiter=None, bucket=None, quiet=not g.debug
    ):  # pylint: disable=unused-argument
        delimiter = delimiter or self.delimiter
        bucket = bucket or self.bucket

        if not quiet:
            logger.info(f"Removing file: {key}")

        _remove = self.autoRefreshToken(self.client.remove_object)
        with spbar.one(
            total=1, disable=quiet, desc="Removing", progress=progress,
        ) as pbar:
            self.autoRefreshToken(self.client.remove_object)(bucket, key)
            pbar.update(1)
            pbar.set_description("Removed")
            return key

    def walk(self, key, delimiter=None, bucket=None):
        bucket = bucket or self.bucket
        delimiter = delimiter or self.delimiter
        root = self.completePath(key, delimiter=delimiter)
        objects = runtime.saferun(self._listAll, default=iter(()))(
            key, delimiter=delimiter, bucket=bucket
        )
        folders, files = lcc.divide(objects, lambda obj: obj.is_dir)
        yield root, self._getObjectNames(folders), self._getObjectNames(files)
        for folder in folders:
            yield from self.walk(folder.object_name, delimiter=delimiter, bucket=bucket)

    def _listAll(self, key, delimiter=None, bucket=None):
        bucket = bucket or self.bucket
        delimiter = delimiter or self.delimiter
        prefix = self.completePath(key, delimiter=delimiter)
        return self.autoRefreshToken(self.client.list_objects)(bucket, prefix=prefix)

    def listAll(self, key, delimiter=None, bucket=None):
        return (obj.object_name for obj in self._listAll(key, delimiter=delimiter, bucket=bucket))

    def listFolders(self, key, delimiter=None, bucket=None):
        return (obj.object_name for obj in self._listAll(key, delimiter=delimiter, bucket=bucket) if obj.is_dir)

    def listFiles(self, key, delimiter=None, bucket=None):
        return (obj.object_name for obj in self._listAll(key, delimiter=delimiter, bucket=bucket) if not obj.is_dir)

    def isFolder(self, key, bucket=None):
        return bool(next(self.listAll(key, bucket=bucket), None))

    def isFile(self, key, bucket=None):
        bucket = bucket or self.bucket
        try:
            self.autoRefreshToken(self.client.stat_object)(bucket, key)
            return True
        except minio.error.S3Error as e:
            if e.code == "NoSuchKey":
                return False
            raise e

    def getStorageMd5(self, key, bucket=None):
        bucket = bucket or self.bucket
        try:
            return self.autoRefreshToken(self.client.stat_object)(
                bucket, key
            ).metadata.get(self.CONTENT_MD5)
        except minio.error.S3Error as e:
            if e.code == "NoSuchKey":
                return None
            raise e

    def getStorageSize(self, key, bucket=None):
        bucket = bucket or self.bucket
        return self.autoRefreshToken(self.client.stat_object)(bucket, key).size

    def storageUrl(self, key, bucket=None):
        bucket = bucket or self.bucket
        return "minio:///" + self.storagePathJoin(bucket, key)

    def _getObjectNames(self, objects):
        return (
            [obj.object_name for obj in objects]
            if isinstance(objects, (tuple, list))
            else objects.object_name
        )


class Progress(Thread):
    def __init__(self, pbar, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pbar = pbar
        self.size = None
        self.key = None

    def set_meta(self, total_length, object_name):
        self.size = total_length
        self.key = object_name

    def update(self, n):
        self.pbar.update(n)
        self.pbar.set_description("Uploading")
