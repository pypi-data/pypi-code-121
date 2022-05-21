from serializers_v.json.parser import json_parser
from serializers_v.src.serializer import serialize, deserialize


class JsonSerializer:

    @staticmethod
    def dumps(item):
        return str(serialize(item)).replace("\n", "\\n")

    @staticmethod
    def dump(item, file):
        file.write(JsonSerializer.dumps(item))

    @staticmethod
    def loads(item):
        return deserialize(json_parser(item.replace("\\n", "\n")))

    @staticmethod
    def load(file):
        return JsonSerializer.loads(file.read())