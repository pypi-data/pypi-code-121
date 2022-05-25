import os

def update_path_in_bat_file(filepath: str, path_addition: str) -> None:
    """Add a line for path updates to the specified file

    :param str filepath: The path to the file to update
    :param str path_addition: The folder to add to the path variable

    :raises FileNotFoundError: if the path getting added is not valid 
    """
    _verify_folders(filepath=filepath, path_addition=path_addition)

    with open(filepath, 'a', encoding='utf8') as f:
        f.write(f'\nset "PATH={path_addition};%PATH%"\n')


def update_path_in_base_file(filepath: str, path_addition: str) -> None:
    """Add linux path updates to the specified file

    :param str filepath: The path to the file to update
    :param str path_addition: The folder to add to the path variable

    :raises FileNotFoundError: if the path getting added is not valid 
    """

    _verify_folders(filepath=filepath, path_addition=path_addition)

    with open(filepath, 'a', encoding='utf8') as f:
        f.write('\nPATH="' + path_addition.replace("\\", "/")+';$PATH"\nexport PATH\nhash -r 2>/dev/null\n')


def _verify_folders(filepath: str, path_addition: str) -> None:
    """check the specified folders

    :param str filepath: The path to the file to update
    :param str path_addition: The folder to add to the path variable

    :raises FileNotFoundError: if the path getting added is not valid 
    """

    if not os.path.isdir(path_addition):
        raise FileNotFoundError(f"Path '{path_addition}' is not a folder")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Bat file '{filepath}' does not exist")