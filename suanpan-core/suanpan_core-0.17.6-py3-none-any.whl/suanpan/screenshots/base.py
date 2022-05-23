# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan import path, runtime
from suanpan.state.base import IndexSaver, TimeSaver
from suanpan.state.storage import StorageSaver
from suanpan.storage import storage
from suanpan.utils import image


class ScreenshotsSaver(StorageSaver):
    def update(self, imageOrPath):
        data = image.read(imageOrPath) if isinstance(imageOrPath, str) else imageOrPath
        self.current.localPath = storage.getPathInTempStore(self.current.storageName)
        storageName = storage.storagePathJoin(
            self.current.storageName, self.currentPattern
        )
        localPath = storage.localPathJoin(self.current.localPath, self.currentPattern)
        image.save(localPath, data, self.current.get("flag"))
        return storage.upload(storageName, localPath)


class ScreenshotsWithThumbnailSaver(StorageSaver):
    WIDTH = 74

    def update(self, imageOrPath):
        data = image.read(imageOrPath) if isinstance(imageOrPath, str) else imageOrPath
        thumbnailData = self.resize(data)

        self.saveScreenshot(
            thumbnailData,
            self.current.thumbnail,
            self.currentPattern,
            self.current.get("flag"),
        )

        return self.saveScreenshot(
            data,
            self.current.storageName,
            self.currentPattern,
            self.current.get("flag"),
        )

    def clean(self):
        for storageName in [self.current.storageName, self.current.thumbnail]:
            self._clean(storageName)

    def resize(self, data):
        height, width = data.shape[0], data.shape[1]
        ratio = float(width) / self.WIDTH
        if ratio <= 1:
            return data

        return image.resize(data, size=(int(width / ratio), int(height / ratio)))

    def saveScreenshot(self, data, storageName, pattern, flag):
        tempPath = storage.getPathInTempStore(storageName)
        storageName = storage.storagePathJoin(storageName, pattern)
        localPath = storage.localPathJoin(tempPath, pattern)

        image.save(localPath, data, flag)
        storage.upload(storageName, localPath)

    def _clean(self, storageName):
        localPath = storage.getPathInTempStore(storageName)
        runtime.saferun(storage.remove)(storageName)
        return path.remove(localPath)


class ScreenshotsIndexSaver(ScreenshotsWithThumbnailSaver, IndexSaver):
    PATTERN = "screenshot_{index}.png"


class ScreenshotsTimeSaver(ScreenshotsWithThumbnailSaver, TimeSaver):
    PATTERN = "screenshot_{time}.png"
