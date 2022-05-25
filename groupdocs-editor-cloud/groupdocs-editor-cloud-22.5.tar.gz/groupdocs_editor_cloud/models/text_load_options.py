# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="TextLoadOptions.py">
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

class TextLoadOptions(LoadOptions):
    """
    Allows to specify custom options for loading plain text (TXT) documents
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
        'recognize_lists': 'bool',
        'leading_spaces': 'str',
        'trailing_spaces': 'str',
        'enable_pagination': 'bool'
    }

    attribute_map = {
        'encoding': 'Encoding',
        'recognize_lists': 'RecognizeLists',
        'leading_spaces': 'LeadingSpaces',
        'trailing_spaces': 'TrailingSpaces',
        'enable_pagination': 'EnablePagination'
    }

    def __init__(self, encoding=None, recognize_lists=None, leading_spaces=None, trailing_spaces=None, enable_pagination=None, **kwargs):  # noqa: E501
        """Initializes new instance of TextLoadOptions"""  # noqa: E501

        self._encoding = None
        self._recognize_lists = None
        self._leading_spaces = None
        self._trailing_spaces = None
        self._enable_pagination = None

        if encoding is not None:
            self.encoding = encoding
        if recognize_lists is not None:
            self.recognize_lists = recognize_lists
        if leading_spaces is not None:
            self.leading_spaces = leading_spaces
        if trailing_spaces is not None:
            self.trailing_spaces = trailing_spaces
        if enable_pagination is not None:
            self.enable_pagination = enable_pagination

        base = super(TextLoadOptions, self)
        base.__init__(**kwargs)

        self.swagger_types.update(base.swagger_types)
        self.attribute_map.update(base.attribute_map)
    
    @property
    def encoding(self):
        """
        Gets the encoding.  # noqa: E501

        Character encoding of the text document, which will be applied for its opening  # noqa: E501

        :return: The encoding.  # noqa: E501
        :rtype: str
        """
        return self._encoding

    @encoding.setter
    def encoding(self, encoding):
        """
        Sets the encoding.

        Character encoding of the text document, which will be applied for its opening  # noqa: E501

        :param encoding: The encoding.  # noqa: E501
        :type: str
        """
        self._encoding = encoding
    
    @property
    def recognize_lists(self):
        """
        Gets the recognize_lists.  # noqa: E501

        Allows to specify how numbered list items are recognized when document is imported from plain text format. The default value is true.  # noqa: E501

        :return: The recognize_lists.  # noqa: E501
        :rtype: bool
        """
        return self._recognize_lists

    @recognize_lists.setter
    def recognize_lists(self, recognize_lists):
        """
        Sets the recognize_lists.

        Allows to specify how numbered list items are recognized when document is imported from plain text format. The default value is true.  # noqa: E501

        :param recognize_lists: The recognize_lists.  # noqa: E501
        :type: bool
        """
        if recognize_lists is None:
            raise ValueError("Invalid value for `recognize_lists`, must not be `None`")  # noqa: E501
        self._recognize_lists = recognize_lists
    
    @property
    def leading_spaces(self):
        """
        Gets the leading_spaces.  # noqa: E501

        Gets or sets preferred option of a leading space handling. By default converts leading spaces to the left indent.  # noqa: E501

        :return: The leading_spaces.  # noqa: E501
        :rtype: str
        """
        return self._leading_spaces

    @leading_spaces.setter
    def leading_spaces(self, leading_spaces):
        """
        Sets the leading_spaces.

        Gets or sets preferred option of a leading space handling. By default converts leading spaces to the left indent.  # noqa: E501

        :param leading_spaces: The leading_spaces.  # noqa: E501
        :type: str
        """
        if leading_spaces is None:
            raise ValueError("Invalid value for `leading_spaces`, must not be `None`")  # noqa: E501
        allowed_values = ["ConvertToIndent", "Preserve", "Trim"]  # noqa: E501
        if not leading_spaces.isdigit():	
            if leading_spaces not in allowed_values:
                raise ValueError(
                    "Invalid value for `leading_spaces` ({0}), must be one of {1}"  # noqa: E501
                    .format(leading_spaces, allowed_values))
            self._leading_spaces = leading_spaces
        else:
            self._leading_spaces = allowed_values[int(leading_spaces) if six.PY3 else long(leading_spaces)]
    
    @property
    def trailing_spaces(self):
        """
        Gets the trailing_spaces.  # noqa: E501

        Gets or sets preferred option of a trailing space handling. By default truncates all trailing spaces.  # noqa: E501

        :return: The trailing_spaces.  # noqa: E501
        :rtype: str
        """
        return self._trailing_spaces

    @trailing_spaces.setter
    def trailing_spaces(self, trailing_spaces):
        """
        Sets the trailing_spaces.

        Gets or sets preferred option of a trailing space handling. By default truncates all trailing spaces.  # noqa: E501

        :param trailing_spaces: The trailing_spaces.  # noqa: E501
        :type: str
        """
        if trailing_spaces is None:
            raise ValueError("Invalid value for `trailing_spaces`, must not be `None`")  # noqa: E501
        allowed_values = ["Trim", "Preserve"]  # noqa: E501
        if not trailing_spaces.isdigit():	
            if trailing_spaces not in allowed_values:
                raise ValueError(
                    "Invalid value for `trailing_spaces` ({0}), must be one of {1}"  # noqa: E501
                    .format(trailing_spaces, allowed_values))
            self._trailing_spaces = trailing_spaces
        else:
            self._trailing_spaces = allowed_values[int(trailing_spaces) if six.PY3 else long(trailing_spaces)]
    
    @property
    def enable_pagination(self):
        """
        Gets the enable_pagination.  # noqa: E501

        Allows to enable or disable pagination in the resultant HTML document. By default is disabled (false).  # noqa: E501

        :return: The enable_pagination.  # noqa: E501
        :rtype: bool
        """
        return self._enable_pagination

    @enable_pagination.setter
    def enable_pagination(self, enable_pagination):
        """
        Sets the enable_pagination.

        Allows to enable or disable pagination in the resultant HTML document. By default is disabled (false).  # noqa: E501

        :param enable_pagination: The enable_pagination.  # noqa: E501
        :type: bool
        """
        if enable_pagination is None:
            raise ValueError("Invalid value for `enable_pagination`, must not be `None`")  # noqa: E501
        self._enable_pagination = enable_pagination

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
        if not isinstance(other, TextLoadOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
