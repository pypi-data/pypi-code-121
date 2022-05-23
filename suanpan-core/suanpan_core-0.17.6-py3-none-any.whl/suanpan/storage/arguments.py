# coding=utf-8
from __future__ import absolute_import, print_function

import os
from suanpan import path, runtime, g
from suanpan.arguments import Arg
from suanpan.components import Result
from suanpan.storage import storage
from suanpan.log import logger
from suanpan.utils import csv, excel, image, json, npy, text


class StorageArg(Arg):
    def getOutputTmpValue(self, *args):
        return storage.delimiter.join(args)


class NameFile(StorageArg):
    def __init__(self, key, **kwargs):
        self.objectPrefix = None  # oss path to save file
        self.filePath = None
        super().__init__(key, **kwargs)

    @property
    def isSet(self):
        return True

    def load(self, args):
        super().load(args)
        if self.value:
            self.objectPrefix = self.value
        return self

    def transform(self, value):
        # self.filePath = storage.getPathInTempStore(value)
        return value

    def clean(self):
        if self.filePath:
            path.remove(self.filePath)
            logger.debug("remove file {}".format(self.filePath))
            self.filePath = None
        return self

    def save(self, result):
        file_path = result.value
        file_name = os.path.basename(file_path)
        if not file_name:
            logger.warn(f"invalid filename: {file_path}")
            return None

        object_name = storage.storagePathJoin(self.objectPrefix, file_name)
        storage.upload(object_name, file_path)
        self.filePath = file_path
        self.logSaved(object_name)
        return object_name


class File(StorageArg):
    FILENAME = "file"
    FILETYPE = None

    def __init__(self, key, **kwargs):
        fileName = kwargs.pop("name", self.FILENAME)
        fileType = kwargs.pop("type", self.FILETYPE)
        self.fileName = f"{fileName}.{fileType.lower()}" if fileType else fileName
        self.objectPrefix = None
        self.objectName = None
        self.filePath = None
        super().__init__(key, **kwargs)

    @property
    def isSet(self):
        return True

    def load(self, args):
        super().load(args)
        if self.value:
            self.value = self.value.replace('{{userId}}', g.userId).replace('{{appId}}', g.appId)
            self.objectPrefix = self.value
            self.objectName = storage.storagePathJoin(self.objectPrefix, self.fileName)
            self.filePath = storage.getPathInTempStore(self.objectName)
            self.value = self.filePath
        return self

    def transform(self, value):
        if self.filePath:
            _download = (
                storage.download if self.required else runtime.saferun(storage.download)
            )
            _download(self.objectName, self.filePath)
        return self.filePath

    def clean(self):
        if self.filePath:
            path.remove(self.filePath)
            logger.debug("clean folder from {} to {}".format(self.filePath, storage.tempStore))
            path.removeEmptyFoldersTo(os.path.dirname(self.filePath), storage.tempStore)
        return self

    def save(self, result):
        filePath = result.value
        storage.upload(self.objectName, filePath)
        if filePath != self.filePath:
            path.remove(filePath)
        self.logSaved(self.objectName)
        return self.objectPrefix


class Folder(StorageArg):
    def __init__(self, key, **kwargs):
        super().__init__(key, **kwargs)
        self.folderName = None
        self.folderPath = None

    @property
    def isSet(self):
        return True

    def load(self, args):
        super().load(args)
        if self.value:
            self.value = self.value.replace('{{userId}}', g.userId).replace('{{appId}}', g.appId)
            self.folderName = self.value
            self.folderPath = storage.getPathInTempStore(self.folderName)
            self.value = self.folderPath
        return self

    def transform(self, value):
        if self.folderPath:
            _download = (
                storage.download if self.required else runtime.saferun(storage.download)
            )
            _download(self.folderName, self.folderPath)
        return self.folderPath

    def clean(self):
        if self.folderPath:
            path.empty(self.folderPath)
        return self

    def save(self, result):
        folderPath = result.value
        storage.upload(self.folderName, folderPath)
        if folderPath != self.folderPath:
            path.remove(folderPath)
        self.logSaved(self.folderName)
        return self.folderName


