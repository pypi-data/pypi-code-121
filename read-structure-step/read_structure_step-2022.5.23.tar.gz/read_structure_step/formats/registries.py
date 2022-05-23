"""
This module contains the decorator definitions to register a reader for
a given file format and its corresponding format checker. The decorators
will automatically add the decorated function to a dictionary to ease
extensibility.

Attributes
----------
REGISTERED_READERS : dict(str, dict(str, str))
    The registry of file formats that can be read. Each entry, which is keyed by the
    extension including the initial dot, is a dictionary with at least the following:
         "function": the function to call to read the file.
         "description": the readable name for the format, e.g. "MDL structure-data file"

REGISTERED_FORMAT_CHECKERS : dict(str, function)
    The registry of functions for checking is an unknown file has a given format.

FORMAT_METADATA : dict(str, dict(str, str))
    Metadata describing a file format.
"""

REGISTERED_READERS = {}
REGISTERED_WRITERS = {}
REGISTERED_FORMAT_CHECKERS = {}
FORMAT_METADATA = {}
default_metadata = {
    "single_structure": True,
    "dimensionality": 0,
    "coordinate_dimensionality": 3,
    "property_data": False,
    "bonds": False,
    "is_complete": True,
    "add_hydrogens": False,
}


def register_reader(file_format):

    tmp = file_format.split()
    extension = tmp[0]
    if extension[0] != ".":
        extension = "." + extension
    if len(tmp) == 1:
        description = ""
    else:
        if tmp[1] == "--":
            description = " ".join(tmp[2:])
        else:
            description = " ".join(tmp[1:])

    def decorator_function(fn):

        REGISTERED_READERS[extension] = {"function": fn, "description": description}

        def wrapper_function(*args, **kwargs):
            return fn(*args, **kwargs)

        return wrapper_function

    return decorator_function


def register_writer(file_format):
    """A decorator for registering structure file writers."""
    tmp = file_format.split()
    extension = tmp[0]
    if extension[0] != ".":
        extension = "." + extension
    if len(tmp) == 1:
        description = ""
    else:
        if tmp[1] == "--":
            description = " ".join(tmp[2:])
        else:
            description = " ".join(tmp[1:])

    def decorator_function(fn):
        REGISTERED_WRITERS[extension] = {"function": fn, "description": description}

        def wrapper_function(*args, **kwargs):
            return fn(*args, **kwargs)

        return wrapper_function

    return decorator_function


def register_format_checker(file_format):
    def decorator_function(fn):

        REGISTERED_FORMAT_CHECKERS[file_format] = fn

        def wrapper_function(*args, **kwargs):
            return fn(*args, **kwargs)

        return wrapper_function

    return decorator_function


def get_format_metadata(extension):
    """Return the metadata for a given extension.

    Parameters
    ----------
    extension : str
        The file format extension, including dot.

    Returns
    -------
    dict(str, any)
        The metadata as a dictionary.
    """
    if extension in FORMAT_METADATA:
        return {**FORMAT_METADATA[extension]}
    else:
        return {**default_metadata}


def set_format_metadata(extensions, **kwargs):
    """Set the metadata for the given extensions.

    Parameters
    ----------
    extensions : str or iterable
        Either a single extension as a string or a lost of extensions that this
        metadata applies to.
    **kwargs :
        Keyword arguments giving the metadata.
    """
    # Check that the keywords are valid
    for key in kwargs.keys():
        if key not in default_metadata:
            raise KeyError(f"Unknown key '{key}' in file format metadata.")

    metadata = {**default_metadata}
    metadata.update(kwargs)

    if isinstance(extensions, str):
        FORMAT_METADATA[extensions] = metadata
    else:
        for extension in extensions:
            FORMAT_METADATA[extension] = metadata


def last_resort_reader(formats, fn):
    """Sets the reader for a list of formats if there is no reader registered.

    Parameters
    ----------
    formats : (str)
        An iterable list of formats handled by the function of last resort.
    fn : function
        The function of last resort.
    """
    for format in formats:
        tmp = format.split()
        extension = tmp[0]
        if extension[0] != ".":
            extension = "." + extension
        if len(tmp) == 1:
            description = ""
        else:
            if tmp[1] == "--":
                description = " ".join(tmp[2:])
            else:
                description = " ".join(tmp[1:])

        if extension not in REGISTERED_READERS:
            REGISTERED_READERS[extension] = {"function": fn, "description": description}


def last_resort_writer(formats, fn):
    """Sets the writer for a list of formats if there is no writer registered.

    Parameters
    ----------
    formats : (str)
        An iterable list of formats handled by the function of last resort.
    fn : function
        The function of last resort.
    """
    for format in formats:
        tmp = format.split()
        extension = tmp[0]
        if extension[0] != ".":
            extension = "." + extension
        if len(tmp) == 1:
            description = ""
        else:
            if tmp[1] == "--":
                description = " ".join(tmp[2:])
            else:
                description = " ".join(tmp[1:])

        if extension not in REGISTERED_WRITERS:
            REGISTERED_WRITERS[extension] = {"function": fn, "description": description}


def last_resort_checker(format, fn):
    """Sets the reader for a list of formats if there is no reader registered.

    Parameters
    ----------
    format : str
        File extension indicating format, e.g. '.pdb'
    fn : function
        The function that checks the file
    """
    tmp = format.split()
    extension = tmp[0]
    if extension[0] != ".":
        extension = "." + extension

    if extension not in REGISTERED_FORMAT_CHECKERS:
        REGISTERED_FORMAT_CHECKERS[extension] = fn
