import abc


class BaseFileHandler(abc.ABC):
    @abc.abstractmethod
    def load_from_fileobj(self, file, **kwargs):
        pass

    @abc.abstractmethod
    def save_to_fileobj(self, file, obj, **kwargs):
        pass

    def load_from_path(self, filepath, mode="r", **kwargs):
        with open(filepath, mode) as f:
            return self.load_from_fileobj(f, **kwargs)

    def save_to_path(self, filepath, obj, mode="w", **kwargs):
        with open(filepath, mode) as f:
            self.save_to_fileobj(f, obj, **kwargs)
