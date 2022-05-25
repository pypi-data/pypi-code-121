# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="WordProcessingLoadOptions.py">
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

class WordProcessingLoadOptions(LoadOptions):
    """
    Allows to specify custom options for loading WordProcessing-compliant documents
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'enable_pagination': 'bool',
        'enable_language_information': 'bool',
        'font_extraction': 'str'
    }

    attribute_map = {
        'enable_pagination': 'EnablePagination',
        'enable_language_information': 'EnableLanguageInformation',
        'font_extraction': 'FontExtraction'
    }

    def __init__(self, enable_pagination=None, enable_language_information=None, font_extraction=None, **kwargs):  # noqa: E501
        """Initializes new instance of WordProcessingLoadOptions"""  # noqa: E501

        self._enable_pagination = None
        self._enable_language_information = None
        self._font_extraction = None

        if enable_pagination is not None:
            self.enable_pagination = enable_pagination
        if enable_language_information is not None:
            self.enable_language_information = enable_language_information
        if font_extraction is not None:
            self.font_extraction = font_extraction

        base = super(WordProcessingLoadOptions, self)
        base.__init__(**kwargs)

        self.swagger_types.update(base.swagger_types)
        self.attribute_map.update(base.attribute_map)
    
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
    
    @property
    def enable_language_information(self):
        """
        Gets the enable_language_information.  # noqa: E501

        Specifies whether language information is exported to the HTML markup in a form of 'lang' HTML attributes. This option may be useful for roundtrip conversion of the multi-language documents. By default it is disabled (false).  # noqa: E501

        :return: The enable_language_information.  # noqa: E501
        :rtype: bool
        """
        return self._enable_language_information

    @enable_language_information.setter
    def enable_language_information(self, enable_language_information):
        """
        Sets the enable_language_information.

        Specifies whether language information is exported to the HTML markup in a form of 'lang' HTML attributes. This option may be useful for roundtrip conversion of the multi-language documents. By default it is disabled (false).  # noqa: E501

        :param enable_language_information: The enable_language_information.  # noqa: E501
        :type: bool
        """
        if enable_language_information is None:
            raise ValueError("Invalid value for `enable_language_information`, must not be `None`")  # noqa: E501
        self._enable_language_information = enable_language_information
    
    @property
    def font_extraction(self):
        """
        Gets the font_extraction.  # noqa: E501

        Responsible for extracting font resources, which are used in the input WordProcessing document. By default doesn't extract any fonts (NotExtract).  # noqa: E501

        :return: The font_extraction.  # noqa: E501
        :rtype: str
        """
        return self._font_extraction

    @font_extraction.setter
    def font_extraction(self, font_extraction):
        """
        Sets the font_extraction.

        Responsible for extracting font resources, which are used in the input WordProcessing document. By default doesn't extract any fonts (NotExtract).  # noqa: E501

        :param font_extraction: The font_extraction.  # noqa: E501
        :type: str
        """
        if font_extraction is None:
            raise ValueError("Invalid value for `font_extraction`, must not be `None`")  # noqa: E501
        allowed_values = ["NotExtract", "ExtractAllEmbedded", "ExtractEmbeddedWithoutSystem", "ExtractAll"]  # noqa: E501
        if not font_extraction.isdigit():	
            if font_extraction not in allowed_values:
                raise ValueError(
                    "Invalid value for `font_extraction` ({0}), must be one of {1}"  # noqa: E501
                    .format(font_extraction, allowed_values))
            self._font_extraction = font_extraction
        else:
            self._font_extraction = allowed_values[int(font_extraction) if six.PY3 else long(font_extraction)]

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
        if not isinstance(other, WordProcessingLoadOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
