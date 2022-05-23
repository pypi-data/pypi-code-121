from enum import Enum
from typing import Dict


class KeyValue:
    """KeyValue object defines a key-value pair

    :param key: key of the pair
    :type key: str
    :param value: value of the pair
    :type value: str
    """

    def __init__(self, key: str, value: str, **kwargs):
        self.key: str = key
        self.value: str = value

    def to_dict(self):
        return {'key': self.key, 'value': self.value}

    def __eq__(self, other):
        if not isinstance(other, KeyValue):
            return False
        return self.key == other.key and self.value == other.value


class NameValue:
    """KeyValue object defines a name-value pair

    :param name: name of the pair
    :type name: str
    :param value: value of the pair
    :type value: str
    """

    def __init__(self, name: str, value: str, **kwargs):
        self.name: str = name
        self.value: str = value

    def __eq__(self, other):
        if not isinstance(other, NameValue):
            return False
        return self.name == other.name and self.value == other.value


class Name:
    """KeyValue object defines a name

    :param name: name
    :type name: str
    """

    def __init__(self, name: str, **kwargs):
        self.name: str = name

    def __eq__(self, other):
        if not isinstance(other, Name):
            return False
        return self.name == other.name


class QueryResponse:
    """The QueryResponse object defines the response from the server to a query request

    :param resources: List of the resources returned from the server
    :type resources: list
    :param count: Total number of the queried resources
    :type count: int
    :param `**kwargs`: The keyword arguments are there in case there are additional attributes returned from server
    """

    def __init__(self, resources: list, count: int, **kwargs):
        self.resources: list = resources
        self.count: int = count


class BasicResponse:
    """The BasicResponse object defines the response from the server

    :param id: ID of the relevant resource
    :type id: str
    :param message: Response message from the server
    :type message: str
    :param `**kwargs`: The keyword arguments are there in case there are additional attributes returned from server
    """

    def __init__(self, id: str, message: str, **kwargs):
        self.id: str = id
        self.message: str = message

    @staticmethod
    def from_dict(br_dict: Dict[str, str]):
        """Returns a :class:`ai_api_client_sdk.models.base_models.BasicResponse` object, created from the values in the
        dict provided as parameter

        :param br_dict: Dict which includes the necessary values to create the object
        :type br_dict: Dict[str, str]
        :return: An object, created from the values provided
        :rtype: class:`ai_api_client_sdk.models.base_models.BasicResponse`
        """
        return BasicResponse(**br_dict)


class Order(Enum):
    ASC = 'asc'
    DESC = 'desc'


class Operation(Enum):
    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'
