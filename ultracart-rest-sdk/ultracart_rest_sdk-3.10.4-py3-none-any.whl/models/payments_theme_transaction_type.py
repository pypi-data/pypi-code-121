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


class PaymentsThemeTransactionType(object):
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
        'code': 'str',
        'credit_card_transaction_type': 'str',
        'screen_branding_theme_oid': 'int'
    }

    attribute_map = {
        'code': 'code',
        'credit_card_transaction_type': 'credit_card_transaction_type',
        'screen_branding_theme_oid': 'screen_branding_theme_oid'
    }

    def __init__(self, code=None, credit_card_transaction_type=None, screen_branding_theme_oid=None):  # noqa: E501
        """PaymentsThemeTransactionType - a model defined in Swagger"""  # noqa: E501

        self._code = None
        self._credit_card_transaction_type = None
        self._screen_branding_theme_oid = None
        self.discriminator = None

        if code is not None:
            self.code = code
        if credit_card_transaction_type is not None:
            self.credit_card_transaction_type = credit_card_transaction_type
        if screen_branding_theme_oid is not None:
            self.screen_branding_theme_oid = screen_branding_theme_oid

    @property
    def code(self):
        """Gets the code of this PaymentsThemeTransactionType.  # noqa: E501

        External human readable identifier for a theme  # noqa: E501

        :return: The code of this PaymentsThemeTransactionType.  # noqa: E501
        :rtype: str
        """
        return self._code

    @code.setter
    def code(self, code):
        """Sets the code of this PaymentsThemeTransactionType.

        External human readable identifier for a theme  # noqa: E501

        :param code: The code of this PaymentsThemeTransactionType.  # noqa: E501
        :type: str
        """

        self._code = code

    @property
    def credit_card_transaction_type(self):
        """Gets the credit_card_transaction_type of this PaymentsThemeTransactionType.  # noqa: E501

        The credit card transaction type for this theme  # noqa: E501

        :return: The credit_card_transaction_type of this PaymentsThemeTransactionType.  # noqa: E501
        :rtype: str
        """
        return self._credit_card_transaction_type

    @credit_card_transaction_type.setter
    def credit_card_transaction_type(self, credit_card_transaction_type):
        """Sets the credit_card_transaction_type of this PaymentsThemeTransactionType.

        The credit card transaction type for this theme  # noqa: E501

        :param credit_card_transaction_type: The credit_card_transaction_type of this PaymentsThemeTransactionType.  # noqa: E501
        :type: str
        """
        allowed_values = ["auth and capture", "auth then capture", "auth only"]  # noqa: E501
        if credit_card_transaction_type not in allowed_values:
            raise ValueError(
                "Invalid value for `credit_card_transaction_type` ({0}), must be one of {1}"  # noqa: E501
                .format(credit_card_transaction_type, allowed_values)
            )

        self._credit_card_transaction_type = credit_card_transaction_type

    @property
    def screen_branding_theme_oid(self):
        """Gets the screen_branding_theme_oid of this PaymentsThemeTransactionType.  # noqa: E501

        Internal identifier for a theme  # noqa: E501

        :return: The screen_branding_theme_oid of this PaymentsThemeTransactionType.  # noqa: E501
        :rtype: int
        """
        return self._screen_branding_theme_oid

    @screen_branding_theme_oid.setter
    def screen_branding_theme_oid(self, screen_branding_theme_oid):
        """Sets the screen_branding_theme_oid of this PaymentsThemeTransactionType.

        Internal identifier for a theme  # noqa: E501

        :param screen_branding_theme_oid: The screen_branding_theme_oid of this PaymentsThemeTransactionType.  # noqa: E501
        :type: int
        """

        self._screen_branding_theme_oid = screen_branding_theme_oid

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
        if issubclass(PaymentsThemeTransactionType, dict):
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
        if not isinstance(other, PaymentsThemeTransactionType):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
