import inspect
import pathlib
import shutil
from os import path

BASE_PATH = "tests/working_dir"


def setup_module(module):
    if path.exists(path.join(BASE_PATH, module.__name__)):
        shutil.rmtree(path.join(BASE_PATH, module.__name__))


def get_test_folder(test_method: str) -> pathlib.Path:
    stack_frame = inspect.stack()[1]
    calling_module = inspect.getmodule(stack_frame[0])
    if calling_module is None:
        raise RuntimeError("Failed to get calling_module")
    print(calling_module.__name__)

    return pathlib.Path(BASE_PATH, calling_module.__name__, test_method)
