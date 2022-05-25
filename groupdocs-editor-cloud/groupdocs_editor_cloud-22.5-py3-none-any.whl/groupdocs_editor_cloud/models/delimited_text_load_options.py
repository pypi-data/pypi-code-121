# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="DelimitedTextLoadOptions.py">
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

class DelimitedTextLoadOptions(LoadOptions):
    """
    Options for loading text-based Spreadsheet documents (CSV, Tab-based etc.), that use a separator (delimiter)
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'separator': 'str',
        'convert_date_time_data': 'bool',
        'convert_numeric_data': 'bool',
        'treat_consecutive_delimiters_as_one': 'bool'
    }

    attribute_map = {
        'separator': 'Separator',
        'convert_date_time_data': 'ConvertDateTimeData',
        'convert_numeric_data': 'ConvertNumericData',
        'treat_consecutive_delimiters_as_one': 'TreatConsecutiveDelimitersAsOne'
    }

    def __init__(self, separator=None, convert_date_time_data=None, convert_numeric_data=None, treat_consecutive_delimiters_as_one=None, **kwargs):  # noqa: E501
        """Initializes new instance of DelimitedTextLoadOptions"""  # noqa: E501

        self._separator = None
        self._convert_date_time_data = None
        self._convert_numeric_data = None
        self._treat_consecutive_delimiters_as_one = None

        if separator is not None:
            self.separator = separator
        if convert_date_time_data is not None:
            self.convert_date_time_data = convert_date_time_data
        if convert_numeric_data is not None:
            self.convert_numeric_data = convert_numeric_data
        if treat_consecutive_delimiters_as_one is not None:
            self.treat_consecutive_delimiters_as_one = treat_consecutive_delimiters_as_one

        base = super(DelimitedTextLoadOptions, self)
        base.__init__(**kwargs)

        self.swagger_types.update(base.swagger_types)
        self.attribute_map.update(base.attribute_map)
    
    @property
    def separator(self):
        """
        Gets the separator.  # noqa: E501

        Allows to specify a string separator (delimiter) for text-based Spreadsheet documents               # noqa: E501

        :return: The separator.  # noqa: E501
        :rtype: str
        """
        return self._separator

    @separator.setter
    def separator(self, separator):
        """
        Sets the separator.

        Allows to specify a string separator (delimiter) for text-based Spreadsheet documents               # noqa: E501

        :param separator: The separator.  # noqa: E501
        :type: str
        """
        self._separator = separator
    
    @property
    def convert_date_time_data(self):
        """
        Gets the convert_date_time_data.  # noqa: E501

        Gets or sets a value that indicates whether the string in text-based document is converted to the date data. Default is false.  # noqa: E501

        :return: The convert_date_time_data.  # noqa: E501
        :rtype: bool
        """
        return self._convert_date_time_data

    @convert_date_time_data.setter
    def convert_date_time_data(self, convert_date_time_data):
        """
        Sets the convert_date_time_data.

        Gets or sets a value that indicates whether the string in text-based document is converted to the date data. Default is false.  # noqa: E501

        :param convert_date_time_data: The convert_date_time_data.  # noqa: E501
        :type: bool
        """
        if convert_date_time_data is None:
            raise ValueError("Invalid value for `convert_date_time_data`, must not be `None`")  # noqa: E501
        self._convert_date_time_data = convert_date_time_data
    
    @property
    def convert_numeric_data(self):
        """
        Gets the convert_numeric_data.  # noqa: E501

        Gets or sets a value that indicates whether the string in text-based document is converted to numeric data. Default is false.  # noqa: E501

        :return: The convert_numeric_data.  # noqa: E501
        :rtype: bool
        """
        return self._convert_numeric_data

    @convert_numeric_data.setter
    def convert_numeric_data(self, convert_numeric_data):
        """
        Sets the convert_numeric_data.

        Gets or sets a value that indicates whether the string in text-based document is converted to numeric data. Default is false.  # noqa: E501

        :param convert_numeric_data: The convert_numeric_data.  # noqa: E501
        :type: bool
        """
        if convert_numeric_data is None:
            raise ValueError("Invalid value for `convert_numeric_data`, must not be `None`")  # noqa: E501
        self._convert_numeric_data = convert_numeric_data
    
    @property
    def treat_consecutive_delimiters_as_one(self):
        """
        Gets the treat_consecutive_delimiters_as_one.  # noqa: E501

        Defines whether consecutive delimiters should be treated as one. By default is false.  # noqa: E501

        :return: The treat_consecutive_delimiters_as_one.  # noqa: E501
        :rtype: bool
        """
        return self._treat_consecutive_delimiters_as_one

    @treat_consecutive_delimiters_as_one.setter
    def treat_consecutive_delimiters_as_one(self, treat_consecutive_delimiters_as_one):
        """
        Sets the treat_consecutive_delimiters_as_one.

        Defines whether consecutive delimiters should be treated as one. By default is false.  # noqa: E501

        :param treat_consecutive_delimiters_as_one: The treat_consecutive_delimiters_as_one.  # noqa: E501
        :type: bool
        """
        if treat_consecutive_delimiters_as_one is None:
            raise ValueError("Invalid value for `treat_consecutive_delimiters_as_one`, must not be `None`")  # noqa: E501
        self._treat_consecutive_delimiters_as_one = treat_consecutive_delimiters_as_one

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
        if not isinstance(other, DelimitedTextLoadOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
