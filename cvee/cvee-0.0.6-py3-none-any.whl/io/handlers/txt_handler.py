from cvee.io.handlers.base import BaseFileHandler


class TXTHandler(BaseFileHandler):
    def load_from_fileobj(self, file, **kwargs):
        return file.read()

    def save_to_fileobj(self, file, obj, **kwargs):
        if isinstance(obj, str):
            file.write(obj)
        else:
            raise TypeError("TXTHandler currently only supports save pure str")
