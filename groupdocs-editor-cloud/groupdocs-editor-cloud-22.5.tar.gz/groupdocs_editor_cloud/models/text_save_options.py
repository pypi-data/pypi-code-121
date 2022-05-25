# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="TextSaveOptions.py">
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

class TextSaveOptions(SaveOptions):
    """
    Allows to specify custom options for generating and saving plain text (TXT) documents
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
        'add_bidi_marks': 'bool',
        'preserve_table_layout': 'bool'
    }

    attribute_map = {
        'encoding': 'Encoding',
        'add_bidi_marks': 'AddBidiMarks',
        'preserve_table_layout': 'PreserveTableLayout'
    }

    def __init__(self, encoding=None, add_bidi_marks=None, preserve_table_layout=None, **kwargs):  # noqa: E501
        """Initializes new instance of TextSaveOptions"""  # noqa: E501

        self._encoding = None
        self._add_bidi_marks = None
        self._preserve_table_layout = None

        if encoding is not None:
            self.encoding = encoding
        if add_bidi_marks is not None:
            self.add_bidi_marks = add_bidi_marks
        if preserve_table_layout is not None:
            self.preserve_table_layout = preserve_table_layout

        base = super(TextSaveOptions, self)
        base.__init__(**kwargs)

        self.swagger_types.update(base.swagger_types)
        self.attribute_map.update(base.attribute_map)
    
    @property
    def encoding(self):
        """
        Gets the encoding.  # noqa: E501

        Character encoding of the text document, which will be applied for its saving  # noqa: E501

        :return: The encoding.  # noqa: E501
        :rtype: str
        """
        return self._encoding

    @encoding.setter
    def encoding(self, encoding):
        """
        Sets the encoding.

        Character encoding of the text document, which will be applied for its saving  # noqa: E501

        :param encoding: The encoding.  # noqa: E501
        :type: str
        """
        self._encoding = encoding
    
    @property
    def add_bidi_marks(self):
        """
        Gets the add_bidi_marks.  # noqa: E501

        Specifies whether to add bi-directional marks before each BiDi run when exporting in plain text format  # noqa: E501

        :return: The add_bidi_marks.  # noqa: E501
        :rtype: bool
        """
        return self._add_bidi_marks

    @add_bidi_marks.setter
    def add_bidi_marks(self, add_bidi_marks):
        """
        Sets the add_bidi_marks.

        Specifies whether to add bi-directional marks before each BiDi run when exporting in plain text format  # noqa: E501

        :param add_bidi_marks: The add_bidi_marks.  # noqa: E501
        :type: bool
        """
        if add_bidi_marks is None:
            raise ValueError("Invalid value for `add_bidi_marks`, must not be `None`")  # noqa: E501
        self._add_bidi_marks = add_bidi_marks
    
    @property
    def preserve_table_layout(self):
        """
        Gets the preserve_table_layout.  # noqa: E501

        Specifies whether the program should attempt to preserve layout of tables when saving in the plain text format. The default value is false.  # noqa: E501

        :return: The preserve_table_layout.  # noqa: E501
        :rtype: bool
        """
        return self._preserve_table_layout

    @preserve_table_layout.setter
    def preserve_table_layout(self, preserve_table_layout):
        """
        Sets the preserve_table_layout.

        Specifies whether the program should attempt to preserve layout of tables when saving in the plain text format. The default value is false.  # noqa: E501

        :param preserve_table_layout: The preserve_table_layout.  # noqa: E501
        :type: bool
        """
        if preserve_table_layout is None:
            raise ValueError("Invalid value for `preserve_table_layout`, must not be `None`")  # noqa: E501
        self._preserve_table_layout = preserve_table_layout

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
        if not isinstance(other, TextSaveOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
