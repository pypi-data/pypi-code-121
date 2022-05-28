import numpy as np
from cvee.io.handlers.base import BaseFileHandler


# TODO: write test cases
class NpzHandler(BaseFileHandler):
    def load_from_fileobj(self, file, **kwargs):
        return np.load(file, allow_pickle=True)

    def save_to_fileobj(self, file, obj, compressed=True, **kwargs):
        func = np.savez_compressed if compressed else np.savez

        if isinstance(obj, dict):
            func(file, **obj)
        elif isinstance(obj, list) or isinstance(obj, tuple):
            func(file, *obj)
        else:
            func(file, obj)

    def load_from_path(self, filepath, **kwargs):
        return np.load(filepath, allow_pickle=True)

    def save_to_path(self, filepath, obj, compressed=True, **kwargs):
        func = np.savez_compressed if compressed else np.savez

        if isinstance(obj, dict):
            func(filepath, **obj)
        elif isinstance(obj, list) or isinstance(obj, tuple):
            func(filepath, *obj)
        else:
            func(filepath, obj)
