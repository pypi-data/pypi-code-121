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


class EmailFlowFolder(object):
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
        'esp_flow_folder_uuid': 'str',
        'merchant_id': 'str',
        'name': 'str',
        'storefront_oid': 'int',
        'system_generated': 'bool'
    }

    attribute_map = {
        'esp_flow_folder_uuid': 'esp_flow_folder_uuid',
        'merchant_id': 'merchant_id',
        'name': 'name',
        'storefront_oid': 'storefront_oid',
        'system_generated': 'system_generated'
    }

    def __init__(self, esp_flow_folder_uuid=None, merchant_id=None, name=None, storefront_oid=None, system_generated=None):  # noqa: E501
        """EmailFlowFolder - a model defined in Swagger"""  # noqa: E501

        self._esp_flow_folder_uuid = None
        self._merchant_id = None
        self._name = None
        self._storefront_oid = None
        self._system_generated = None
        self.discriminator = None

        if esp_flow_folder_uuid is not None:
            self.esp_flow_folder_uuid = esp_flow_folder_uuid
        if merchant_id is not None:
            self.merchant_id = merchant_id
        if name is not None:
            self.name = name
        if storefront_oid is not None:
            self.storefront_oid = storefront_oid
        if system_generated is not None:
            self.system_generated = system_generated

    @property
    def esp_flow_folder_uuid(self):
        """Gets the esp_flow_folder_uuid of this EmailFlowFolder.  # noqa: E501

        Email flow folder UUID  # noqa: E501

        :return: The esp_flow_folder_uuid of this EmailFlowFolder.  # noqa: E501
        :rtype: str
        """
        return self._esp_flow_folder_uuid

    @esp_flow_folder_uuid.setter
    def esp_flow_folder_uuid(self, esp_flow_folder_uuid):
        """Sets the esp_flow_folder_uuid of this EmailFlowFolder.

        Email flow folder UUID  # noqa: E501

        :param esp_flow_folder_uuid: The esp_flow_folder_uuid of this EmailFlowFolder.  # noqa: E501
        :type: str
        """

        self._esp_flow_folder_uuid = esp_flow_folder_uuid

    @property
    def merchant_id(self):
        """Gets the merchant_id of this EmailFlowFolder.  # noqa: E501

        Merchant ID  # noqa: E501

        :return: The merchant_id of this EmailFlowFolder.  # noqa: E501
        :rtype: str
        """
        return self._merchant_id

    @merchant_id.setter
    def merchant_id(self, merchant_id):
        """Sets the merchant_id of this EmailFlowFolder.

        Merchant ID  # noqa: E501

        :param merchant_id: The merchant_id of this EmailFlowFolder.  # noqa: E501
        :type: str
        """

        self._merchant_id = merchant_id

    @property
    def name(self):
        """Gets the name of this EmailFlowFolder.  # noqa: E501

        Name of email flow folder  # noqa: E501

        :return: The name of this EmailFlowFolder.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this EmailFlowFolder.

        Name of email flow folder  # noqa: E501

        :param name: The name of this EmailFlowFolder.  # noqa: E501
        :type: str
        """
        if name is not None and len(name) > 250:
            raise ValueError("Invalid value for `name`, length must be less than or equal to `250`")  # noqa: E501

        self._name = name

    @property
    def storefront_oid(self):
        """Gets the storefront_oid of this EmailFlowFolder.  # noqa: E501

        Storefront oid  # noqa: E501

        :return: The storefront_oid of this EmailFlowFolder.  # noqa: E501
        :rtype: int
        """
        return self._storefront_oid

    @storefront_oid.setter
    def storefront_oid(self, storefront_oid):
        """Sets the storefront_oid of this EmailFlowFolder.

        Storefront oid  # noqa: E501

        :param storefront_oid: The storefront_oid of this EmailFlowFolder.  # noqa: E501
        :type: int
        """

        self._storefront_oid = storefront_oid

    @property
    def system_generated(self):
        """Gets the system_generated of this EmailFlowFolder.  # noqa: E501

        System generated folder  # noqa: E501

        :return: The system_generated of this EmailFlowFolder.  # noqa: E501
        :rtype: bool
        """
        return self._system_generated

    @system_generated.setter
    def system_generated(self, system_generated):
        """Sets the system_generated of this EmailFlowFolder.

        System generated folder  # noqa: E501

        :param system_generated: The system_generated of this EmailFlowFolder.  # noqa: E501
        :type: bool
        """

        self._system_generated = system_generated

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
        if issubclass(EmailFlowFolder, dict):
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
        if not isinstance(other, EmailFlowFolder):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
