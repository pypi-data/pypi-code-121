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


class Ptsv2paymentsPaymentInformationPaymentType(object):
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
        'name': 'str',
        'sub_type_name': 'str',
        'method': 'Ptsv2paymentsPaymentInformationPaymentTypeMethod'
    }

    attribute_map = {
        'name': 'name',
        'sub_type_name': 'subTypeName',
        'method': 'method'
    }

    def __init__(self, name=None, sub_type_name=None, method=None):
        """
        Ptsv2paymentsPaymentInformationPaymentType - a model defined in Swagger
        """

        self._name = None
        self._sub_type_name = None
        self._method = None

        if name is not None:
          self.name = name
        if sub_type_name is not None:
          self.sub_type_name = sub_type_name
        if method is not None:
          self.method = method

    @property
    def name(self):
        """
        Gets the name of this Ptsv2paymentsPaymentInformationPaymentType.
        A Payment Type is an agreed means for a payee to receive legal tender from a payer. The way one pays for a commercial financial transaction. Examples: Card, Bank Transfer, Digital, Direct Debit. Possible values: - `CARD` (use this for a PIN debit transaction) - `CHECK` (use this for all eCheck payment transactions - ECP Debit, ECP Follow-on Credit, ECP StandAlone Credit) 

        :return: The name of this Ptsv2paymentsPaymentInformationPaymentType.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this Ptsv2paymentsPaymentInformationPaymentType.
        A Payment Type is an agreed means for a payee to receive legal tender from a payer. The way one pays for a commercial financial transaction. Examples: Card, Bank Transfer, Digital, Direct Debit. Possible values: - `CARD` (use this for a PIN debit transaction) - `CHECK` (use this for all eCheck payment transactions - ECP Debit, ECP Follow-on Credit, ECP StandAlone Credit) 

        :param name: The name of this Ptsv2paymentsPaymentInformationPaymentType.
        :type: str
        """

        self._name = name

    @property
    def sub_type_name(self):
        """
        Gets the sub_type_name of this Ptsv2paymentsPaymentInformationPaymentType.
        Detailed information about the Payment Type. Possible values: - `DEBIT`: Use this value to indicate a PIN debit transaction.  Examples: For Card, if Credit or Debit or PrePaid. For Bank Transfer, if Online Bank Transfer or Wire Transfers. 

        :return: The sub_type_name of this Ptsv2paymentsPaymentInformationPaymentType.
        :rtype: str
        """
        return self._sub_type_name

    @sub_type_name.setter
    def sub_type_name(self, sub_type_name):
        """
        Sets the sub_type_name of this Ptsv2paymentsPaymentInformationPaymentType.
        Detailed information about the Payment Type. Possible values: - `DEBIT`: Use this value to indicate a PIN debit transaction.  Examples: For Card, if Credit or Debit or PrePaid. For Bank Transfer, if Online Bank Transfer or Wire Transfers. 

        :param sub_type_name: The sub_type_name of this Ptsv2paymentsPaymentInformationPaymentType.
        :type: str
        """

        self._sub_type_name = sub_type_name

    @property
    def method(self):
        """
        Gets the method of this Ptsv2paymentsPaymentInformationPaymentType.

        :return: The method of this Ptsv2paymentsPaymentInformationPaymentType.
        :rtype: Ptsv2paymentsPaymentInformationPaymentTypeMethod
        """
        return self._method

    @method.setter
    def method(self, method):
        """
        Sets the method of this Ptsv2paymentsPaymentInformationPaymentType.

        :param method: The method of this Ptsv2paymentsPaymentInformationPaymentType.
        :type: Ptsv2paymentsPaymentInformationPaymentTypeMethod
        """

        self._method = method

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
        if not isinstance(other, Ptsv2paymentsPaymentInformationPaymentType):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
