# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="PresentationLoadOptions.py">
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

class PresentationLoadOptions(LoadOptions):
    """
    Allows to specify custom options for editing documents of all supportable Presentation (PowerPoint-compatible) formats
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'slide_number': 'int',
        'show_hidden_slides': 'bool'
    }

    attribute_map = {
        'slide_number': 'SlideNumber',
        'show_hidden_slides': 'ShowHiddenSlides'
    }

    def __init__(self, slide_number=None, show_hidden_slides=None, **kwargs):  # noqa: E501
        """Initializes new instance of PresentationLoadOptions"""  # noqa: E501

        self._slide_number = None
        self._show_hidden_slides = None

        if slide_number is not None:
            self.slide_number = slide_number
        if show_hidden_slides is not None:
            self.show_hidden_slides = show_hidden_slides

        base = super(PresentationLoadOptions, self)
        base.__init__(**kwargs)

        self.swagger_types.update(base.swagger_types)
        self.attribute_map.update(base.attribute_map)
    
    @property
    def slide_number(self):
        """
        Gets the slide_number.  # noqa: E501

        Allows to specify the slide number, which should be opened for editing  # noqa: E501

        :return: The slide_number.  # noqa: E501
        :rtype: int
        """
        return self._slide_number

    @slide_number.setter
    def slide_number(self, slide_number):
        """
        Sets the slide_number.

        Allows to specify the slide number, which should be opened for editing  # noqa: E501

        :param slide_number: The slide_number.  # noqa: E501
        :type: int
        """
        if slide_number is None:
            raise ValueError("Invalid value for `slide_number`, must not be `None`")  # noqa: E501
        self._slide_number = slide_number
    
    @property
    def show_hidden_slides(self):
        """
        Gets the show_hidden_slides.  # noqa: E501

        Specifies whether the hidden slides should be included or not. Default is false     - hidden slides are not shown and exception will be thrown while trying to edit  # noqa: E501

        :return: The show_hidden_slides.  # noqa: E501
        :rtype: bool
        """
        return self._show_hidden_slides

    @show_hidden_slides.setter
    def show_hidden_slides(self, show_hidden_slides):
        """
        Sets the show_hidden_slides.

        Specifies whether the hidden slides should be included or not. Default is false     - hidden slides are not shown and exception will be thrown while trying to edit  # noqa: E501

        :param show_hidden_slides: The show_hidden_slides.  # noqa: E501
        :type: bool
        """
        if show_hidden_slides is None:
            raise ValueError("Invalid value for `show_hidden_slides`, must not be `None`")  # noqa: E501
        self._show_hidden_slides = show_hidden_slides

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
        if not isinstance(other, PresentationLoadOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
