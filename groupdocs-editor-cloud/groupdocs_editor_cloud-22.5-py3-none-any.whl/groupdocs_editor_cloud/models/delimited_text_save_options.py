# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="DelimitedTextSaveOptions.py">
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

class DelimitedTextSaveOptions(SaveOptions):
    """
    Contains options for generating and saving text-based Spreadsheet documents (CSV, Tab-based etc.), that use a separator (delimiter)
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
        'encoding': 'str',
        'trim_leading_blank_row_and_column': 'bool',
        'keep_separators_for_blank_row': 'bool'
    }

    attribute_map = {
        'separator': 'Separator',
        'encoding': 'Encoding',
        'trim_leading_blank_row_and_column': 'TrimLeadingBlankRowAndColumn',
        'keep_separators_for_blank_row': 'KeepSeparatorsForBlankRow'
    }

    def __init__(self, separator=None, encoding=None, trim_leading_blank_row_and_column=None, keep_separators_for_blank_row=None, **kwargs):  # noqa: E501
        """Initializes new instance of DelimitedTextSaveOptions"""  # noqa: E501

        self._separator = None
        self._encoding = None
        self._trim_leading_blank_row_and_column = None
        self._keep_separators_for_blank_row = None

        if separator is not None:
            self.separator = separator
        if encoding is not None:
            self.encoding = encoding
        if trim_leading_blank_row_and_column is not None:
            self.trim_leading_blank_row_and_column = trim_leading_blank_row_and_column
        if keep_separators_for_blank_row is not None:
            self.keep_separators_for_blank_row = keep_separators_for_blank_row

        base = super(DelimitedTextSaveOptions, self)
        base.__init__(**kwargs)

        self.swagger_types.update(base.swagger_types)
        self.attribute_map.update(base.attribute_map)
    
    @property
    def separator(self):
        """
        Gets the separator.  # noqa: E501

        Allows to specify a string separator (delimiter) for text-based Spreadsheet documents  # noqa: E501

        :return: The separator.  # noqa: E501
        :rtype: str
        """
        return self._separator

    @separator.setter
    def separator(self, separator):
        """
        Sets the separator.

        Allows to specify a string separator (delimiter) for text-based Spreadsheet documents  # noqa: E501

        :param separator: The separator.  # noqa: E501
        :type: str
        """
        self._separator = separator
    
    @property
    def encoding(self):
        """
        Gets the encoding.  # noqa: E501

        Allows to set an encoding for the text-based Spreadsheet document. By default (and if not specified) is UTF-8.  # noqa: E501

        :return: The encoding.  # noqa: E501
        :rtype: str
        """
        return self._encoding

    @encoding.setter
    def encoding(self, encoding):
        """
        Sets the encoding.

        Allows to set an encoding for the text-based Spreadsheet document. By default (and if not specified) is UTF-8.  # noqa: E501

        :param encoding: The encoding.  # noqa: E501
        :type: str
        """
        self._encoding = encoding
    
    @property
    def trim_leading_blank_row_and_column(self):
        """
        Gets the trim_leading_blank_row_and_column.  # noqa: E501

        Indicates whether leading blank rows and columns should be trimmed like what MS Excel does  # noqa: E501

        :return: The trim_leading_blank_row_and_column.  # noqa: E501
        :rtype: bool
        """
        return self._trim_leading_blank_row_and_column

    @trim_leading_blank_row_and_column.setter
    def trim_leading_blank_row_and_column(self, trim_leading_blank_row_and_column):
        """
        Sets the trim_leading_blank_row_and_column.

        Indicates whether leading blank rows and columns should be trimmed like what MS Excel does  # noqa: E501

        :param trim_leading_blank_row_and_column: The trim_leading_blank_row_and_column.  # noqa: E501
        :type: bool
        """
        if trim_leading_blank_row_and_column is None:
            raise ValueError("Invalid value for `trim_leading_blank_row_and_column`, must not be `None`")  # noqa: E501
        self._trim_leading_blank_row_and_column = trim_leading_blank_row_and_column
    
    @property
    def keep_separators_for_blank_row(self):
        """
        Gets the keep_separators_for_blank_row.  # noqa: E501

        Indicates whether separators should be output for blank row. Default value is false which means the content for blank row will be empty.  # noqa: E501

        :return: The keep_separators_for_blank_row.  # noqa: E501
        :rtype: bool
        """
        return self._keep_separators_for_blank_row

    @keep_separators_for_blank_row.setter
    def keep_separators_for_blank_row(self, keep_separators_for_blank_row):
        """
        Sets the keep_separators_for_blank_row.

        Indicates whether separators should be output for blank row. Default value is false which means the content for blank row will be empty.  # noqa: E501

        :param keep_separators_for_blank_row: The keep_separators_for_blank_row.  # noqa: E501
        :type: bool
        """
        if keep_separators_for_blank_row is None:
            raise ValueError("Invalid value for `keep_separators_for_blank_row`, must not be `None`")  # noqa: E501
        self._keep_separators_for_blank_row = keep_separators_for_blank_row

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
        if not isinstance(other, DelimitedTextSaveOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
