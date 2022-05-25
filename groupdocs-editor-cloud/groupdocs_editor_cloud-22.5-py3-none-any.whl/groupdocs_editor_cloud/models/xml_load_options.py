# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="XmlLoadOptions.py">
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

from groupdocs_editor_cloud.models import LoadOptions

class XmlLoadOptions(LoadOptions):
    """
    Allows to specify custom options for loading XML (eXtensible Markup Language) documents
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'encoding': 'str',
        'fix_incorrect_structure': 'bool',
        'recognize_uris': 'bool',
        'recognize_emails': 'bool',
        'trim_trailing_whitespaces': 'bool',
        'attribute_values_quote_type': 'str'
    }

    attribute_map = {
        'encoding': 'Encoding',
        'fix_incorrect_structure': 'FixIncorrectStructure',
        'recognize_uris': 'RecognizeUris',
        'recognize_emails': 'RecognizeEmails',
        'trim_trailing_whitespaces': 'TrimTrailingWhitespaces',
        'attribute_values_quote_type': 'AttributeValuesQuoteType'
    }

    def __init__(self, encoding=None, fix_incorrect_structure=None, recognize_uris=None, recognize_emails=None, trim_trailing_whitespaces=None, attribute_values_quote_type=None, **kwargs):  # noqa: E501
        """Initializes new instance of XmlLoadOptions"""  # noqa: E501

        self._encoding = None
        self._fix_incorrect_structure = None
        self._recognize_uris = None
        self._recognize_emails = None
        self._trim_trailing_whitespaces = None
        self._attribute_values_quote_type = None

        if encoding is not None:
            self.encoding = encoding
        if fix_incorrect_structure is not None:
            self.fix_incorrect_structure = fix_incorrect_structure
        if recognize_uris is not None:
            self.recognize_uris = recognize_uris
        if recognize_emails is not None:
            self.recognize_emails = recognize_emails
        if trim_trailing_whitespaces is not None:
            self.trim_trailing_whitespaces = trim_trailing_whitespaces
        if attribute_values_quote_type is not None:
            self.attribute_values_quote_type = attribute_values_quote_type

        base = super(XmlLoadOptions, self)
        base.__init__(**kwargs)

        self.swagger_types.update(base.swagger_types)
        self.attribute_map.update(base.attribute_map)
    
    @property
    def encoding(self):
        """
        Gets the encoding.  # noqa: E501

        Character encoding of the text document, which will be applied for its opening. By default is null - internal document encoding will be applied.               # noqa: E501

        :return: The encoding.  # noqa: E501
        :rtype: str
        """
        return self._encoding

    @encoding.setter
    def encoding(self, encoding):
        """
        Sets the encoding.

        Character encoding of the text document, which will be applied for its opening. By default is null - internal document encoding will be applied.               # noqa: E501

        :param encoding: The encoding.  # noqa: E501
        :type: str
        """
        self._encoding = encoding
    
    @property
    def fix_incorrect_structure(self):
        """
        Gets the fix_incorrect_structure.  # noqa: E501

        Allows to enable or disable mechanism for fixing corrupted XML structure. By default is disabled (false).               # noqa: E501

        :return: The fix_incorrect_structure.  # noqa: E501
        :rtype: bool
        """
        return self._fix_incorrect_structure

    @fix_incorrect_structure.setter
    def fix_incorrect_structure(self, fix_incorrect_structure):
        """
        Sets the fix_incorrect_structure.

        Allows to enable or disable mechanism for fixing corrupted XML structure. By default is disabled (false).               # noqa: E501

        :param fix_incorrect_structure: The fix_incorrect_structure.  # noqa: E501
        :type: bool
        """
        if fix_incorrect_structure is None:
            raise ValueError("Invalid value for `fix_incorrect_structure`, must not be `None`")  # noqa: E501
        self._fix_incorrect_structure = fix_incorrect_structure
    
    @property
    def recognize_uris(self):
        """
        Gets the recognize_uris.  # noqa: E501

        Allows to enable URI recognition algorithm  # noqa: E501

        :return: The recognize_uris.  # noqa: E501
        :rtype: bool
        """
        return self._recognize_uris

    @recognize_uris.setter
    def recognize_uris(self, recognize_uris):
        """
        Sets the recognize_uris.

        Allows to enable URI recognition algorithm  # noqa: E501

        :param recognize_uris: The recognize_uris.  # noqa: E501
        :type: bool
        """
        if recognize_uris is None:
            raise ValueError("Invalid value for `recognize_uris`, must not be `None`")  # noqa: E501
        self._recognize_uris = recognize_uris
    
    @property
    def recognize_emails(self):
        """
        Gets the recognize_emails.  # noqa: E501

        Allows to enable recognition algorithm for email addresses in attribute values  # noqa: E501

        :return: The recognize_emails.  # noqa: E501
        :rtype: bool
        """
        return self._recognize_emails

    @recognize_emails.setter
    def recognize_emails(self, recognize_emails):
        """
        Sets the recognize_emails.

        Allows to enable recognition algorithm for email addresses in attribute values  # noqa: E501

        :param recognize_emails: The recognize_emails.  # noqa: E501
        :type: bool
        """
        if recognize_emails is None:
            raise ValueError("Invalid value for `recognize_emails`, must not be `None`")  # noqa: E501
        self._recognize_emails = recognize_emails
    
    @property
    def trim_trailing_whitespaces(self):
        """
        Gets the trim_trailing_whitespaces.  # noqa: E501

        Allows to enable the truncation of trailing whitespaces in the inner-tag text. By default is disabled (false) - trailing whitespaces will be preserved.               # noqa: E501

        :return: The trim_trailing_whitespaces.  # noqa: E501
        :rtype: bool
        """
        return self._trim_trailing_whitespaces

    @trim_trailing_whitespaces.setter
    def trim_trailing_whitespaces(self, trim_trailing_whitespaces):
        """
        Sets the trim_trailing_whitespaces.

        Allows to enable the truncation of trailing whitespaces in the inner-tag text. By default is disabled (false) - trailing whitespaces will be preserved.               # noqa: E501

        :param trim_trailing_whitespaces: The trim_trailing_whitespaces.  # noqa: E501
        :type: bool
        """
        if trim_trailing_whitespaces is None:
            raise ValueError("Invalid value for `trim_trailing_whitespaces`, must not be `None`")  # noqa: E501
        self._trim_trailing_whitespaces = trim_trailing_whitespaces
    
    @property
    def attribute_values_quote_type(self):
        """
        Gets the attribute_values_quote_type.  # noqa: E501

        Allows to specify quote type (single or double quotes) for attribute values. Double quotes are default.               # noqa: E501

        :return: The attribute_values_quote_type.  # noqa: E501
        :rtype: str
        """
        return self._attribute_values_quote_type

    @attribute_values_quote_type.setter
    def attribute_values_quote_type(self, attribute_values_quote_type):
        """
        Sets the attribute_values_quote_type.

        Allows to specify quote type (single or double quotes) for attribute values. Double quotes are default.               # noqa: E501

        :param attribute_values_quote_type: The attribute_values_quote_type.  # noqa: E501
        :type: str
        """
        if attribute_values_quote_type is None:
            raise ValueError("Invalid value for `attribute_values_quote_type`, must not be `None`")  # noqa: E501
        allowed_values = ["DoubleQuote", "SingleQuote"]  # noqa: E501
        if not attribute_values_quote_type.isdigit():	
            if attribute_values_quote_type not in allowed_values:
                raise ValueError(
                    "Invalid value for `attribute_values_quote_type` ({0}), must be one of {1}"  # noqa: E501
                    .format(attribute_values_quote_type, allowed_values))
            self._attribute_values_quote_type = attribute_values_quote_type
        else:
            self._attribute_values_quote_type = allowed_values[int(attribute_values_quote_type) if six.PY3 else long(attribute_values_quote_type)]

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
        if not isinstance(other, XmlLoadOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
