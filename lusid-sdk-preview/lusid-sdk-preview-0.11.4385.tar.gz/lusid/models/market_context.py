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


class MarketContext(object):
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
        'market_rules': 'list[MarketDataKeyRule]',
        'suppliers': 'MarketContextSuppliers',
        'options': 'MarketOptions',
        'specific_rules': 'list[MarketDataSpecificRule]'
    }

    attribute_map = {
        'market_rules': 'marketRules',
        'suppliers': 'suppliers',
        'options': 'options',
        'specific_rules': 'specificRules'
    }

    required_map = {
        'market_rules': 'optional',
        'suppliers': 'optional',
        'options': 'optional',
        'specific_rules': 'optional'
    }

    def __init__(self, market_rules=None, suppliers=None, options=None, specific_rules=None, local_vars_configuration=None):  # noqa: E501
        """MarketContext - a model defined in OpenAPI"
        
        :param market_rules:  The set of rules that define how to resolve particular use cases. These can be relatively general or specific in nature.  Nominally any number are possible and will be processed in order where applicable. However, there is evidently a potential  for increased computational cost where many rules must be applied to resolve data. Ensuring that portfolios are structured in  such a way as to reduce the number of rules required is therefore sensible.
        :type market_rules: list[lusid.MarketDataKeyRule]
        :param suppliers: 
        :type suppliers: lusid.MarketContextSuppliers
        :param options: 
        :type options: lusid.MarketOptions
        :param specific_rules:  Extends market data key rules to be able to catch dependencies depending on where the dependency comes from, as opposed to what the dependency is asking for.  Using two specific rules, one could instruct rates curves requested by bonds to be retrieved from a different scope than rates curves requested by swaps.  WARNING: The use of specific rules impacts performance. Where possible, one should use MarketDataKeyRules only.
        :type specific_rules: list[lusid.MarketDataSpecificRule]

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._market_rules = None
        self._suppliers = None
        self._options = None
        self._specific_rules = None
        self.discriminator = None

        self.market_rules = market_rules
        self.suppliers = suppliers
        if options is not None:
            self.options = options
        self.specific_rules = specific_rules

    @property
    def market_rules(self):
        """Gets the market_rules of this MarketContext.  # noqa: E501

        The set of rules that define how to resolve particular use cases. These can be relatively general or specific in nature.  Nominally any number are possible and will be processed in order where applicable. However, there is evidently a potential  for increased computational cost where many rules must be applied to resolve data. Ensuring that portfolios are structured in  such a way as to reduce the number of rules required is therefore sensible.  # noqa: E501

        :return: The market_rules of this MarketContext.  # noqa: E501
        :rtype: list[lusid.MarketDataKeyRule]
        """
        return self._market_rules

    @market_rules.setter
    def market_rules(self, market_rules):
        """Sets the market_rules of this MarketContext.

        The set of rules that define how to resolve particular use cases. These can be relatively general or specific in nature.  Nominally any number are possible and will be processed in order where applicable. However, there is evidently a potential  for increased computational cost where many rules must be applied to resolve data. Ensuring that portfolios are structured in  such a way as to reduce the number of rules required is therefore sensible.  # noqa: E501

        :param market_rules: The market_rules of this MarketContext.  # noqa: E501
        :type market_rules: list[lusid.MarketDataKeyRule]
        """

        self._market_rules = market_rules

    @property
    def suppliers(self):
        """Gets the suppliers of this MarketContext.  # noqa: E501


        :return: The suppliers of this MarketContext.  # noqa: E501
        :rtype: lusid.MarketContextSuppliers
        """
        return self._suppliers

    @suppliers.setter
    def suppliers(self, suppliers):
        """Sets the suppliers of this MarketContext.


        :param suppliers: The suppliers of this MarketContext.  # noqa: E501
        :type suppliers: lusid.MarketContextSuppliers
        """

        self._suppliers = suppliers

    @property
    def options(self):
        """Gets the options of this MarketContext.  # noqa: E501


        :return: The options of this MarketContext.  # noqa: E501
        :rtype: lusid.MarketOptions
        """
        return self._options

    @options.setter
    def options(self, options):
        """Sets the options of this MarketContext.


        :param options: The options of this MarketContext.  # noqa: E501
        :type options: lusid.MarketOptions
        """

        self._options = options

    @property
    def specific_rules(self):
        """Gets the specific_rules of this MarketContext.  # noqa: E501

        Extends market data key rules to be able to catch dependencies depending on where the dependency comes from, as opposed to what the dependency is asking for.  Using two specific rules, one could instruct rates curves requested by bonds to be retrieved from a different scope than rates curves requested by swaps.  WARNING: The use of specific rules impacts performance. Where possible, one should use MarketDataKeyRules only.  # noqa: E501

        :return: The specific_rules of this MarketContext.  # noqa: E501
        :rtype: list[lusid.MarketDataSpecificRule]
        """
        return self._specific_rules

    @specific_rules.setter
    def specific_rules(self, specific_rules):
        """Sets the specific_rules of this MarketContext.

        Extends market data key rules to be able to catch dependencies depending on where the dependency comes from, as opposed to what the dependency is asking for.  Using two specific rules, one could instruct rates curves requested by bonds to be retrieved from a different scope than rates curves requested by swaps.  WARNING: The use of specific rules impacts performance. Where possible, one should use MarketDataKeyRules only.  # noqa: E501

        :param specific_rules: The specific_rules of this MarketContext.  # noqa: E501
        :type specific_rules: list[lusid.MarketDataSpecificRule]
        """

        self._specific_rules = specific_rules

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
        if not isinstance(other, MarketContext):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, MarketContext):
            return True

        return self.to_dict() != other.to_dict()
