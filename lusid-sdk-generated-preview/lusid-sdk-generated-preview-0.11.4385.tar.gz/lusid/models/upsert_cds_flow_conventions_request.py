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


class UpsertCdsFlowConventionsRequest(object):
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
        'cds_flow_conventions': 'CdsFlowConventions'
    }

    attribute_map = {
        'cds_flow_conventions': 'cdsFlowConventions'
    }

    required_map = {
        'cds_flow_conventions': 'optional'
    }

    def __init__(self, cds_flow_conventions=None, local_vars_configuration=None):  # noqa: E501
        """UpsertCdsFlowConventionsRequest - a model defined in OpenAPI"
        
        :param cds_flow_conventions: 
        :type cds_flow_conventions: lusid.CdsFlowConventions

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._cds_flow_conventions = None
        self.discriminator = None

        if cds_flow_conventions is not None:
            self.cds_flow_conventions = cds_flow_conventions

    @property
    def cds_flow_conventions(self):
        """Gets the cds_flow_conventions of this UpsertCdsFlowConventionsRequest.  # noqa: E501


        :return: The cds_flow_conventions of this UpsertCdsFlowConventionsRequest.  # noqa: E501
        :rtype: lusid.CdsFlowConventions
        """
        return self._cds_flow_conventions

    @cds_flow_conventions.setter
    def cds_flow_conventions(self, cds_flow_conventions):
        """Sets the cds_flow_conventions of this UpsertCdsFlowConventionsRequest.


        :param cds_flow_conventions: The cds_flow_conventions of this UpsertCdsFlowConventionsRequest.  # noqa: E501
        :type cds_flow_conventions: lusid.CdsFlowConventions
        """

        self._cds_flow_conventions = cds_flow_conventions

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
        if not isinstance(other, UpsertCdsFlowConventionsRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, UpsertCdsFlowConventionsRequest):
            return True

        return self.to_dict() != other.to_dict()
