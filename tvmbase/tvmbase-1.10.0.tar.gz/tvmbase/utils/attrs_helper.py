from typing import Type

import attrs


def convert_nested(data: dict, data_class: Type[attrs.define]):
    for field in attrs.fields(data_class):
        value = data.get(field.name)
        if isinstance(value, dict):
            data[field.name] = field.type(**value)
