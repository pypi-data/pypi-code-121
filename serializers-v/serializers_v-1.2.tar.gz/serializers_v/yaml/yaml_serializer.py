from serializers_v.json import parser
from serializers_v.src.serializer import *


class YamlSerializer:

    @staticmethod
    def dumps(item):
        return str(serialize(item)).replace("\n", "\\n")

    @staticmethod
    def dump(item, file):
        file.write(YamlSerializer.dumps(item))

    @staticmethod
    def loads(item):
        return deserialize(parser.json_parser(item.replace("\\n", "\n")))

    @staticmethod
    def load(file):
        return YamlSerializer.loads(file.read())