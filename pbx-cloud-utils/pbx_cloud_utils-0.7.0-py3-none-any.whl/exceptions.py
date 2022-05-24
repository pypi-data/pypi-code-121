class StorageError(Exception):
    """
    Base storage error.
    """


class UnsupportedStorageClassError(StorageError):
    def __init__(self, storage_class_name, *args):
        message = f"Unsupported storage class: {storage_class_name}"
        super().__init__(message, *args)
