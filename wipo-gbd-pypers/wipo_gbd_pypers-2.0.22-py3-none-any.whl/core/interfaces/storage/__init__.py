from .s3 import S3Storage
from .filesystem import FSStorage
import os

_storage = None


def get_storage():
    global _storage
    if _storage:
        return _storage
    if os.environ.get('GBD_STORAGE', 'S3') != 'S3':
        _storage = FSStorage()
    else:
        _storage = S3Storage()
    return _storage
