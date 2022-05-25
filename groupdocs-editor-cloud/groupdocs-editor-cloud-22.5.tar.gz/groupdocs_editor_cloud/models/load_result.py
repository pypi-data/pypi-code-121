# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="LoadResult.py">
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

class LoadResult(object):
    """
    Describes load result
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'html_path': 'str',
        'resources_path': 'str'
    }

    attribute_map = {
        'html_path': 'HtmlPath',
        'resources_path': 'ResourcesPath'
    }

    def __init__(self, html_path=None, resources_path=None, **kwargs):  # noqa: E501
        """Initializes new instance of LoadResult"""  # noqa: E501

        self._html_path = None
        self._resources_path = None

        if html_path is not None:
            self.html_path = html_path
        if resources_path is not None:
            self.resources_path = resources_path
    
    @property
    def html_path(self):
        """
        Gets the html_path.  # noqa: E501

        Path of the editable document  # noqa: E501

        :return: The html_path.  # noqa: E501
        :rtype: str
        """
        return self._html_path

    @html_path.setter
    def html_path(self, html_path):
        """
        Sets the html_path.

        Path of the editable document  # noqa: E501

        :param html_path: The html_path.  # noqa: E501
        :type: str
        """
        self._html_path = html_path
    
    @property
    def resources_path(self):
        """
        Gets the resources_path.  # noqa: E501

        Path of the document resources  # noqa: E501

        :return: The resources_path.  # noqa: E501
        :rtype: str
        """
        return self._resources_path

    @resources_path.setter
    def resources_path(self, resources_path):
        """
        Sets the resources_path.

        Path of the document resources  # noqa: E501

        :param resources_path: The resources_path.  # noqa: E501
        :type: str
        """
        self._resources_path = resources_path

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
        if not isinstance(other, LoadResult):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
