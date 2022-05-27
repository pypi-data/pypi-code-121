__author__ = 'Lene Preuss <lene.preuss@gmail.com>'

import json
import pickle
from bz2 import open as bzopen
from gzip import open as gzopen
from lzma import open as xzopen
from typing import Callable, Dict

OPEN_FUNCTIONS: Dict[str, Callable] = {
    'bz2': bzopen,
    'gz': gzopen,
    'xz': xzopen,
}
DUMP_PARAMS: Dict[str, Dict] = {
    'json': {'dump': json.dump, 'mode': 'wt', 'kwargs': dict(default=str)},
    'pickle': {'dump': pickle.dump, 'mode': 'wb', 'kwargs': {}}
}


def open_function(extension: str) -> Callable:
    return OPEN_FUNCTIONS.get(extension, open)


def dump_data(user_data: Dict, backup_filename: str) -> None:
    filename_parts = backup_filename.split('.')
    extension = filename_parts[-1].lower()
    dump_format = extension if extension in DUMP_PARAMS else filename_parts[-2].lower()
    dump_params = DUMP_PARAMS.get(dump_format, DUMP_PARAMS['pickle'])
    dump_func = dump_params['dump']
    mode = dump_params['mode']
    kwargs = dump_params['kwargs']
    with open_function(extension)(backup_filename, mode) as backup_file:
        dump_func(user_data, backup_file, **kwargs)
