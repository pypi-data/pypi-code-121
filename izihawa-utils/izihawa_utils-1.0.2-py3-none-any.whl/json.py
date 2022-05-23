import enum
import types
from datetime import (
    date,
    datetime,
)

from izihawa_utils.common import filter_none


class JsonSerializator:
    def __init__(self, max_serialization_depth, custom_field_processors=None, custom_type_processors=None):
        self._max_serialization_depth = max_serialization_depth
        self._custom_field_processors = custom_field_processors or {}
        self._custom_type_processors = custom_type_processors or {}

    def _process_list(self, field, depth, excludes=None, includes=None, *args, **kwargs):
        depth += 1
        if depth > self._max_serialization_depth:
            return

        r = [self.process_field(x, depth, excludes=excludes, includes=includes, *args, **kwargs) for x in field]
        return filter_none(r)

    def _process_dict(self, field, depth, excludes=None, includes=None, *args, **kwargs):
        depth += 1
        result = {}
        if depth > self._max_serialization_depth:
            return result
        for key in field:
            if excludes and key in excludes:
                continue
            if key in self._custom_field_processors:
                value = self._custom_field_processors[key](
                    field[key], depth, excludes=excludes, includes=includes, *args, **kwargs
                )
            else:
                value = self.process_field(field[key], depth, excludes=excludes, includes=includes, *args, **kwargs)
            if value is None:
                continue
            key = self.process_field(key, depth, excludes=excludes, includes=includes, *args, **kwargs)
            result[key] = value
        return result

    def process_field(self, field, depth, excludes=None, includes=None, *args, **kwargs):
        for type_, processor in self._custom_type_processors.items():
            if isinstance(field, type_):
                return processor(field, depth, excludes=excludes, includes=includes, *args, **kwargs)
        if isinstance(field, (date, datetime)):
            return field.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(field, (enum.Enum, enum.IntEnum)):
            return field.name
        if isinstance(field, (list, tuple, set)) or isinstance(field, types.GeneratorType):
            return self._process_list(field, depth, excludes=excludes, includes=includes, *args, **kwargs)
        if isinstance(field, dict):
            return self._process_dict(field, depth, excludes=excludes, includes=includes, *args, **kwargs)
        return field


class JsonSerializable:
    serializator = JsonSerializator
    max_serialization_depth = 1

    def serialize(self, max_depth=None, excludes=None, includes=None, *args, **kwargs):
        serializator = self.serializator(max_serialization_depth=max_depth or self.max_serialization_depth)
        return serializator.process_field(self, depth=0, excludes=excludes, includes=includes, *args, **kwargs)
