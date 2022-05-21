from typing import Any, Tuple, List

from requests.api import get


def get_file_for_upload(
    file_name: str, file_object_or_path: Any, read_mode: str = "rb"
) -> tuple:
    """
    takes file_name and file_object_or_path and formats files in a way that is acceptable to Python
    requests for multipart encoded file.
    if type(file_object_or_path) == str, then we convert to a readable object

    Args:
        file_name (str): file name to assign to file_object_or_path
        file_object_or_path (Any): should be either a file path or a readable file object
        read_mode (str, optional): only relevant if as_path == True. read mode for opening file (eg 'rb', 'r'). Defaults to 'rb'.

    Returns:
        tuple: multipart form encoded file format: ('file', (file_name, readable_file_object))
    """
    if type(file_object_or_path) == str:
        return ("file", (file_name, open(file_object_or_path, read_mode)))
    else:
        return ("file", (file_name, file_object_or_path))


def open_files(files: List[Tuple]) -> List[tuple]:
    """
    Takes a list of form [(file_name, file_path_or_object, 'r'),...], and returns a list of tuples in correct format for multipart encoded file
    Note that 'r' here is the read mode in which we want to read our file
    open_files is written so that if a user does not pass a read_mode in any of their tuples in Files, then 'r' is the default read_mode

    Args:
        files (List[Tuple]): list of form [(file_name, file_path_or_object),...]
        read_mode (str, optional): to read bytes objects, should be 'rb', to read text, should be 'r', etc. Defaults to 'rb'.

    Returns:
        List[tuple]: list in form [('file', (file_name, readable_file_object)),...]
    """
    fileList = []
    for fileTuple in files:
        if len(fileTuple) == 3:
            file_name, file_object_or_path, read_mode = fileTuple
            fileList.append(
                get_file_for_upload(file_name, file_object_or_path, read_mode=read_mode)
            )
        elif len(fileTuple) == 2:
            file_name, file_object_or_path = fileTuple
            read_mode = "r"
            fileList.append(
                get_file_for_upload(file_name, file_object_or_path, read_mode=read_mode)
            )
    return fileList


def close_files(files: List[tuple]):
    """
    closes files after we call open_files

    Args:
        files (List[tuple]): list in form [('file', (file_name, readable_file_object)),...]
    """
    for _, (file_name, file_object) in files:
        file_object.close()
