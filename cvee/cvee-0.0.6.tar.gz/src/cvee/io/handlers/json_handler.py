import json
from cvee.io.handlers.base import BaseFileHandler


class JSONHandler(BaseFileHandler):
    def load_from_fileobj(self, file, **kwargs):
        return json.load(file)

    def save_to_fileobj(self, file, obj, **kwargs):
        json.dump(obj, file)
