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


class Currency(object):
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
        'currency_code': 'str',
        'exchange_rate': 'float',
        'localized': 'float',
        'localized_formatted': 'str',
        'value': 'float'
    }

    attribute_map = {
        'currency_code': 'currency_code',
        'exchange_rate': 'exchange_rate',
        'localized': 'localized',
        'localized_formatted': 'localized_formatted',
        'value': 'value'
    }

    def __init__(self, currency_code=None, exchange_rate=None, localized=None, localized_formatted=None, value=None):  # noqa: E501
        """Currency - a model defined in Swagger"""  # noqa: E501

        self._currency_code = None
        self._exchange_rate = None
        self._localized = None
        self._localized_formatted = None
        self._value = None
        self.discriminator = None

        if currency_code is not None:
            self.currency_code = currency_code
        if exchange_rate is not None:
            self.exchange_rate = exchange_rate
        if localized is not None:
            self.localized = localized
        if localized_formatted is not None:
            self.localized_formatted = localized_formatted
        if value is not None:
            self.value = value

    @property
    def currency_code(self):
        """Gets the currency_code of this Currency.  # noqa: E501

        Currency code of the localized value  # noqa: E501

        :return: The currency_code of this Currency.  # noqa: E501
        :rtype: str
        """
        return self._currency_code

    @currency_code.setter
    def currency_code(self, currency_code):
        """Sets the currency_code of this Currency.

        Currency code of the localized value  # noqa: E501

        :param currency_code: The currency_code of this Currency.  # noqa: E501
        :type: str
        """

        self._currency_code = currency_code

    @property
    def exchange_rate(self):
        """Gets the exchange_rate of this Currency.  # noqa: E501

        Exchange rate used to localize  # noqa: E501

        :return: The exchange_rate of this Currency.  # noqa: E501
        :rtype: float
        """
        return self._exchange_rate

    @exchange_rate.setter
    def exchange_rate(self, exchange_rate):
        """Sets the exchange_rate of this Currency.

        Exchange rate used to localize  # noqa: E501

        :param exchange_rate: The exchange_rate of this Currency.  # noqa: E501
        :type: float
        """

        self._exchange_rate = exchange_rate

    @property
    def localized(self):
        """Gets the localized of this Currency.  # noqa: E501

        Value localized to the customer  # noqa: E501

        :return: The localized of this Currency.  # noqa: E501
        :rtype: float
        """
        return self._localized

    @localized.setter
    def localized(self, localized):
        """Sets the localized of this Currency.

        Value localized to the customer  # noqa: E501

        :param localized: The localized of this Currency.  # noqa: E501
        :type: float
        """

        self._localized = localized

    @property
    def localized_formatted(self):
        """Gets the localized_formatted of this Currency.  # noqa: E501

        Value localized and formatted for the customer  # noqa: E501

        :return: The localized_formatted of this Currency.  # noqa: E501
        :rtype: str
        """
        return self._localized_formatted

    @localized_formatted.setter
    def localized_formatted(self, localized_formatted):
        """Sets the localized_formatted of this Currency.

        Value localized and formatted for the customer  # noqa: E501

        :param localized_formatted: The localized_formatted of this Currency.  # noqa: E501
        :type: str
        """

        self._localized_formatted = localized_formatted

    @property
    def value(self):
        """Gets the value of this Currency.  # noqa: E501

        Value in base currency  # noqa: E501

        :return: The value of this Currency.  # noqa: E501
        :rtype: float
        """
        return self._value

    @value.setter
    def value(self, value):
        """Sets the value of this Currency.

        Value in base currency  # noqa: E501

        :param value: The value of this Currency.  # noqa: E501
        :type: float
        """

        self._value = value

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
        if issubclass(Currency, dict):
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
        if not isinstance(other, Currency):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
