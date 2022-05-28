import os
from pathlib import Path

from cvee.io.handlers.bin_handler import BinHandler
from cvee.io.handlers.geometry_handler import GeometryHandler
from cvee.io.handlers.image_handler import ImageHandler
from cvee.io.handlers.json_handler import JSONHandler
from cvee.io.handlers.npy_handler import NpyHandler
from cvee.io.handlers.npz_handler import NpzHandler
from cvee.io.handlers.pickle_handler import PickleHandler
from cvee.io.handlers.txt_handler import TXTHandler
from cvee.io.handlers.xml_handler import XMLHandler
from cvee.io.handlers.yaml_handler import YAMLHandler

file_handlers = {
    "json": JSONHandler(),
    "txt": TXTHandler(),
    "bin": BinHandler(),
    "pkl": PickleHandler(),
    "pickle": PickleHandler(),
    "yaml": YAMLHandler(),
    "yml": YAMLHandler(),
    "npy": NpyHandler(),
    "npz": NpzHandler(),
    "ply": GeometryHandler(),
    "obj": GeometryHandler(),
    "xyz": GeometryHandler(),
    "jpg": ImageHandler(),
    "jpeg": ImageHandler(),
    "png": ImageHandler(),
    "urdf": XMLHandler(),
}


def load(file, file_format=None, **kwargs):
    """Load data from file of different formats.

    This function provides a unified api for loading data from
    file of different formats.

    Args:
        file (str or Path or fileobj): Filename or a file object.
        file_format (str, optional): Use the file format to specify the file handler,
            otherwise the file format will be inferred from the file name.
            Current supported file formats: txt, json, yaml/yml, pkl/pickle,
            npy, npz, obj, ply, jpg/jpeg, png, mp4, avi.

    Returns:
        The data of the file.
    """
    if isinstance(file, Path):
        file = str(file)
    if file_format is None and not isinstance(file, str):
        raise TypeError("Format should be specified when file is not str or path")
    if file_format is None and isinstance(file, str):
        file_format = file.split(".")[-1]
    if file_format not in file_handlers:
        raise TypeError(f"Unsupported file format: {file_format}")

    file_handler = file_handlers[file_format]

    if isinstance(file, str):
        obj = file_handler.load_from_path(file, **kwargs)
    elif hasattr(file, "read"):
        obj = file_handler.load_from_fileobj(file, **kwargs)
    else:
        raise TypeError("File must be a filepath str or a file object")
    return obj


def save(file, obj, file_format=None, auto_mkdirs=False, **kwargs):
    """Save data to file of different formats.

    This function provides a unified api for saving data to
    file of different formats.

    Args:
        file (str or Path or fileobj): Filename or a file object.
        obj (any): The python object to be saved.
        file_format (str, optional): Use the file format to specify the file handler,
            otherwise the file format will be inferred from the file name.
            Current supported file formats: txt, json, yaml/yml, csv, pkl/pickle,
            npy, npz, obj, ply, jpg/jpeg, png, mp4, avi, pt.

    Returns:
        The data of the file.
    """
    if isinstance(file, Path):
        file = str(file)
    if file_format is None and not isinstance(file, str):
        raise TypeError("Format should be specified when file is not str or path")
    if file_format is None and isinstance(file, str):
        file_format = file.split(".")[-1]
    if file_format not in file_handlers:
        raise TypeError(f"Unsupported file format: {file_format}")

    if auto_mkdirs:
        if isinstance(file, str):
            os.makedirs(os.path.dirname(file), exist_ok=True)
        else:
            raise RuntimeError("Cannot mkdirs for fileobj")

    file_handler = file_handlers[file_format]

    if isinstance(file, str):
        file_handler.save_to_path(file, obj, **kwargs)
    elif hasattr(file, "write"):
        file_handler.save_to_fileobj(file, obj, **kwargs)
    else:
        raise TypeError("File must be a filepath str or a file object")
