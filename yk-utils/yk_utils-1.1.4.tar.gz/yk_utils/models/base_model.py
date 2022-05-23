""" Base model automatically generated from swagger.
"""
import json
import pprint
import typing
from datetime import datetime
import six
from yk_utils.models.deserialization import deserialize_dbmodel, deserialize_model
from yk_utils.objects.object_operations import datetime2str, convert_to_string

GenericType = typing.TypeVar('T')


class Model:
    """
    Base model for swagger generated objects.
    """
    # swaggerTypes: The key is attribute name and the
    # value is attribute type.
    swagger_types = {}

    # swaggerTypesDB: The key is attribute name and the
    # value is attribute type.
    swagger_types_db = None

    # swaggerTypes: The key is attribute name and the
    # value is attribute type.
    fields_to_not_save = []

    # attributeMap: The key is attribute name and the
    # value is json key in definition.
    attribute_map = {}

    @classmethod
    def from_dict(cls: typing.Type[GenericType], dikt) -> GenericType:
        """Returns the dict as a model"""
        return deserialize_model(dikt, cls)

    @classmethod
    def from_db(cls, mongo_object) -> GenericType:
        """Returns the mongodb object as a model"""
        return deserialize_dbmodel(json.loads(
            json.dumps(mongo_object, default=convert_to_string)), cls)

    def to_db(self):
        """Returns the model properties as a dict

        :rtype: dict
        """
        result = {}
        if self.swagger_types_db is None:
            self.swagger_types_db = self.swagger_types

        for attr, _ in six.iteritems(self.swagger_types_db):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_db() if hasattr(x, "to_db") else x,
                    value
                ))
            elif hasattr(value, "to_db"):
                result[attr] = value.to_db()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_db())
                    if hasattr(item[1], "to_db") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_dict(self):
        """Returns the model properties as a dict

        :rtype: dict
        """
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            attr_name = self.attribute_map[attr] if self.attribute_map else attr
            if isinstance(value, list):
                result[attr_name] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_enumdict"):
                result[attr_name] = value.to_enumdict()
            elif hasattr(value, "to_dict"):
                result[attr_name] = value.to_dict()
            elif isinstance(value, datetime):
                result[attr_name] = datetime2str(value)
            elif isinstance(value, dict):
                result[attr_name] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            elif value is not None:
                result[attr_name] = value

        return result

    def to_str(self):
        """Returns the string representation of the model

        :rtype: str
        """
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
