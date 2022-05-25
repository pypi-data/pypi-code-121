import os


def check_if_file_exists(file_path: str) -> None:
    """Static method checking whether a file exists. If not, then a FileNotFoundError is raised.

    :param file_path: a path to a file whose presence is verified.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError("The file %s does not exist!" % file_path)
