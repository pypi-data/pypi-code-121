import os
from pathlib import Path


def check_if_file_exists(file_path: str) -> None:
    """function checking whether a file exists. If not, then a FileNotFoundError is raised.

    :param file_path: a path to a file whose presence is verified.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError("The file %s does not exist!" % file_path)


def create_directory_if_nonexistent(output_dir: Path) -> None:
    """Function checking whether a directory exists, if not then it is created

    :param output_dir: a path to an output directory
    """
    is_dir = Path(output_dir).is_dir()
    if not is_dir:
        os.mkdir(output_dir)
