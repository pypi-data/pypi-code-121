import pickle

from cvee.io.handlers.base import BaseFileHandler


class PickleHandler(BaseFileHandler):
    def load_from_fileobj(self, file, **kwargs):
        return pickle.load(file)

    def save_to_fileobj(self, file, obj, **kwargs):
        pickle.dump(obj, file)

    def load_from_path(self, filepath, **kwargs):
        return super(PickleHandler, self).load_from_path(filepath, mode="rb", **kwargs)

    def save_to_path(self, filepath, obj, **kwargs):
        return super(PickleHandler, self).save_to_path(filepath, obj, mode="wb", **kwargs)
