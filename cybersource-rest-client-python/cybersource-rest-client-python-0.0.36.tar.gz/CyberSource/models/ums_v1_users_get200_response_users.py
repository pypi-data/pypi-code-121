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


class UmsV1UsersGet200ResponseUsers(object):
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
        'account_information': 'UmsV1UsersGet200ResponseAccountInformation',
        'organization_information': 'UmsV1UsersGet200ResponseOrganizationInformation',
        'contact_information': 'UmsV1UsersGet200ResponseContactInformation'
    }

    attribute_map = {
        'account_information': 'accountInformation',
        'organization_information': 'organizationInformation',
        'contact_information': 'contactInformation'
    }

    def __init__(self, account_information=None, organization_information=None, contact_information=None):
        """
        UmsV1UsersGet200ResponseUsers - a model defined in Swagger
        """

        self._account_information = None
        self._organization_information = None
        self._contact_information = None

        if account_information is not None:
          self.account_information = account_information
        if organization_information is not None:
          self.organization_information = organization_information
        if contact_information is not None:
          self.contact_information = contact_information

    @property
    def account_information(self):
        """
        Gets the account_information of this UmsV1UsersGet200ResponseUsers.

        :return: The account_information of this UmsV1UsersGet200ResponseUsers.
        :rtype: UmsV1UsersGet200ResponseAccountInformation
        """
        return self._account_information

    @account_information.setter
    def account_information(self, account_information):
        """
        Sets the account_information of this UmsV1UsersGet200ResponseUsers.

        :param account_information: The account_information of this UmsV1UsersGet200ResponseUsers.
        :type: UmsV1UsersGet200ResponseAccountInformation
        """

        self._account_information = account_information

    @property
    def organization_information(self):
        """
        Gets the organization_information of this UmsV1UsersGet200ResponseUsers.

        :return: The organization_information of this UmsV1UsersGet200ResponseUsers.
        :rtype: UmsV1UsersGet200ResponseOrganizationInformation
        """
        return self._organization_information

    @organization_information.setter
    def organization_information(self, organization_information):
        """
        Sets the organization_information of this UmsV1UsersGet200ResponseUsers.

        :param organization_information: The organization_information of this UmsV1UsersGet200ResponseUsers.
        :type: UmsV1UsersGet200ResponseOrganizationInformation
        """

        self._organization_information = organization_information

    @property
    def contact_information(self):
        """
        Gets the contact_information of this UmsV1UsersGet200ResponseUsers.

        :return: The contact_information of this UmsV1UsersGet200ResponseUsers.
        :rtype: UmsV1UsersGet200ResponseContactInformation
        """
        return self._contact_information

    @contact_information.setter
    def contact_information(self, contact_information):
        """
        Sets the contact_information of this UmsV1UsersGet200ResponseUsers.

        :param contact_information: The contact_information of this UmsV1UsersGet200ResponseUsers.
        :type: UmsV1UsersGet200ResponseContactInformation
        """

        self._contact_information = contact_information

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
        if not isinstance(other, UmsV1UsersGet200ResponseUsers):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
