# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="PdfSaveOptions.py">
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

class PdfSaveOptions(SaveOptions):
    """
    Allows to specify custom options for generating and saving PDF (Portable Document Format) documents
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
        'compliance': 'str'
    }

    attribute_map = {
        'password': 'Password',
        'compliance': 'Compliance'
    }

    def __init__(self, password=None, compliance=None, **kwargs):  # noqa: E501
        """Initializes new instance of PdfSaveOptions"""  # noqa: E501

        self._password = None
        self._compliance = None

        if password is not None:
            self.password = password
        if compliance is not None:
            self.compliance = compliance

        base = super(PdfSaveOptions, self)
        base.__init__(**kwargs)

        self.swagger_types.update(base.swagger_types)
        self.attribute_map.update(base.attribute_map)
    
    @property
    def password(self):
        """
        Gets the password.  # noqa: E501

        Password, which will be applied to the generated PDF document as user password, required for opening. If NULL or empty, no password will be applied to the document. Otherwise, document will be encrypted with RC4 (key length of 128 bit).               # noqa: E501

        :return: The password.  # noqa: E501
        :rtype: str
        """
        return self._password

    @password.setter
    def password(self, password):
        """
        Sets the password.

        Password, which will be applied to the generated PDF document as user password, required for opening. If NULL or empty, no password will be applied to the document. Otherwise, document will be encrypted with RC4 (key length of 128 bit).               # noqa: E501

        :param password: The password.  # noqa: E501
        :type: str
        """
        self._password = password
    
    @property
    def compliance(self):
        """
        Gets the compliance.  # noqa: E501

        Specifies the PDF standards compliance level for output documents. Default is PdfCompliance.Pdf15.               # noqa: E501

        :return: The compliance.  # noqa: E501
        :rtype: str
        """
        return self._compliance

    @compliance.setter
    def compliance(self, compliance):
        """
        Sets the compliance.

        Specifies the PDF standards compliance level for output documents. Default is PdfCompliance.Pdf15.               # noqa: E501

        :param compliance: The compliance.  # noqa: E501
        :type: str
        """
        if compliance is None:
            raise ValueError("Invalid value for `compliance`, must not be `None`")  # noqa: E501
        allowed_values = ["Pdf15", "PdfA1a", "PdfA1b"]  # noqa: E501
        if not compliance.isdigit():	
            if compliance not in allowed_values:
                raise ValueError(
                    "Invalid value for `compliance` ({0}), must be one of {1}"  # noqa: E501
                    .format(compliance, allowed_values))
            self._compliance = compliance
        else:
            self._compliance = allowed_values[int(compliance) if six.PY3 else long(compliance)]

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
        if not isinstance(other, PdfSaveOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
