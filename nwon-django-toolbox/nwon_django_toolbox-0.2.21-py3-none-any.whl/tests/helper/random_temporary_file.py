import tempfile
from typing import Optional


def get_random_tempfile_path(suffix: Optional[str] = None, delete: bool = False) -> str:
    """
    Creates a temporary file and returns the path of it.

    The file is located in the temp folder of your operating system.
    """

    if suffix is not None:
        temp_file = tempfile.NamedTemporaryFile(delete=delete, suffix=f".{suffix}")
    else:
        temp_file = tempfile.NamedTemporaryFile(
            delete=delete,
        )

    return temp_file.name


__all__ = ["get_random_tempfile_path"]
