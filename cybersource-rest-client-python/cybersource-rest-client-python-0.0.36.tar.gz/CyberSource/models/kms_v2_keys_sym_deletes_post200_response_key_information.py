# coding: utf-8

"""
    CyberSource Merged Spec

    All CyberSource API specs merged together. These are available at https://developer.cybersource.com/api/reference/api-reference.html

    OpenAPI spec version: 0.0.1
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from pprint import pformat
from six import iteritems
import re


class KmsV2KeysSymDeletesPost200ResponseKeyInformation(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
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
        'organization_id': 'str',
        'key_id': 'str',
        'status': 'str',
        'message': 'str',
        'error_information': 'KmsV2KeysSymPost201ResponseErrorInformation'
    }

    attribute_map = {
        'organization_id': 'organizationId',
        'key_id': 'keyId',
        'status': 'status',
        'message': 'message',
        'error_information': 'errorInformation'
    }

    def __init__(self, organization_id=None, key_id=None, status=None, message=None, error_information=None):
        """
        KmsV2KeysSymDeletesPost200ResponseKeyInformation - a model defined in Swagger
        """

        self._organization_id = None
        self._key_id = None
        self._status = None
        self._message = None
        self._error_information = None

        if organization_id is not None:
          self.organization_id = organization_id
        if key_id is not None:
          self.key_id = key_id
        if status is not None:
          self.status = status
        if message is not None:
          self.message = message
        if error_information is not None:
          self.error_information = error_information

    @property
    def organization_id(self):
        """
        Gets the organization_id of this KmsV2KeysSymDeletesPost200ResponseKeyInformation.
        Merchant Id 

        :return: The organization_id of this KmsV2KeysSymDeletesPost200ResponseKeyInformation.
        :rtype: str
        """
        return self._organization_id

    @organization_id.setter
    def organization_id(self, organization_id):
        """
        Sets the organization_id of this KmsV2KeysSymDeletesPost200ResponseKeyInformation.
        Merchant Id 

        :param organization_id: The organization_id of this KmsV2KeysSymDeletesPost200ResponseKeyInformation.
        :type: str
        """

        self._organization_id = organization_id

    @property
    def key_id(self):
        """
        Gets the key_id of this KmsV2KeysSymDeletesPost200ResponseKeyInformation.
        Key serial number 

        :return: The key_id of this KmsV2KeysSymDeletesPost200ResponseKeyInformation.
        :rtype: str
        """
        return self._key_id

    @key_id.setter
    def key_id(self, key_id):
        """
        Sets the key_id of this KmsV2KeysSymDeletesPost200ResponseKeyInformation.
        Key serial number 

        :param key_id: The key_id of this KmsV2KeysSymDeletesPost200ResponseKeyInformation.
        :type: str
        """

        self._key_id = key_id

    @property
    def status(self):
        """
        Gets the status of this KmsV2KeysSymDeletesPost200ResponseKeyInformation.
        The status of the key.  Possible values:  - FAILED  - ACTIVE  - INACTIVE  - EXPIRED 

        :return: The status of this KmsV2KeysSymDeletesPost200ResponseKeyInformation.
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """
        Sets the status of this KmsV2KeysSymDeletesPost200ResponseKeyInformation.
        The status of the key.  Possible values:  - FAILED  - ACTIVE  - INACTIVE  - EXPIRED 

        :param status: The status of this KmsV2KeysSymDeletesPost200ResponseKeyInformation.
        :type: str
        """

        self._status = status

    @property
    def message(self):
        """
        Gets the message of this KmsV2KeysSymDeletesPost200ResponseKeyInformation.
        message in case of failed key 

        :return: The message of this KmsV2KeysSymDeletesPost200ResponseKeyInformation.
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message):
        """
        Sets the message of this KmsV2KeysSymDeletesPost200ResponseKeyInformation.
        message in case of failed key 

        :param message: The message of this KmsV2KeysSymDeletesPost200ResponseKeyInformation.
        :type: str
        """

        self._message = message

    @property
    def error_information(self):
        """
        Gets the error_information of this KmsV2KeysSymDeletesPost200ResponseKeyInformation.

        :return: The error_information of this KmsV2KeysSymDeletesPost200ResponseKeyInformation.
        :rtype: KmsV2KeysSymPost201ResponseErrorInformation
        """
        return self._error_information

    @error_information.setter
    def error_information(self, error_information):
        """
        Sets the error_information of this KmsV2KeysSymDeletesPost200ResponseKeyInformation.

        :param error_information: The error_information of this KmsV2KeysSymDeletesPost200ResponseKeyInformation.
        :type: KmsV2KeysSymPost201ResponseErrorInformation
        """

        self._error_information = error_information

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in iteritems(self.swagger_types):
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

        return result

    def to_str(self):
        """
        Returns the string representation of the model
        """
        return pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        if not isinstance(other, KmsV2KeysSymDeletesPost200ResponseKeyInformation):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
