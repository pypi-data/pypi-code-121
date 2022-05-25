from aqueduct_executor.operators.utils.storages.config import StorageConfig
from aqueduct_executor.operators.utils.storages.file import FileStorage
from aqueduct_executor.operators.utils.storages.s3 import S3Storage
from aqueduct_executor.operators.utils.storages.storage import Storage


def parse_storage(storage_config: StorageConfig) -> Storage:
    if storage_config.s3_config:
        return S3Storage(storage_config.s3_config)
    if storage_config.file_config:
        return FileStorage(storage_config.file_config)
