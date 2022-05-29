import os
import os.path
import importlib


def get_name():
    mod = importlib.import_module("config.project")
    if hasattr(mod, "name"):
        return getattr(mod, "name")
    return os.path.basename(os.getcwd())
