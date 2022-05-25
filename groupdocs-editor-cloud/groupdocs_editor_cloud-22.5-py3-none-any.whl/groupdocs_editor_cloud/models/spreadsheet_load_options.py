# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="SpreadsheetLoadOptions.py">
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

class SpreadsheetLoadOptions(LoadOptions):
    """
    Allows to specify custom options for editing documents of all supportable Spreadsheet (Excel-compatible) formats
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'worksheet_index': 'int',
        'exclude_hidden_worksheets': 'bool'
    }

    attribute_map = {
        'worksheet_index': 'WorksheetIndex',
        'exclude_hidden_worksheets': 'ExcludeHiddenWorksheets'
    }

    def __init__(self, worksheet_index=None, exclude_hidden_worksheets=None, **kwargs):  # noqa: E501
        """Initializes new instance of SpreadsheetLoadOptions"""  # noqa: E501

        self._worksheet_index = None
        self._exclude_hidden_worksheets = None

        if worksheet_index is not None:
            self.worksheet_index = worksheet_index
        if exclude_hidden_worksheets is not None:
            self.exclude_hidden_worksheets = exclude_hidden_worksheets

        base = super(SpreadsheetLoadOptions, self)
        base.__init__(**kwargs)

        self.swagger_types.update(base.swagger_types)
        self.attribute_map.update(base.attribute_map)
    
    @property
    def worksheet_index(self):
        """
        Gets the worksheet_index.  # noqa: E501

        Allows to specify the 0-based index of the worksheet (tab) of the input Spreadsheet document, which should be converted to the HTML.  # noqa: E501

        :return: The worksheet_index.  # noqa: E501
        :rtype: int
        """
        return self._worksheet_index

    @worksheet_index.setter
    def worksheet_index(self, worksheet_index):
        """
        Sets the worksheet_index.

        Allows to specify the 0-based index of the worksheet (tab) of the input Spreadsheet document, which should be converted to the HTML.  # noqa: E501

        :param worksheet_index: The worksheet_index.  # noqa: E501
        :type: int
        """
        if worksheet_index is None:
            raise ValueError("Invalid value for `worksheet_index`, must not be `None`")  # noqa: E501
        self._worksheet_index = worksheet_index
    
    @property
    def exclude_hidden_worksheets(self):
        """
        Gets the exclude_hidden_worksheets.  # noqa: E501

        Allows to exclude hidden worksheets in the input Spreadsheet document, so they will be totally ignored. Default is false - hidden worksheets are available and processed as normal.  # noqa: E501

        :return: The exclude_hidden_worksheets.  # noqa: E501
        :rtype: bool
        """
        return self._exclude_hidden_worksheets

    @exclude_hidden_worksheets.setter
    def exclude_hidden_worksheets(self, exclude_hidden_worksheets):
        """
        Sets the exclude_hidden_worksheets.

        Allows to exclude hidden worksheets in the input Spreadsheet document, so they will be totally ignored. Default is false - hidden worksheets are available and processed as normal.  # noqa: E501

        :param exclude_hidden_worksheets: The exclude_hidden_worksheets.  # noqa: E501
        :type: bool
        """
        if exclude_hidden_worksheets is None:
            raise ValueError("Invalid value for `exclude_hidden_worksheets`, must not be `None`")  # noqa: E501
        self._exclude_hidden_worksheets = exclude_hidden_worksheets

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
        if not isinstance(other, SpreadsheetLoadOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
