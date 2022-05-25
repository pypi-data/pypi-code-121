# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="WordProcessingSaveOptions.py">
#   Copyright (c) 2003-2022 Aspose Pty Ltd
# </copyright>
# <summary>
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
# </summary>
# -----------------------------------------------------------------------------------

import pprint
import re  # noqa: F401

import six

from groupdocs_editor_cloud.models import SaveOptions

class WordProcessingSaveOptions(SaveOptions):
    """
    Allows to specify custom options for generating and saving WordProcessing-compliant documents
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'password': 'str',
        'enable_pagination': 'bool',
        'locale': 'str',
        'locale_bi': 'str',
        'locale_far_east': 'str',
        'protection_type': 'str',
        'protection_password': 'str'
    }

    attribute_map = {
        'password': 'Password',
        'enable_pagination': 'EnablePagination',
        'locale': 'Locale',
        'locale_bi': 'LocaleBi',
        'locale_far_east': 'LocaleFarEast',
        'protection_type': 'ProtectionType',
        'protection_password': 'ProtectionPassword'
    }

    def __init__(self, password=None, enable_pagination=None, locale=None, locale_bi=None, locale_far_east=None, protection_type=None, protection_password=None, **kwargs):  # noqa: E501
        """Initializes new instance of WordProcessingSaveOptions"""  # noqa: E501

        self._password = None
        self._enable_pagination = None
        self._locale = None
        self._locale_bi = None
        self._locale_far_east = None
        self._protection_type = None
        self._protection_password = None

        if password is not None:
            self.password = password
        if enable_pagination is not None:
            self.enable_pagination = enable_pagination
        if locale is not None:
            self.locale = locale
        if locale_bi is not None:
            self.locale_bi = locale_bi
        if locale_far_east is not None:
            self.locale_far_east = locale_far_east
        if protection_type is not None:
            self.protection_type = protection_type
        if protection_password is not None:
            self.protection_password = protection_password

        base = super(WordProcessingSaveOptions, self)
        base.__init__(**kwargs)

        self.swagger_types.update(base.swagger_types)
        self.attribute_map.update(base.attribute_map)
    
    @property
    def password(self):
        """
        Gets the password.  # noqa: E501

        Allows to specify document password  # noqa: E501

        :return: The password.  # noqa: E501
        :rtype: str
        """
        return self._password

    @password.setter
    def password(self, password):
        """
        Sets the password.

        Allows to specify document password  # noqa: E501

        :param password: The password.  # noqa: E501
        :type: str
        """
        self._password = password
    
    @property
    def enable_pagination(self):
        """
        Gets the enable_pagination.  # noqa: E501

        Allows to enable or disable pagination which will be used for saving the document. If the original document was opened and edited in pagination mode, this option also should be enabled. By default is disabled.  # noqa: E501

        :return: The enable_pagination.  # noqa: E501
        :rtype: bool
        """
        return self._enable_pagination

    @enable_pagination.setter
    def enable_pagination(self, enable_pagination):
        """
        Sets the enable_pagination.

        Allows to enable or disable pagination which will be used for saving the document. If the original document was opened and edited in pagination mode, this option also should be enabled. By default is disabled.  # noqa: E501

        :param enable_pagination: The enable_pagination.  # noqa: E501
        :type: bool
        """
        if enable_pagination is None:
            raise ValueError("Invalid value for `enable_pagination`, must not be `None`")  # noqa: E501
        self._enable_pagination = enable_pagination
    
    @property
    def locale(self):
        """
        Gets the locale.  # noqa: E501

        Allows to set override default locale (language) for the WordProcessing document, which will be applied during its creation. When is not specified (default value), MS Word (or other program) will detect (or choose) the document locale according to its own settings or other factors.  # noqa: E501

        :return: The locale.  # noqa: E501
        :rtype: str
        """
        return self._locale

    @locale.setter
    def locale(self, locale):
        """
        Sets the locale.

        Allows to set override default locale (language) for the WordProcessing document, which will be applied during its creation. When is not specified (default value), MS Word (or other program) will detect (or choose) the document locale according to its own settings or other factors.  # noqa: E501

        :param locale: The locale.  # noqa: E501
        :type: str
        """
        self._locale = locale
    
    @property
    def locale_bi(self):
        """
        Gets the locale_bi.  # noqa: E501

        Allows to set override locale (language) for the WordProcessing document for the RTL (right-to-left) text, which will be applied during its creation. When is not specified (default value), MS Word (or other program) will detect (or choose) the document RTL locale according to its own settings or other factors.  # noqa: E501

        :return: The locale_bi.  # noqa: E501
        :rtype: str
        """
        return self._locale_bi

    @locale_bi.setter
    def locale_bi(self, locale_bi):
        """
        Sets the locale_bi.

        Allows to set override locale (language) for the WordProcessing document for the RTL (right-to-left) text, which will be applied during its creation. When is not specified (default value), MS Word (or other program) will detect (or choose) the document RTL locale according to its own settings or other factors.  # noqa: E501

        :param locale_bi: The locale_bi.  # noqa: E501
        :type: str
        """
        self._locale_bi = locale_bi
    
    @property
    def locale_far_east(self):
        """
        Gets the locale_far_east.  # noqa: E501

        Allows to override the locale (language) for the WordProcessing document for the East-Asian text, which will be applied during its creation. When is not specified (default value), MS Word (or other program) will detect (or choose) the document East-Asian locale according to its own settings or other factors.  # noqa: E501

        :return: The locale_far_east.  # noqa: E501
        :rtype: str
        """
        return self._locale_far_east

    @locale_far_east.setter
    def locale_far_east(self, locale_far_east):
        """
        Sets the locale_far_east.

        Allows to override the locale (language) for the WordProcessing document for the East-Asian text, which will be applied during its creation. When is not specified (default value), MS Word (or other program) will detect (or choose) the document East-Asian locale according to its own settings or other factors.  # noqa: E501

        :param locale_far_east: The locale_far_east.  # noqa: E501
        :type: str
        """
        self._locale_far_east = locale_far_east
    
    @property
    def protection_type(self):
        """
        Gets the protection_type.  # noqa: E501

        Write-protection type. Default value is NoProtection  # noqa: E501

        :return: The protection_type.  # noqa: E501
        :rtype: str
        """
        return self._protection_type

    @protection_type.setter
    def protection_type(self, protection_type):
        """
        Sets the protection_type.

        Write-protection type. Default value is NoProtection  # noqa: E501

        :param protection_type: The protection_type.  # noqa: E501
        :type: str
        """
        if protection_type is None:
            raise ValueError("Invalid value for `protection_type`, must not be `None`")  # noqa: E501
        allowed_values = ["NoProtection", "AllowOnlyRevisions", "AllowOnlyComments", "AllowOnlyFormFields", "ReadOnly"]  # noqa: E501
        if not protection_type.isdigit():	
            if protection_type not in allowed_values:
                raise ValueError(
                    "Invalid value for `protection_type` ({0}), must be one of {1}"  # noqa: E501
                    .format(protection_type, allowed_values))
            self._protection_type = protection_type
        else:
            self._protection_type = allowed_values[int(protection_type) if six.PY3 else long(protection_type)]
    
    @property
    def protection_password(self):
        """
        Gets the protection_password.  # noqa: E501

        Write-protection password. Used when protection type is specified.  # noqa: E501

        :return: The protection_password.  # noqa: E501
        :rtype: str
        """
        return self._protection_password

    @protection_password.setter
    def protection_password(self, protection_password):
        """
        Sets the protection_password.

        Write-protection password. Used when protection type is specified.  # noqa: E501

        :param protection_password: The protection_password.  # noqa: E501
        :type: str
        """
        self._protection_password = protection_password

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

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, WordProcessingSaveOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
