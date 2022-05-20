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


class TransactionGatewaysResponse(object):
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
        'error': 'Error',
        'gateways': 'list[TransactionGateway]',
        'metadata': 'ResponseMetadata',
        'success': 'bool',
        'warning': 'Warning'
    }

    attribute_map = {
        'error': 'error',
        'gateways': 'gateways',
        'metadata': 'metadata',
        'success': 'success',
        'warning': 'warning'
    }

    def __init__(self, error=None, gateways=None, metadata=None, success=None, warning=None):  # noqa: E501
        """TransactionGatewaysResponse - a model defined in Swagger"""  # noqa: E501

        self._error = None
        self._gateways = None
        self._metadata = None
        self._success = None
        self._warning = None
        self.discriminator = None

        if error is not None:
            self.error = error
        if gateways is not None:
            self.gateways = gateways
        if metadata is not None:
            self.metadata = metadata
        if success is not None:
            self.success = success
        if warning is not None:
            self.warning = warning

    @property
    def error(self):
        """Gets the error of this TransactionGatewaysResponse.  # noqa: E501


        :return: The error of this TransactionGatewaysResponse.  # noqa: E501
        :rtype: Error
        """
        return self._error

    @error.setter
    def error(self, error):
        """Sets the error of this TransactionGatewaysResponse.


        :param error: The error of this TransactionGatewaysResponse.  # noqa: E501
        :type: Error
        """

        self._error = error

    @property
    def gateways(self):
        """Gets the gateways of this TransactionGatewaysResponse.  # noqa: E501


        :return: The gateways of this TransactionGatewaysResponse.  # noqa: E501
        :rtype: list[TransactionGateway]
        """
        return self._gateways

    @gateways.setter
    def gateways(self, gateways):
        """Sets the gateways of this TransactionGatewaysResponse.


        :param gateways: The gateways of this TransactionGatewaysResponse.  # noqa: E501
        :type: list[TransactionGateway]
        """

        self._gateways = gateways

    @property
    def metadata(self):
        """Gets the metadata of this TransactionGatewaysResponse.  # noqa: E501


        :return: The metadata of this TransactionGatewaysResponse.  # noqa: E501
        :rtype: ResponseMetadata
        """
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        """Sets the metadata of this TransactionGatewaysResponse.


        :param metadata: The metadata of this TransactionGatewaysResponse.  # noqa: E501
        :type: ResponseMetadata
        """

        self._metadata = metadata

    @property
    def success(self):
        """Gets the success of this TransactionGatewaysResponse.  # noqa: E501

        Indicates if API call was successful  # noqa: E501

        :return: The success of this TransactionGatewaysResponse.  # noqa: E501
        :rtype: bool
        """
        return self._success

    @success.setter
    def success(self, success):
        """Sets the success of this TransactionGatewaysResponse.

        Indicates if API call was successful  # noqa: E501

        :param success: The success of this TransactionGatewaysResponse.  # noqa: E501
        :type: bool
        """

        self._success = success

    @property
    def warning(self):
        """Gets the warning of this TransactionGatewaysResponse.  # noqa: E501


        :return: The warning of this TransactionGatewaysResponse.  # noqa: E501
        :rtype: Warning
        """
        return self._warning

    @warning.setter
    def warning(self, warning):
        """Sets the warning of this TransactionGatewaysResponse.


        :param warning: The warning of this TransactionGatewaysResponse.  # noqa: E501
        :type: Warning
        """

        self._warning = warning

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
        if issubclass(TransactionGatewaysResponse, dict):
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
        if not isinstance(other, TransactionGatewaysResponse):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
