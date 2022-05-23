# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan import error, path, runtime
from suanpan.state.base import IndexSaver, Saver, TimeSaver
from suanpan.storage import storage


class StorageSaver(Saver):
    PATTERN = None

    def __init__(self, name, **kwargs):
        super().__init__(storageName=name, **kwargs)

    @property
    def currentPattern(self):
        _pattern = self.current.pattern or self.PATTERN
        if not _pattern:
            raise error.StateError("Pattern is not set!")
        return _pattern.format(**self.current)

    def update(self):
        self.current.localPath = storage.getPathInTempStore(self.current.storageName)
        storageName = storage.storagePathJoin(
            self.current.storageName, self.currentPattern
        )
        localPath = storage.localPathJoin(self.current.localPath, self.currentPattern)
        return storage.upload(storageName, localPath)

    def clean(self):
        self.current.localPath = storage.getPathInTempStore(self.current.storageName)
        runtime.saferun(storage.remove)(self.current.storageName)
        return path.remove(self.current.localPath)


class StorageIndexSaver(StorageSaver, IndexSaver):
    pass


class StorageTimeSaver(StorageSaver, TimeSaver):
    pass
