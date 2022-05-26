from __future__ import absolute_import
from abc import ABCMeta, abstractmethod
import enum
import six


class ObjBase(six.with_metaclass(ABCMeta)):
    @abstractmethod
    def get_serialize_map(self):
        """
        Returns Dict[api_field, attr_name]

        :return: dict
        """
    @abstractmethod
    def get_deserialize_map(self):
        """
        Returns Dict[attr_name, api_field or (api_field, callable)]

        Deserializes response into the object based on the Map. For arbitrary logic, a tuple of (api_field, callable)
        can be passed. Callable will be called with api_field_value if present.

        :return: dict
        """

    def serialize(self):
        res = {}
        serialization_map = self.get_serialize_map()
        for api_field, attr_name in serialization_map.items():
            attr_val = getattr(self, attr_name)
            if attr_val is None:
                continue
            if isinstance(attr_val, ObjBase):
                res[api_field] = attr_val.serialize()
            elif isinstance(attr_val, list) and all([isinstance(x, ObjBase) for x in attr_val]):
                res[api_field] = [v.serialize() for v in attr_val]
            elif isinstance(attr_val, enum.Enum):
                res[api_field] = attr_val.value
            else:
                res[api_field] = attr_val
        return res

    @classmethod
    def deserialize(cls, data, obj=None, only=None):
        if not obj:
            obj = cls.__new__(cls)
        if only and (not isinstance(only, list) or any([x for x in only if not isinstance(x, str)])):
            raise Exception('only should be a list of string')
        deserialization_map = obj.get_deserialize_map()
        for attr_name, val in deserialization_map.items():
            if only and attr_name not in only:
                continue
            if isinstance(val, tuple):
                api_field, callable_ = val
                deserialized_val = callable_(data.get(api_field))
                setattr(obj, attr_name, deserialized_val)
            else:
                setattr(obj, attr_name, data.get(val))
        return obj


def nested_field(api_field, cls):
    if not issubclass(cls, ObjBase):
        raise Exception('{} should be a subclass of ObjBase'.format(cls.__name__))
    return api_field, lambda data: cls.deserialize(data) if data is not None else None


def list_field(api_field, cls):
    if not issubclass(cls, ObjBase):
        raise Exception('{} should be a subclass of ObjBase'.format(cls.__name__))

    def deserialize(data):
        if not isinstance(data, list):
            return data
        return [cls.deserialize(d) for d in data]

    return api_field, deserialize


def enum_field(api_field, cls):
    if not issubclass(cls, enum.Enum):
        raise Exception('{} should be a subclass of Enum'.format(cls.__name__))

    def deserialize(data):
        if data not in list(cls.__members__.values()):
            return data
        return cls(data)

    return api_field, deserialize
