# coding: utf-8

"""
    LUSID API

    FINBOURNE Technology  # noqa: E501

    The version of the OpenAPI document: 0.11.4385
    Contact: info@finbourne.com
    Generated by: https://openapi-generator.tech
"""


try:
    from inspect import getfullargspec
except ImportError:
    from inspect import getargspec as getfullargspec
import pprint
import re  # noqa: F401
import six

from lusid.configuration import Configuration


class UpsertReturnsResponse(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
      required_map (dict): The key is attribute name
                           and the value is whether it is 'required' or 'optional'.
    """
    openapi_types = {
        'version': 'Version',
        'href': 'str',
        'values': 'list[dict(str, datetime)]',
        'failed': 'list[dict(str, ErrorDetail)]',
        'links': 'list[Link]'
    }

    attribute_map = {
        'version': 'version',
        'href': 'href',
        'values': 'values',
        'failed': 'failed',
        'links': 'links'
    }

    required_map = {
        'version': 'required',
        'href': 'optional',
        'values': 'optional',
        'failed': 'optional',
        'links': 'optional'
    }

    def __init__(self, version=None, href=None, values=None, failed=None, links=None, local_vars_configuration=None):  # noqa: E501
        """UpsertReturnsResponse - a model defined in OpenAPI"
        
        :param version:  (required)
        :type version: lusid.Version
        :param href:  The specific Uniform Resource Identifier (URI) for this resource at the requested effective and asAt datetime.
        :type href: str
        :param values:  The set of values that were successfully retrieved.
        :type values: list[dict(str, datetime)]
        :param failed:  The set of values that could not be retrieved due along with a reason for this, e.g badly formed request.
        :type failed: list[dict(str, ErrorDetail)]
        :param links:  Collection of links.
        :type links: list[lusid.Link]

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._version = None
        self._href = None
        self._values = None
        self._failed = None
        self._links = None
        self.discriminator = None

        self.version = version
        self.href = href
        self.values = values
        self.failed = failed
        self.links = links

    @property
    def version(self):
        """Gets the version of this UpsertReturnsResponse.  # noqa: E501


        :return: The version of this UpsertReturnsResponse.  # noqa: E501
        :rtype: lusid.Version
        """
        return self._version

    @version.setter
    def version(self, version):
        """Sets the version of this UpsertReturnsResponse.


        :param version: The version of this UpsertReturnsResponse.  # noqa: E501
        :type version: lusid.Version
        """
        if self.local_vars_configuration.client_side_validation and version is None:  # noqa: E501
            raise ValueError("Invalid value for `version`, must not be `None`")  # noqa: E501

        self._version = version

    @property
    def href(self):
        """Gets the href of this UpsertReturnsResponse.  # noqa: E501

        The specific Uniform Resource Identifier (URI) for this resource at the requested effective and asAt datetime.  # noqa: E501

        :return: The href of this UpsertReturnsResponse.  # noqa: E501
        :rtype: str
        """
        return self._href

    @href.setter
    def href(self, href):
        """Sets the href of this UpsertReturnsResponse.

        The specific Uniform Resource Identifier (URI) for this resource at the requested effective and asAt datetime.  # noqa: E501

        :param href: The href of this UpsertReturnsResponse.  # noqa: E501
        :type href: str
        """

        self._href = href

    @property
    def values(self):
        """Gets the values of this UpsertReturnsResponse.  # noqa: E501

        The set of values that were successfully retrieved.  # noqa: E501

        :return: The values of this UpsertReturnsResponse.  # noqa: E501
        :rtype: list[dict(str, datetime)]
        """
        return self._values

    @values.setter
    def values(self, values):
        """Sets the values of this UpsertReturnsResponse.

        The set of values that were successfully retrieved.  # noqa: E501

        :param values: The values of this UpsertReturnsResponse.  # noqa: E501
        :type values: list[dict(str, datetime)]
        """

        self._values = values

    @property
    def failed(self):
        """Gets the failed of this UpsertReturnsResponse.  # noqa: E501

        The set of values that could not be retrieved due along with a reason for this, e.g badly formed request.  # noqa: E501

        :return: The failed of this UpsertReturnsResponse.  # noqa: E501
        :rtype: list[dict(str, ErrorDetail)]
        """
        return self._failed

    @failed.setter
    def failed(self, failed):
        """Sets the failed of this UpsertReturnsResponse.

        The set of values that could not be retrieved due along with a reason for this, e.g badly formed request.  # noqa: E501

        :param failed: The failed of this UpsertReturnsResponse.  # noqa: E501
        :type failed: list[dict(str, ErrorDetail)]
        """

        self._failed = failed

    @property
    def links(self):
        """Gets the links of this UpsertReturnsResponse.  # noqa: E501

        Collection of links.  # noqa: E501

        :return: The links of this UpsertReturnsResponse.  # noqa: E501
        :rtype: list[lusid.Link]
        """
        return self._links

    @links.setter
    def links(self, links):
        """Sets the links of this UpsertReturnsResponse.

        Collection of links.  # noqa: E501

        :param links: The links of this UpsertReturnsResponse.  # noqa: E501
        :type links: list[lusid.Link]
        """

        self._links = links

    def to_dict(self, serialize=False):
        """Returns the model properties as a dict"""
        result = {}

        def convert(x):
            if hasattr(x, "to_dict"):
                args = getfullargspec(x.to_dict).args
                if len(args) == 1:
                    return x.to_dict()
                else:
                    return x.to_dict(serialize)
            else:
                return x

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            attr = self.attribute_map.get(attr, attr) if serialize else attr
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: convert(x),
                    value
                ))
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], convert(item[1])),
                    value.items()
                ))
            else:
                result[attr] = convert(value)

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, UpsertReturnsResponse):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, UpsertReturnsResponse):
            return True

        return self.to_dict() != other.to_dict()