class Data(File):
    FILENAME = "data"


class Json(Data):
    FILETYPE = "json"

    def transform(self, value):
        filePath = super().transform(value)
        if not filePath:
            return None
        _load = json.load if self.required else runtime.saferun(json.load)
        return _load(filePath)

    def save(self, result):
        path.mkdirs(self.filePath, parent=True)
        json.dump(result.value, self.filePath)
        return super().save(Result.froms(value=self.filePath))


class Csv(Data):
    FILETYPE = "csv"

    def cleanParams(self, params):
        params = super().cleanParams(params)
        return {k: v for k, v in params.items() if k not in ("table", "partition")}

    def transform(self, value):
        filePath = super().transform(value)
        if not filePath:
            return None
        _load = csv.load if self.required else runtime.saferun(csv.load)
        return _load(filePath)

    def save(self, result):
        path.mkdirs(self.filePath, parent=True)
        csv.dump(result.value, self.filePath)
        return super().save(Result.froms(value=self.filePath))


class Table(Csv):
    pass


class Excel(Data):
    FILETYPE = "xlsx"
    LEGACY_FILETYPE = "xls"

    def __init__(self, key, **kwargs):
        self.fileTypeSet = kwargs.get("type") is not None
        super().__init__(key, **kwargs)

    def load(self, args):
        super().load(args)
        if not self.objectName:
            self.value = self.filePath
            return self

        if not storage.isFile(self.objectName) and not self.fileTypeSet:
            fileType = self.LEGACY_FILETYPE
            self.fileName = "{}.{}".format(self.fileName.split(".")[0], fileType)
            self.objectName = storage.storagePathJoin(self.objectPrefix, self.fileName)
        self.filePath = storage.getPathInTempStore(self.objectName)
        path.safeMkdirsForFile(self.filePath)
        self.value = self.filePath
        return self

    def transform(self, value):
        value = super().transform(value)
        if self.filePath:
            _load = excel.load if self.required else runtime.saferun(excel.load)
            value = _load(self.filePath)
        return value

    def save(self, result):
        path.mkdirs(self.filePath, parent=True)
        excel.dump(result.value, self.filePath)
        return super().save(Result.froms(value=self.filePath))


class Npy(Data):
    FILETYPE = "npy"

    def transform(self, value):
        filePath = super().transform(value)
        if not filePath:
            return None
        _load = npy.load if self.required else runtime.saferun(npy.load)
        return _load(filePath)

    def save(self, result):
        path.mkdirs(self.filePath, parent=True)
        npy.dump(result.value, self.filePath)
        return super().save(Result.froms(value=self.filePath))


class String(Data):
    FILETYPE = "txt"

    def transform(self, value):
        filePath = super().transform(value)
        if not filePath:
            return None
        _load = text.load if self.required else runtime.saferun(text.load)
        return _load(filePath)

    def save(self, result):
        path.mkdirs(self.filePath, parent=True)
        text.dump(result.value, self.filePath)
        return super().save(Result.froms(value=self.filePath))


class Visual(String):
    FILENAME = "part-00000"
    FILETYPE = ""


class Model(File):
    FILENAME = "model"


class H5Model(Model):
    FILETYPE = "h5"


class Checkpoint(Model):
    FILETYPE = "ckpt"


class JsonModel(Model):
    FILETYPE = "json"


class Image(File):
    FILENAME = "image"
    FILETYPE = "png"

    def transform(self, value):
        filePath = super().transform(value)
        if not filePath:
            return None
        _read = image.read if self.required else runtime.saferun(image.read)
        return _read(filePath)

    def save(self, result):
        image.save(self.filePath, result.value)
        return super().save(Result.froms(value=self.filePath))


class Screenshots(Image):
    FILENAME = "screenshots"
