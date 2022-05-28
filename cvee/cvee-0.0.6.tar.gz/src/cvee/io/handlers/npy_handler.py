import numpy as np

from cvee.io.handlers.base import BaseFileHandler


# TODO: write test cases
class NpyHandler(BaseFileHandler):
    def load_from_fileobj(self, file, **kwargs):
        return np.load(file, allow_pickle=True)

    def save_to_fileobj(self, file, obj, **kwargs):
        np.save(file, obj)

    def load_from_path(self, filepath, **kwargs):
        return np.load(filepath, allow_pickle=True)

    def save_to_path(self, filepath, obj, **kwargs):
        np.save(filepath, obj)
