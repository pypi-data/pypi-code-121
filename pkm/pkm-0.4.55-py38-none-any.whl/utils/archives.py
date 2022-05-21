import tarfile
from io import UnsupportedOperation
from pathlib import Path
from zipfile import ZipFile

from pkm.utils.strings import endswith_any


def extract_archive(archive_path: Path, target_directory: Path):
    target_directory.mkdir(exist_ok=True, parents=True)

    if endswith_any(archive_path.name, (".zip", '.whl')):
        with ZipFile(archive_path) as z:
            z.extractall(target_directory)
    elif archive_path.name.endswith('.tar.gz'):
        with tarfile.open(archive_path) as tar:
            tar.extractall(target_directory)
    elif archive_path.name.endswith(".tar.bz2"):
        with tarfile.open(archive_path, 'r:bz2') as tar:
            tar.extractall(target_directory)
    else:
        raise UnsupportedOperation(f"does not support archive {archive_path.name}")
