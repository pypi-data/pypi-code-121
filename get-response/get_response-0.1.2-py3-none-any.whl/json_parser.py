import json

from get_response.base_parser import BaseParser
from get_response.base_parser import T_GET_OBJECTS


class JsonParser(BaseParser):

    def __init__(self, obj: str) -> None:
        super().__init__(obj)
        self._obj_dict = json.loads(self.obj)

    def get_objects(self, field: str) -> T_GET_OBJECTS:
        """Parsing a serialized to dict json object."""
        dicts_queue = [self._obj_dict]
        fields_found = []

        for dictionary in dicts_queue:
            for key, value in dictionary.items():

                if key == field:
                    fields_found.append(value)

                elif isinstance(value, dict):
                    dicts_queue.append(value)

                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            dicts_queue.append(item)
                        if isinstance(item, list):
                            value.extend(item)

        return tuple(fields_found)
