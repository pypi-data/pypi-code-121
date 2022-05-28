import xml.etree.ElementTree as ET
from cvee.io.handlers.base import BaseFileHandler


class XMLHandler(BaseFileHandler):
    def load_from_fileobj(self, file, **kwargs):
        return ET.parse(file)

    def save_to_fileobj(self, file, obj, **kwargs):
        obj = ET.tostring(obj)
        file.write(obj)
