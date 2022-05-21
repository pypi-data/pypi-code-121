from dataclasses import dataclass

from bloc_client.value_type import ValueType


@dataclass
class FunctionOpt:
    key: str
    description: str
    value_type: ValueType
    is_array: bool

    def json_dict(self):
        return {
            "key": self.key,
            "description": self.description,
            "value_type": self.value_type.value,
            "is_array": self.is_array   
        }
