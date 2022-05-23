import os
from . import formats
import re


def guess_extension(file_name, use_file_name=False):
    """
    Returns the file format. It can either use the file name extension or
    guess based on signatures found in the file.

    Parameters
    ----------
    file_name: str
        Name of the file

    use_file_name: bool, optional, default: False
        If set to True, uses the file name extension to identify the
        file format.

    Returns
    -------
    extension: str
        The file format.
    """

    if use_file_name is True:
        (root, ext) = os.path.splitext(file_name)

        if ext == "":
            return None

        return ext.lower()

    available_extensions = formats.registries.REGISTERED_FORMAT_CHECKERS.keys()

    for extension in available_extensions:

        extension_checker = formats.registries.REGISTERED_FORMAT_CHECKERS[extension]

        if extension_checker(file_name) is True:
            return extension


def sanitize_file_format(file_format):
    """
    Returns a uniform file format string.

    Parameters
    ----------
    file_format: str
        Extension of the file.

    Returns
    -------
    file_format: str
        The sanitized file format.
    """

    if re.match(r"^\.?[a-zA-Z\d]+$", file_format) is None:
        raise NameError(
            "read_structure_step: the file format %s could not be validated"
            % file_format
        )

    file_format = file_format.lower()

    if file_format.startswith(".") is False:
        file_format = "." + file_format

    return file_format
