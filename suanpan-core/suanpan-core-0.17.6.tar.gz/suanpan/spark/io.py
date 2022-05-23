# coding=utf-8
from __future__ import absolute_import, print_function

from contextlib import contextmanager

from suanpan import error

OSS_BUCKET_NAME_CONF = "spark.hadoop.fs.oss.bucketName"


def getStorageHost(spark):
    ossBucketName = spark.sparkContext._conf.get(  # pylint: disable=protected-access
        OSS_BUCKET_NAME_CONF
    )
    if not ossBucketName:
        raise error.SparkError(f"Config {OSS_BUCKET_NAME_CONF} not found")
    return f"oss://{ossBucketName}/"


def getStoragePath(spark, filepath):
    return getStorageHost(spark) + filepath


class File(object):
    def __init__(self, spark, filepath, mode="r"):
        self.spark = spark
        self.filepath = filepath
        self.mode = mode

        self.sc = self.spark.sparkContext
        self.hadoop = self.sc._jvm.org.apache.hadoop  # pylint: disable=protected-access
        self.ioUtils = (
            self.sc._jvm.org.apache.commons.io.IOUtils  # pylint: disable=protected-access
        )
        self.uri = self.sc._jvm.java.net.URI  # pylint: disable=protected-access
        self.fs = self.hadoop.fs.FileSystem
        self.conf = (
            self.sc._jsc.hadoopConfiguration()  # pylint: disable=protected-access
        )
        self.path = self.hadoop.fs.Path(filepath)
        self.fsImpl = self.fs.get(self.uri.create(self.filepath), self.conf)

        self.inputStream = self.fsImpl.open(self.path) if "r" in self.mode else None
        self.overwrite = "a" not in self.mode
        self.outputStream = (
            self.fsImpl.create(self.path, self.overwrite) if "w" in self.mode else None
        )

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.flush()
        self.close()

    def read(self, decode="utf-8"):
        if not self.inputStream:
            raise error.SparkError(f"Error mode {self.mode}")
        return self.ioUtils.toString(self.inputStream, decode)

    def readlines(self, decode="utf-8"):
        if not self.inputStream:
            raise error.SparkError(f"Error mode {self.mode}")
        return self.ioUtils.readLines(self.inputStream, decode)

    def write(self, content, encode="utf-8"):
        if not self.outputStream:
            raise error.SparkError(f"Error mode {self.mode}")
        if not isinstance(content, bytearray):
            content = bytearray(content, encode)
        self.outputStream.write(content)

    def flush(self):
        if self.outputStream:
            self.outputStream.flush()

    def close(self):
        if self.inputStream:
            self.inputStream.close()
        if self.outputStream:
            self.outputStream.close()


class MinioFile(File):
    def __init__(self, spark, filepath, mode="r"):
        filepath = getStoragePath(spark, filepath)
        super().__init__(spark, filepath, mode=mode)


@contextmanager
def open(spark, filepath, mode="r", filetype=File):
    file = filetype(spark, filepath, mode=mode)
    yield file
    file.flush()
    file.close()
