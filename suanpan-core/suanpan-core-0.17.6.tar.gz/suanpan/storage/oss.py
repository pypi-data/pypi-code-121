# coding=utf-8
from __future__ import absolute_import, division, print_function

import functools
import math
import os

import oss2
from lostc import collection as lcc
from oss2.models import PartInfo
from oss2.resumable import ResumableDownloadStore, ResumableStore

from suanpan import api, asyncio, g
from suanpan import path as spath
from suanpan import runtime
from suanpan.log import logger
from suanpan.storage import base
from suanpan.utils import pbar as spbar


class Storage(base.Storage):
    LARGE_FILE_SIZE = 1024 * 1024 * 1024  # 1GB
    PREFERRED_SIZE = 500 * 1024 * 1024  # 500MB

    def __init__(
        self,
        ossAccessId=None,
        ossAccessKey=None,
        ossBucketName="suanpan",
        ossEndpoint="http://oss-cn-beijing.aliyuncs.com",
        ossDelimiter="/",
        ossTempStore=base.Storage.DEFAULT_TEMP_DATA_STORE,
        ossGlobalStore=base.Storage.DEFAULT_GLOBAL_DATA_STORE,
        ossDownloadNumThreads=1,
        ossDownloadStoreName=".py-oss-download",
        ossUploadNumThreads=1,
        ossUploadStoreName=".py-oss-upload",
        **kwargs,
    ):
        super().__init__(
            delimiter=ossDelimiter,
            tempStore=ossTempStore,
            globalStore=ossGlobalStore,
            **kwargs,
        )

        self.bucketName = ossBucketName
        self.endpoint = ossEndpoint
        self.refreshAccessKey(accessId=ossAccessId, accessKey=ossAccessKey)

        self.downloadNumThreads = ossDownloadNumThreads
        self.downloadStoreName = ossDownloadStoreName
        self.downloadStore = ResumableDownloadStore(
            self.tempStore, self.downloadStoreName
        )

        self.uploadNumThreads = ossUploadNumThreads
        self.uploadStoreName = ossUploadStoreName
        self.uploadStore = ResumableStore(self.tempStore, self.uploadStoreName)

        self._removeOssLogger()

    def autoRefreshToken(self, func):
        @functools.wraps(func)
        def _dec(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except oss2.exceptions.OssError as e:
                if e.status != 403:
                    raise e
                logger.warning("Oss access denied, refreshing access key.")
                self.refreshAccessKey()
                return func(*args, **kwargs)

        return _dec

    def autoRefreshBucket(self, bucket):
        try:
            bucket.object_exists(f"studio/{g.userId}/config")
            return bucket
        except oss2.exceptions.OssError as e:
            if e.status != 403:
                raise e
            logger.warning("Oss access denied, refreshing access key.")
            self.refreshAccessKey()
            bucket = self.getBucketByName(bucket.bucket_name)
            return bucket

    def refreshAccessKey(self, accessId=None, accessKey=None):
        if accessId and accessKey:
            self.accessId = accessId
            self.accessKey = accessKey
            self.auth = oss2.Auth(self.accessId, self.accessKey)
        else:
            data = api.oss.getToken()
            self.accessId = data["Credentials"]["AccessKeyId"]
            self.accessKey = data["Credentials"]["AccessKeySecret"]
            self.securityToken = data["Credentials"]["SecurityToken"]
            self.auth = oss2.StsAuth(self.accessId, self.accessKey, self.securityToken)

        self.bucket = self.getBucket(self.bucketName)
        return self.accessId, self.accessKey

    def _removeOssLogger(self):
        ossLogger = getattr(oss2, "logger", None)
        if ossLogger:
            self._removeLoggerHandlers(ossLogger)

    def _removeLoggerHandlers(self, _logger):
        for handler in _logger.handlers[:]:
            _logger.removeHandler(handler)
        return _logger

    @runtime.retry(stop_max_attempt_number=3)
    def download(
        self,
        key,
        path=None,
        progress=None,
        bucketOrBucketName=None,
        ignores=None,
        quiet=not g.debug,
    ):
        bucket = self.getBucket(bucketOrBucketName)
        ignores = ignores or self.DEFAULT_IGNORE_KEYWORDS
        downloadFunction = (
            self.downloadFile
            if self.isFile(key, bucketOrBucketName=bucket)
            else self.downloadFolder
        )
        return downloadFunction(
            key,
            path=path,
            progress=progress,
            bucketOrBucketName=bucket,
            ignores=ignores,
            quiet=quiet,
        )

    def downloadFolder(
        self,
        key,
        path=None,
        progress=None,
        delimiter=None,
        bucketOrBucketName=None,
        ignores=None,
        quiet=not g.debug,
    ):
        bucket = self.getBucket(bucketOrBucketName)
        ignores = ignores or self.DEFAULT_IGNORE_KEYWORDS
        delimiter = delimiter or self.delimiter
        path = os.path.abspath(path) if path else self.getPathInTempStore(key)
        url = self.storageUrl(key, bucketOrBucketName=bucket)

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
            for _, _, files in self.walk(
                key, delimiter=delimiter, bucketOrBucketName=bucket
            )
            for file in files
        }

        # Download from oss
        _run = functools.partial(
            self.downloadFile, bucketOrBucketName=bucket, ignores=ignores, quiet=True
        )
        asyncio.starmap(
            _run, downloads.items(), pbar=quiet, desc="Downloading", progress=progress,
        )
        # Remove ignores
        self.removeIgnores(path, ignores=ignores)
        # Remove rest files and folders
        files = (
            os.path.join(root, file)
            for root, _, files in os.walk(path)
            for file in files
        )
        restFiles = [file for file in files if file not in downloads.values()]
        asyncio.map(
            spath.remove,
            restFiles,
            pbar=quiet or not restFiles,
            desc="Removing Rest Files",
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
        bucketOrBucketName=None,
        ignores=None,
        quiet=not g.debug,
    ):
        bucket = self.getBucket(bucketOrBucketName)
        ignores = ignores or self.DEFAULT_IGNORE_KEYWORDS
        path = os.path.abspath(path) if path else self.getPathInTempStore(key)
        url = self.storageUrl(key, bucketOrBucketName=bucket)
        fileSize = self.getStorageSize(key, bucketOrBucketName=bucket)

        if not quiet:
            logger.info(f"Downloading file: {url} -> {path}")

        with spbar.one(total=fileSize, disable=quiet, progress=progress) as pbar:
            if self.basename(key) in ignores:
                pbar.update(fileSize)
                pbar.set_description("Ignored")
                return path

            fileMd5 = self.getLocalMd5(path)
            objectMd5 = self.getStorageMd5(key, bucketOrBucketName=bucket)
            if self.checkMd5(fileMd5, objectMd5):
                pbar.update(fileSize)
                pbar.set_description("Existed")
                return path

            def _percentage(consumed_bytes, total_bytes):
                if total_bytes:
                    pbar.update(consumed_bytes - pbar.n)
                    pbar.set_description("Downloading")

            spath.safeMkdirsForFile(path)
            self.autoRefreshToken(oss2.resumable_download)(
                bucket,
                key,
                path,
                num_threads=self.downloadNumThreads,
                store=self.downloadStore,
                progress_callback=_percentage,
            )

            pbar.set_description("Downloaded")

            return path

    @runtime.retry(stop_max_attempt_number=3)
    def upload(
        self,
        key,
        path=None,
        progress=None,
        bucketOrBucketName=None,
        ignores=None,
        quiet=not g.debug,
    ):
        bucket = self.getBucket(bucketOrBucketName)
        ignores = ignores or self.DEFAULT_IGNORE_KEYWORDS
        uploadFunction = self.uploadFolder if os.path.isdir(path) else self.uploadFile
        return uploadFunction(
            key,
            path=path,
            progress=progress,
            bucketOrBucketName=bucket,
            ignores=ignores,
            quiet=quiet,
        )

    def uploadFolder(
        self,
        key,
        path=None,
        progress=None,
        bucketOrBucketName=None,
        ignores=None,
        quiet=not g.debug,
    ):
        bucket = self.getBucket(bucketOrBucketName)
        ignores = ignores or self.DEFAULT_IGNORE_KEYWORDS
        path = os.path.abspath(path) if path else self.getPathInTempStore(key)
        url = self.storageUrl(key, bucketOrBucketName=bucket)

        if not quiet:
            logger.info(f"Uploading folder: {path} -> {url}")

        if key in ignores:
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
            uploadItems = [(key, file) for file, key in uploads.items()]
            _run = functools.partial(
                self.uploadFile, bucketOrBucketName=bucket, ignores=ignores, quiet=True
            )
            asyncio.starmap(
                _run, uploadItems, pbar=quiet, desc="Uploading", progress=progress,
            )

        # Remove rest files
        localFiles = set(self.localRelativePath(file, path) for file in uploads.keys())
        remoteFiles = set(
            self.storageRelativePath(file, key)
            for _, _, files in self.walk(key)
            for file in files
        )
        restFiles = [
            self.storagePathJoin(key, file) for file in remoteFiles - localFiles
        ]
        _run = functools.partial(self.remove, bucketOrBucketName=bucket, quiet=True)
        asyncio.map(
            _run, restFiles, pbar=quiet or not restFiles, desc="Removing Rest Files",
        )
        # End
        return path

    def uploadFile(
        self,
        key,
        path=None,
        progress=None,
        bucketOrBucketName=None,
        ignores=None,
        quiet=not g.debug,
    ):
        bucket = self.getBucket(bucketOrBucketName)
        ignores = ignores or self.DEFAULT_IGNORE_KEYWORDS
        path = os.path.abspath(path) if path else self.getPathInTempStore(key)
        url = self.storageUrl(key, bucketOrBucketName=bucket)
        fileSize = self.getLocalSize(path)

        if not quiet:
            logger.info(f"Uploading file: {path} -> {url}")

        with spbar.one(total=fileSize, disable=quiet, progress=progress) as pbar:
            if self.basename(key) in ignores:
                pbar.update(fileSize)
                pbar.set_description("Ignored")
                return path

            fileMd5 = self.getLocalMd5(path)
            objectMd5 = self.getStorageMd5(key, bucketOrBucketName=bucket)
            if self.checkMd5(fileMd5, objectMd5):
                pbar.update(fileSize)
                pbar.set_description("Existed")
                return path

            def _percentage(consumed_bytes, total_bytes):
                if total_bytes:
                    pbar.update(consumed_bytes - pbar.n)
                    pbar.set_description("Uploading")

            self.autoRefreshToken(oss2.resumable_upload)(
                bucket,
                key,
                path,
                num_threads=self.uploadNumThreads,
                store=self.uploadStore,
                progress_callback=_percentage,
                headers={self.CONTENT_MD5: fileMd5},
            )

            pbar.set_description("Uploaded")

            return path

    @runtime.retry(stop_max_attempt_number=3)
    def copy(
        self, name, dist, progress=None, bucketOrBucketName=None, quiet=not g.debug
    ):
        bucket = self.getBucket(bucketOrBucketName)
        copyFunction = (
            self.copyFile
            if self.isFile(name, bucketOrBucketName=bucket)
            else self.copyFolder
        )
        return copyFunction(
            name, dist, progress=progress, bucketOrBucketName=bucket, quiet=quiet
        )

    def copyFolder(
        self,
        src,
        dist,
        progress=None,
        bucketOrBucketName=None,
        delimiter=None,
        quiet=not g.debug,
    ):
        bucket = self.getBucket(bucketOrBucketName)
        delimiter = delimiter or self.delimiter
        src = self.completePath(src)
        dist = self.completePath(dist)
        srcurl = self.storageUrl(src, bucketOrBucketName=bucket)
        disturl = self.storageUrl(dist, bucketOrBucketName=bucket)

        if not quiet:
            logger.info(f"Copying folder: {srcurl} -> {disturl}")

        copyItems = [
            (file, file.replace(src, dist))
            for _, _, files in self.walk(
                src, delimiter=delimiter, bucketOrBucketName=bucket
            )
            for file in files
        ]
        _run = functools.partial(self.copyFile, bucketOrBucketName=bucket, quiet=True)
        asyncio.starmap(
            _run, copyItems, pbar=quiet, desc="Copying", progress=progress,
        )
        return dist

    def copyFile(
        self, src, dist, progress=None, bucketOrBucketName=None, quiet=not g.debug
    ):
        bucket = self.getBucket(bucketOrBucketName)
        fileSize = self.getStorageSize(src, bucketOrBucketName=bucket)
        copyFunction = (
            self.copyLargeFile
            if fileSize >= self.LARGE_FILE_SIZE
            else self.copySmallFile
        )
        return copyFunction(
            src,
            dist,
            fileSize,
            progress=progress,
            bucketOrBucketName=bucket,
            quiet=quiet,
        )

    def copySmallFile(
        self,
        src,
        dist,
        size,
        progress=None,
        bucketOrBucketName=None,
        quiet=not g.debug,
    ):
        bucket = self.getBucket(bucketOrBucketName)
        srcurl = self.storageUrl(src, bucketOrBucketName=bucket)
        disturl = self.storageUrl(dist, bucketOrBucketName=bucket)

        if not quiet:
            logger.info(f"Copying file: {srcurl} -> {disturl}")

        with spbar.one(
            total=size, desc="Copying", disable=quiet, progress=progress
        ) as pbar:
            objectMd5 = self.getStorageMd5(src, bucketOrBucketName=bucket)
            distMd5 = self.getStorageMd5(dist, bucketOrBucketName=bucket)
            if self.checkMd5(objectMd5, distMd5):
                pbar.update(size)
                pbar.set_description("Existed")
                return dist

            bucket.copy_object(bucket.bucket_name, src, dist)
            pbar.update(size)
            pbar.set_description("Copied")
            return dist

    def copyLargeFile(
        self,
        src,
        dist,
        size,
        progress=None,
        bucketOrBucketName=None,
        quiet=not g.debug,
    ):
        bucket = self.getBucket(bucketOrBucketName)
        srcurl = self.storageUrl(src, bucketOrBucketName=bucket)
        disturl = self.storageUrl(dist, bucketOrBucketName=bucket)

        if not quiet:
            logger.info(f"Copying file: {srcurl} -> {disturl}")

        with spbar.one(
            total=size, desc="Copying", disable=quiet, progress=progress
        ) as pbar:
            objectMd5 = self.getStorageMd5(src, bucketOrBucketName=bucket)
            distMd5 = self.getStorageMd5(dist, bucketOrBucketName=bucket)
            if self.checkMd5(objectMd5, distMd5):
                pbar.update(size)
                pbar.set_description("Existed")
                return dist

            partSize = self.autoRefreshToken(oss2.determine_part_size)(
                size, preferred_size=self.PREFERRED_SIZE
            )
            uploadId = bucket.init_multipart_upload(dist).upload_id
            parts = math.ceil(size / partSize)
            parts = (
                (i + 1, i * partSize, min((i + 1) * partSize, size))
                for i in range(parts)
            )

            def _copy(part):
                partNumber, byteRange = part[0], part[-2:]
                result = bucket.upload_part_copy(
                    bucket.bucket_name, src, byteRange, dist, uploadId, partNumber,
                )
                pbar.update(byteRange[1] - byteRange[0])
                pbar.set_description("Copying")
                return PartInfo(partNumber, result.etag)

            parts = [_copy(part) for part in parts]
            bucket.complete_multipart_upload(dist, uploadId, parts)
            pbar.set_description("Copied")
            return dist

    @runtime.retry(stop_max_attempt_number=3)
    def remove(
        self,
        key,
        progress=None,
        delimiter=None,
        bucketOrBucketName=None,
        quiet=not g.debug,
    ):
        delimiter = delimiter or self.delimiter
        bucket = self.getBucket(bucketOrBucketName)
        removeFunc = (
            self.removeFile
            if self.isFile(key, bucketOrBucketName=bucket)
            else self.removeFolder
        )
        return removeFunc(
            key,
            progress=progress,
            delimiter=delimiter,
            bucketOrBucketName=bucket,
            quiet=quiet,
        )

    def removeFolder(
        self,
        key,
        progress=None,
        delimiter=None,
        bucketOrBucketName=None,
        quiet=not g.debug,
    ):
        delimiter = delimiter or self.delimiter
        bucket = self.getBucket(bucketOrBucketName)
        key = self.completePath(key)
        url = self.storageUrl(key, bucketOrBucketName=bucket)

        if not quiet:
            logger.info(f"Removing folder: {url}")

        removes = [file for _, _, files in self.walk(key) for file in files]
        _run = functools.partial(
            self.removeFile, delimiter=delimiter, bucketOrBucketName=bucket, quiet=True
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
        self,
        key,
        progress=None,
        delimiter=None,
        bucketOrBucketName=None,
        quiet=not g.debug,
    ):  # pylint: disable=unused-argument
        delimiter = delimiter or self.delimiter
        bucket = self.getBucket(bucketOrBucketName)
        url = self.storageUrl(key, bucketOrBucketName=bucket)

        if not quiet:
            logger.info(f"Removing file: {url}")

        with spbar.one(
            total=1, disable=quiet, desc="Removing", progress=progress,
        ) as pbar:
            bucket.delete_object(key)
            pbar.update(1)
            pbar.set_description("Removed")
        return key

    def walk(self, key, delimiter=None, bucketOrBucketName=None):
        bucket = self.getBucket(bucketOrBucketName)
        delimiter = delimiter or self.delimiter
        root = self.completePath(key, delimiter=delimiter)
        objects = (
            obj
            for obj in runtime.saferun(self._listAll, default=iter(()))(
                key, delimiter=delimiter, bucketOrBucketName=bucket
            )
            if obj.key != root
        )
        folders, files = lcc.divide(objects, lambda obj: obj.is_prefix())
        folders, files = self._getObjectNames(folders), self._getObjectNames(files)
        yield root, folders, files
        for folder in folders:
            yield from self.walk(folder, delimiter=delimiter, bucketOrBucketName=bucket)

    def _listAll(self, key, delimiter=None, bucketOrBucketName=None):
        bucket = self.getBucket(bucketOrBucketName)
        delimiter = delimiter or self.delimiter
        prefix = self.completePath(key, delimiter=delimiter)
        return (
            obj
            for obj in self.autoRefreshToken(oss2.ObjectIterator)(
                delimiter=delimiter, prefix=prefix, bucket=bucket
            )
        )

    def listAll(self, key, delimiter=None, bucketOrBucketName=None):
        return (
            obj.key
            for obj in self._listAll(
                key, delimiter=delimiter, bucketOrBucketName=bucketOrBucketName
            )
        )

    def listFolders(self, key, delimiter=None, bucketOrBucketName=None):
        return (
            obj.key
            for obj in self._listAll(
                key, delimiter=delimiter, bucketOrBucketName=bucketOrBucketName
            )
            if obj.is_prefix()
        )

    def listFiles(self, key, delimiter=None, bucketOrBucketName=None):
        return (
            obj.key
            for obj in self._listAll(
                key, delimiter=delimiter, bucketOrBucketName=bucketOrBucketName
            )
            if not obj.is_prefix()
        )

    def isFolder(self, key, bucketOrBucketName=None):
        bucket = self.getBucket(bucketOrBucketName)
        return next(self.listAll(key, bucketOrBucketName=bucket), None)

    def isFile(self, key, bucketOrBucketName=None):
        bucket = self.getBucket(bucketOrBucketName)
        return bucket.object_exists(key)

    def getStorageMd5(self, key, bucketOrBucketName=None):
        bucket = self.getBucket(bucketOrBucketName)
        try:
            return bucket.head_object(key).headers.get(self.CONTENT_MD5)
        except oss2.exceptions.NotFound:
            return None

    def getStorageSize(self, key, bucketOrBucketName=None):
        bucket = self.getBucket(bucketOrBucketName)
        return bucket.head_object(key).content_length

    def storageUrl(self, key, bucketOrBucketName=None):
        bucket = self.getBucket(bucketOrBucketName)
        return "oss:///" + self.storagePathJoin(bucket.bucket_name, key)

    def getBucket(self, bucketOrBucketName):
        return self.autoRefreshBucket(
            bucketOrBucketName
            if isinstance(bucketOrBucketName, oss2.Bucket)
            else self.getBucketByName(bucketOrBucketName)
        )

    def getBucketByName(self, bucketName=None):
        return (
            oss2.Bucket(self.auth, self.endpoint, bucketName)
            if bucketName
            else self.bucket
        )

    def _getObjectNames(self, objects):
        return (
            [obj.key for obj in objects]
            if isinstance(objects, (tuple, list))
            else objects.key
        )
