from serializers_v.toml.parser import parser_to_toml, parser_to_dict
from serializers_v.src.serializer import serialize, deserialize


class TomlSerializer:

    @staticmethod
    def dumps(item):
        return parser_to_toml(serialize(item)).replace("\n", "\\n")

    @staticmethod
    def dump(item, file):
        file.write(TomlSerializer.dumps(item))

    @staticmethod
    def loads(item):
        return deserialize(parser_to_dict(item.replace("\\n", "\n")))

    @staticmethod
    def load(file):
        return TomlSerializer.loads(file.read())