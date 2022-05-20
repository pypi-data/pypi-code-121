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


class KmsV2KeysAsymPost201ResponseCertificateInformation(object):
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
        'alias': 'str',
        'key_id': 'str',
        'key': 'str',
        'expiration_date': 'str'
    }

    attribute_map = {
        'alias': 'alias',
        'key_id': 'keyId',
        'key': 'key',
        'expiration_date': 'expirationDate'
    }

    def __init__(self, alias=None, key_id=None, key=None, expiration_date=None):
        """
        KmsV2KeysAsymPost201ResponseCertificateInformation - a model defined in Swagger
        """

        self._alias = None
        self._key_id = None
        self._key = None
        self._expiration_date = None

        if alias is not None:
          self.alias = alias
        if key_id is not None:
          self.key_id = key_id
        if key is not None:
          self.key = key
        if expiration_date is not None:
          self.expiration_date = expiration_date

    @property
    def alias(self):
        """
        Gets the alias of this KmsV2KeysAsymPost201ResponseCertificateInformation.
        Key alias

        :return: The alias of this KmsV2KeysAsymPost201ResponseCertificateInformation.
        :rtype: str
        """
        return self._alias

    @alias.setter
    def alias(self, alias):
        """
        Sets the alias of this KmsV2KeysAsymPost201ResponseCertificateInformation.
        Key alias

        :param alias: The alias of this KmsV2KeysAsymPost201ResponseCertificateInformation.
        :type: str
        """

        self._alias = alias

    @property
    def key_id(self):
        """
        Gets the key_id of this KmsV2KeysAsymPost201ResponseCertificateInformation.
        Key Serial Number 

        :return: The key_id of this KmsV2KeysAsymPost201ResponseCertificateInformation.
        :rtype: str
        """
        return self._key_id

    @key_id.setter
    def key_id(self, key_id):
        """
        Sets the key_id of this KmsV2KeysAsymPost201ResponseCertificateInformation.
        Key Serial Number 

        :param key_id: The key_id of this KmsV2KeysAsymPost201ResponseCertificateInformation.
        :type: str
        """

        self._key_id = key_id

    @property
    def key(self):
        """
        Gets the key of this KmsV2KeysAsymPost201ResponseCertificateInformation.
        value of the key 

        :return: The key of this KmsV2KeysAsymPost201ResponseCertificateInformation.
        :rtype: str
        """
        return self._key

    @key.setter
    def key(self, key):
        """
        Sets the key of this KmsV2KeysAsymPost201ResponseCertificateInformation.
        value of the key 

        :param key: The key of this KmsV2KeysAsymPost201ResponseCertificateInformation.
        :type: str
        """

        self._key = key

    @property
    def expiration_date(self):
        """
        Gets the expiration_date of this KmsV2KeysAsymPost201ResponseCertificateInformation.
        The expiration time in UTC. `Format: YYYY-MM-DDThh:mm:ssZ`  Example 2016-08-11T22:47:57Z equals August 11, 2016, at 22:47:57 (10:47:57 p.m.). The T separates the date and the time. The Z indicates UTC. 

        :return: The expiration_date of this KmsV2KeysAsymPost201ResponseCertificateInformation.
        :rtype: str
        """
        return self._expiration_date

    @expiration_date.setter
    def expiration_date(self, expiration_date):
        """
        Sets the expiration_date of this KmsV2KeysAsymPost201ResponseCertificateInformation.
        The expiration time in UTC. `Format: YYYY-MM-DDThh:mm:ssZ`  Example 2016-08-11T22:47:57Z equals August 11, 2016, at 22:47:57 (10:47:57 p.m.). The T separates the date and the time. The Z indicates UTC. 

        :param expiration_date: The expiration_date of this KmsV2KeysAsymPost201ResponseCertificateInformation.
        :type: str
        """

        self._expiration_date = expiration_date

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
        if not isinstance(other, KmsV2KeysAsymPost201ResponseCertificateInformation):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
