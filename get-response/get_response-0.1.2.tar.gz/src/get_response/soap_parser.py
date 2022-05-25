import re
import xml.etree.ElementTree as ET

from get_response.base_parser import BaseParser
from get_response.base_parser import T_GET_OBJECTS


class SoapParser(BaseParser):

    def __init__(self, obj: str) -> None:
        super().__init__(obj)
        self._obj_xml = ET.fromstring(
            self._prepare_obj(obj))

    def get_objects(self, field: str) -> T_GET_OBJECTS:
        """Parsing a serialized by ElementTree object."""
        fields_found = []

        for children in self._obj_xml.iter():
            current_tag = children.tag
            tag_name = current_tag[current_tag.find('}') + 1::]

            if tag_name == field:
                for text in children.itertext():
                    print(repr(text))
                    fields_found.append(text)

        return tuple(fields_found)

    @staticmethod
    def _prepare_obj(obj: str) -> str:
        result = re.sub(r">(?:\W+)<", r"><", obj)
        return result.strip()
