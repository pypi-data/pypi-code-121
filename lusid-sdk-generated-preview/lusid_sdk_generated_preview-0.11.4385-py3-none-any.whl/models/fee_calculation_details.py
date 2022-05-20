# coding: utf-8

"""
    LUSID API

    FINBOURNE Technology  # noqa: E501

    The version of the OpenAPI document: 0.11.4385
    Contact: info@finbourne.com
    Generated by: https://openapi-generator.tech
"""


try:
    from inspect import getfullargspec
except ImportError:
    from inspect import getargspec as getfullargspec
import pprint
import re  # noqa: F401
import six

from lusid.configuration import Configuration


class FeeCalculationDetails(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
      required_map (dict): The key is attribute name
                           and the value is whether it is 'required' or 'optional'.
    """
    openapi_types = {
        'rule_type': 'str',
        'rule_information': 'str',
        'additional_information': 'dict(str, str)',
        'property_key': 'str',
        'fee': 'CalculationInfo',
        'max_fee': 'CalculationInfo',
        'min_fee': 'CalculationInfo'
    }

    attribute_map = {
        'rule_type': 'ruleType',
        'rule_information': 'ruleInformation',
        'additional_information': 'additionalInformation',
        'property_key': 'propertyKey',
        'fee': 'fee',
        'max_fee': 'maxFee',
        'min_fee': 'minFee'
    }

    required_map = {
        'rule_type': 'required',
        'rule_information': 'required',
        'additional_information': 'required',
        'property_key': 'required',
        'fee': 'required',
        'max_fee': 'optional',
        'min_fee': 'optional'
    }

    def __init__(self, rule_type=None, rule_information=None, additional_information=None, property_key=None, fee=None, max_fee=None, min_fee=None, local_vars_configuration=None):  # noqa: E501
        """FeeCalculationDetails - a model defined in OpenAPI"
        
        :param rule_type:  Rule Type (required)
        :type rule_type: str
        :param rule_information:  Rule Sub Type (required)
        :type rule_information: str
        :param additional_information:  Other property keys populated for the fee (required)
        :type additional_information: dict(str, str)
        :param property_key:  The property key which uniquely identifies the property. The format for the property key is {domain}/{scope}/{code}, e.g. 'Portfolio/Manager/Id'. (required)
        :type property_key: str
        :param fee:  (required)
        :type fee: lusid.CalculationInfo
        :param max_fee: 
        :type max_fee: lusid.CalculationInfo
        :param min_fee: 
        :type min_fee: lusid.CalculationInfo

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._rule_type = None
        self._rule_information = None
        self._additional_information = None
        self._property_key = None
        self._fee = None
        self._max_fee = None
        self._min_fee = None
        self.discriminator = None

        self.rule_type = rule_type
        self.rule_information = rule_information
        self.additional_information = additional_information
        self.property_key = property_key
        self.fee = fee
        if max_fee is not None:
            self.max_fee = max_fee
        if min_fee is not None:
            self.min_fee = min_fee

    @property
    def rule_type(self):
        """Gets the rule_type of this FeeCalculationDetails.  # noqa: E501

        Rule Type  # noqa: E501

        :return: The rule_type of this FeeCalculationDetails.  # noqa: E501
        :rtype: str
        """
        return self._rule_type

    @rule_type.setter
    def rule_type(self, rule_type):
        """Sets the rule_type of this FeeCalculationDetails.

        Rule Type  # noqa: E501

        :param rule_type: The rule_type of this FeeCalculationDetails.  # noqa: E501
        :type rule_type: str
        """
        if self.local_vars_configuration.client_side_validation and rule_type is None:  # noqa: E501
            raise ValueError("Invalid value for `rule_type`, must not be `None`")  # noqa: E501

        self._rule_type = rule_type

    @property
    def rule_information(self):
        """Gets the rule_information of this FeeCalculationDetails.  # noqa: E501

        Rule Sub Type  # noqa: E501

        :return: The rule_information of this FeeCalculationDetails.  # noqa: E501
        :rtype: str
        """
        return self._rule_information

    @rule_information.setter
    def rule_information(self, rule_information):
        """Sets the rule_information of this FeeCalculationDetails.

        Rule Sub Type  # noqa: E501

        :param rule_information: The rule_information of this FeeCalculationDetails.  # noqa: E501
        :type rule_information: str
        """
        if self.local_vars_configuration.client_side_validation and rule_information is None:  # noqa: E501
            raise ValueError("Invalid value for `rule_information`, must not be `None`")  # noqa: E501

        self._rule_information = rule_information

    @property
    def additional_information(self):
        """Gets the additional_information of this FeeCalculationDetails.  # noqa: E501

        Other property keys populated for the fee  # noqa: E501

        :return: The additional_information of this FeeCalculationDetails.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._additional_information

    @additional_information.setter
    def additional_information(self, additional_information):
        """Sets the additional_information of this FeeCalculationDetails.

        Other property keys populated for the fee  # noqa: E501

        :param additional_information: The additional_information of this FeeCalculationDetails.  # noqa: E501
        :type additional_information: dict(str, str)
        """
        if self.local_vars_configuration.client_side_validation and additional_information is None:  # noqa: E501
            raise ValueError("Invalid value for `additional_information`, must not be `None`")  # noqa: E501

        self._additional_information = additional_information

    @property
    def property_key(self):
        """Gets the property_key of this FeeCalculationDetails.  # noqa: E501

        The property key which uniquely identifies the property. The format for the property key is {domain}/{scope}/{code}, e.g. 'Portfolio/Manager/Id'.  # noqa: E501

        :return: The property_key of this FeeCalculationDetails.  # noqa: E501
        :rtype: str
        """
        return self._property_key

    @property_key.setter
    def property_key(self, property_key):
        """Sets the property_key of this FeeCalculationDetails.

        The property key which uniquely identifies the property. The format for the property key is {domain}/{scope}/{code}, e.g. 'Portfolio/Manager/Id'.  # noqa: E501

        :param property_key: The property_key of this FeeCalculationDetails.  # noqa: E501
        :type property_key: str
        """
        if self.local_vars_configuration.client_side_validation and property_key is None:  # noqa: E501
            raise ValueError("Invalid value for `property_key`, must not be `None`")  # noqa: E501

        self._property_key = property_key

    @property
    def fee(self):
        """Gets the fee of this FeeCalculationDetails.  # noqa: E501


        :return: The fee of this FeeCalculationDetails.  # noqa: E501
        :rtype: lusid.CalculationInfo
        """
        return self._fee

    @fee.setter
    def fee(self, fee):
        """Sets the fee of this FeeCalculationDetails.


        :param fee: The fee of this FeeCalculationDetails.  # noqa: E501
        :type fee: lusid.CalculationInfo
        """
        if self.local_vars_configuration.client_side_validation and fee is None:  # noqa: E501
            raise ValueError("Invalid value for `fee`, must not be `None`")  # noqa: E501

        self._fee = fee

    @property
    def max_fee(self):
        """Gets the max_fee of this FeeCalculationDetails.  # noqa: E501


        :return: The max_fee of this FeeCalculationDetails.  # noqa: E501
        :rtype: lusid.CalculationInfo
        """
        return self._max_fee

    @max_fee.setter
    def max_fee(self, max_fee):
        """Sets the max_fee of this FeeCalculationDetails.


        :param max_fee: The max_fee of this FeeCalculationDetails.  # noqa: E501
        :type max_fee: lusid.CalculationInfo
        """

        self._max_fee = max_fee

    @property
    def min_fee(self):
        """Gets the min_fee of this FeeCalculationDetails.  # noqa: E501


        :return: The min_fee of this FeeCalculationDetails.  # noqa: E501
        :rtype: lusid.CalculationInfo
        """
        return self._min_fee

    @min_fee.setter
    def min_fee(self, min_fee):
        """Sets the min_fee of this FeeCalculationDetails.


        :param min_fee: The min_fee of this FeeCalculationDetails.  # noqa: E501
        :type min_fee: lusid.CalculationInfo
        """

        self._min_fee = min_fee

    def to_dict(self, serialize=False):
        """Returns the model properties as a dict"""
        result = {}

        def convert(x):
            if hasattr(x, "to_dict"):
                args = getfullargspec(x.to_dict).args
                if len(args) == 1:
                    return x.to_dict()
                else:
                    return x.to_dict(serialize)
            else:
                return x

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            attr = self.attribute_map.get(attr, attr) if serialize else attr
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: convert(x),
                    value
                ))
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], convert(item[1])),
                    value.items()
                ))
            else:
                result[attr] = convert(value)

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, FeeCalculationDetails):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, FeeCalculationDetails):
            return True

        return self.to_dict() != other.to_dict()
