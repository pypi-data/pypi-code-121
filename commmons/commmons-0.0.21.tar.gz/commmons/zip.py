import shutil
import zipfile

__all__ = [
    "create_zip",
    "is_valid_zip"
]


def create_zip(basename, source_dir, retry=3) -> str:
    """
    Zips the content of source_dir.
    :param basename: Name of the resulting zip file (w/o extension). Supports both Absolute and Relative.
    :param source_dir: Path to the source folder. Supports both Absolute and Relative.
    :param retry: Number of times to retry if is_valid_zip returns false.
    :return: Absolute path of the resulting zip file
    """
    zip_path = shutil.make_archive(basename, 'zip', source_dir)
    if not is_valid_zip(zip_path):
        if retry > 0:
            return create_zip(basename, source_dir, retry - 1)
        raise RuntimeError('zip is not valid')
    return zip_path


def is_valid_zip(path: str) -> bool:
    return zipfile.ZipFile(path).testzip() is None
