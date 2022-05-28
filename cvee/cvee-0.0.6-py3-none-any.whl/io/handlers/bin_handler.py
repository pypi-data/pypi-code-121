import numpy as np

from cvee.io.handlers.base import BaseFileHandler


# TODO: write test cases
class BinHandler(BaseFileHandler):
    def load_from_fileobj(self, file, **kwargs):
        return file.read()

    def save_to_fileobj(self, file, obj, **kwargs):
        file.write(obj)

    def load_from_path(self, filepath, **kwargs):
        with open(filepath, "rb") as f:
            return self.load_from_fileobj(f, **kwargs)

    def save_to_path(self, filepath, obj, **kwargs):
        with open(filepath, "wb") as f:
            self.save_to_fileobj(f, obj, **kwargs)
