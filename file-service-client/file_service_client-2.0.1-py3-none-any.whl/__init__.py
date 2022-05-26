__version__ = "2.0.1"

__all__ = [
    "FileServiceClient",
    "FileStoreServiceClient",
    "FileDefinitionModel",
    "FileResourceModel",
]

try:
    # Attempts to import the client class
    # Allowed to fail importing so the package metadata can be read for building
    from .file_service_client import FileServiceClient
    from .file_store_client import FileStoreServiceClient
    from .models import FileDefinitionModel, FileResourceModel
except (ImportError, ModuleNotFoundError):  # pragma: no cover
    pass  # pragma: no cover
