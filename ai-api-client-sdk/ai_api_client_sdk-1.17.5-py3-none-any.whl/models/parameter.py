from enum import Enum
from typing import Any, Dict


class Parameter:
    """The Parameter object defines the parameter specified in the executable definition.

    :param name: name of the parameter
    :type name: str
    :param type: Type of the parameter
    :type type: class:`ai_api_client_sdk.models.parameter.Parameter.Type`
    :param `**kwargs`: The keyword arguments are there in case there are additional attributes returned from server
    """
    class Type(Enum):
        STRING = 'string'

    def __init__(self, name: str, type: Type, **kwargs):
        self.name: str = name
        self.type: Parameter.Type = type  # pylint: disable=used-before-assignment

    def __eq__(self, other):
        if not isinstance(other, Parameter):
            return False
        return self.name == other.name and self.type == other.type

    @staticmethod
    def from_dict(parameter_dict: Dict[str, Any]):
        """Returns a :class:`ai_api_client_sdk.models.parameter.Parameter` object, created from the values in the dict
        provided as parameter

        :param parameter_dict: Dict which includes the necessary values to create the object
        :type parameter_dict: Dict[str, Any]
        :return: An object, created from the values provided
        :rtype: class:`ai_api_client_sdk.models.parameter.Parameter`
        """
        parameter_dict['type'] = Parameter.Type(parameter_dict['type'])
        return Parameter(**parameter_dict)
