import yaml
from cvee.io.handlers.base import BaseFileHandler


class YAMLHandler(BaseFileHandler):
    def load_from_fileobj(self, file, **kwargs):
        return yaml.safe_load(file)

    def save_to_fileobj(self, file, obj, **kwargs):
        yaml.safe_dump(obj, file)
