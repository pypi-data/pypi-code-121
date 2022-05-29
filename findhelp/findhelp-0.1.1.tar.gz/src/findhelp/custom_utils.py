import re
from typing import Union
from unidecode import unidecode

from findhelp.custom_exceptions import NotEqualLengthError


def sel_arg(arg_dict: dict, arg_search: str):
    """Selects a single element from a dictionary. Returns None if key doesn't exist

    Args:
        arg_dict (dict): Dictionary where key will be searched
        arg_search (str): Key to search for

    Returns:
        object: Element stored in arg_dict[arg_search]. None if key doesn't exist
    """
    if arg_search in arg_dict.keys():
        return arg_dict[arg_search]
    return None


def search_in_list(
        base_list: list, value: Union[str, re.Pattern], ignore_case: bool = False, ignore_accents: bool = True):
    """Search for matches in a list

    Selects the elements within a list that match with a string / regular expression pattern

    Args:
        base_list (list): List in which value will be searched
        value (Union[str, re.Pattern]): String / re.Pattern to search for
        ignore_case (bool, optional): Indicates if upper / lower case is ignored.
            Just for searching purposes, result will consider the actual characters of each coincidence. Defaults to False.
        ignore_accents (bool, optional): Indicates if accent characters must be turned into non-accented ones. 
            Just for searching purposes, result will consider the actual characters of each coincidence. Defaults to True.

    Returns:
        list[str]: List with all coincidences found, respecting ortography (e.g. accents, upper/lowercase)
    """

    if ignore_accents:
        base_new = [unidecode(
            str(element)) for element in base_list]
    else:
        base_new = base_list[:]

    # indexes
    if not ignore_case:
        if isinstance(value, re.Pattern):
            indexes = [index for index, item in enumerate(
                base_new) if value.search(str(item))]
        else:
            indexes = [index for index, item in enumerate(
                base_new) if value in str(item)]

    else:
        if isinstance(value, re.Pattern):
            indexes = [index for index, item in enumerate(
                base_new) if value.search(str(item).lower())]
        else:
            indexes = [index for index, item in enumerate(
                base_new) if value.lower() in str(item).lower()]

    return [element for index, element in enumerate(base_list) if index in indexes]


def forcedir_sep(path: str, dir_sep: str) -> str:
    """Forces separators to be a specific one

    Args:
        path (str): string path in which separators will be replaced
        dir_sep (str): separator

    Returns:
        str: path string with a single unified separator
    """
    return path.replace("\\\\", dir_sep).replace("\\", dir_sep).replace("/", dir_sep)


def join_result(output_type: str, defaultdir_sep: str, fullpath: str, type: str,
                folder_parent: str, folder_name: str, file_name: str = None,
                ext: str = None):
    """Joins a single found coincidence into a list / dict

    Args:
        output_type (str): Indicates if join must be made using 'list' or 'dict'
        defaultdir_sep (str): Separator to force all paths to have the same one
        fullpath (str): Folder in which the actual coincidence was found. fullpath = folder_parent + folder_name
        type (str): Indicates if the coincidence is a 'folder' or a 'file'
        folder_parent (str): Path to 'fullpath' parent. For filtering purposes.
        folder_name (str): Name of the folder in which the coincidence was fount. For filtering purposes.
        file_name (str, optional): Filename of the coincidence, if applicable (if type != 'folder'). Defaults to None.
        ext (str, optional): Filename extension of the coincidence, if applicable (if type != 'folder'). Defaults to None.

    Returns:
        list | dict: An list / dictionary with each of the elements, ready to join with other found coincidences
    """
    fullpath = forcedir_sep(fullpath, defaultdir_sep)
    folder_parent = forcedir_sep(folder_parent, defaultdir_sep)

    if output_type == "dict":
        return {
            "fullpath": fullpath,
            "type": type,
            "folder_parent": folder_parent,
            "folder_name": folder_name,
            "file_name": file_name,
            "ext": ext
        }
    elif output_type == "list":
        return [
            fullpath,
            type,
            folder_parent,
            folder_name,
            file_name,
            ext
        ]
    return None


def parse_line(line: list, max_len: list) -> str:
    """Builds a string from a list of strings, justifying each element using spaces

    Args:
        line (list): List of strings to justify
        max_len (list): List of lengths for each string

    Raises:
        NotEqualLengthError: Raised if len(line) and len(max_len) are different

    Returns:
        str: string resulting from justifying each of the strings within 'line',
            and putting all of them together
    """
    str_result = ""
    if len(line) != len(max_len):
        raise NotEqualLengthError(message="Lists lengths are not equal")

    for index in range(len(line)):
        str_result += str(line[index]).ljust(max_len[index])

    return str_result


def find_len(string) -> int:
    """Gets the length of a string. 0 if string is None

    Args:
        string (str): String to calculate len

    Returns:
        int: Len of the string
    """
    if string:
        string = str(string)
    else:
        string = ""

    return len(string)


def force_filename(filename: str) -> str:
    return re.sub('[^\w_.)( -]', '', filename)


def default_ignore_folders():
    """Gets default ignore folders

    Returns:
        list: Default list of folders to ignore in future searchs.
    """
    return [
        "site-packages",
        ".git",
        "$RECYCLE.BIN",
        "node_modules",
        "__pycache__",
        ".vscode",
    ]
