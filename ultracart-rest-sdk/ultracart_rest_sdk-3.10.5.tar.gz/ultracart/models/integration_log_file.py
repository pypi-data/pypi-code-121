# coding: utf-8

"""
    UltraCart Rest API V2

    UltraCart REST API Version 2  # noqa: E501

    OpenAPI spec version: 2.0.0
    Contact: support@ultracart.com
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six


class IntegrationLogFile(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'mime_type': 'str',
        'name': 'str',
        'size': 'int',
        'uuid': 'str'
    }

    attribute_map = {
        'mime_type': 'mime_type',
        'name': 'name',
        'size': 'size',
        'uuid': 'uuid'
    }

    def __init__(self, mime_type=None, name=None, size=None, uuid=None):  # noqa: E501
        """IntegrationLogFile - a model defined in Swagger"""  # noqa: E501

        self._mime_type = None
        self._name = None
        self._size = None
        self._uuid = None
        self.discriminator = None

        if mime_type is not None:
            self.mime_type = mime_type
        if name is not None:
            self.name = name
        if size is not None:
            self.size = size
        if uuid is not None:
            self.uuid = uuid

    @property
    def mime_type(self):
        """Gets the mime_type of this IntegrationLogFile.  # noqa: E501


        :return: The mime_type of this IntegrationLogFile.  # noqa: E501
        :rtype: str
        """
        return self._mime_type

    @mime_type.setter
    def mime_type(self, mime_type):
        """Sets the mime_type of this IntegrationLogFile.


        :param mime_type: The mime_type of this IntegrationLogFile.  # noqa: E501
        :type: str
        """

        self._mime_type = mime_type

    @property
    def name(self):
        """Gets the name of this IntegrationLogFile.  # noqa: E501


        :return: The name of this IntegrationLogFile.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this IntegrationLogFile.


        :param name: The name of this IntegrationLogFile.  # noqa: E501
        :type: str
        """

        self._name = name

    @property
    def size(self):
        """Gets the size of this IntegrationLogFile.  # noqa: E501


        :return: The size of this IntegrationLogFile.  # noqa: E501
        :rtype: int
        """
        return self._size

    @size.setter
    def size(self, size):
        """Sets the size of this IntegrationLogFile.


        :param size: The size of this IntegrationLogFile.  # noqa: E501
        :type: int
        """

        self._size = size

    @property
    def uuid(self):
        """Gets the uuid of this IntegrationLogFile.  # noqa: E501


        :return: The uuid of this IntegrationLogFile.  # noqa: E501
        :rtype: str
        """
        return self._uuid

    @uuid.setter
    def uuid(self, uuid):
        """Sets the uuid of this IntegrationLogFile.


        :param uuid: The uuid of this IntegrationLogFile.  # noqa: E501
        :type: str
        """

        self._uuid = uuid

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(IntegrationLogFile, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, IntegrationLogFile):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
