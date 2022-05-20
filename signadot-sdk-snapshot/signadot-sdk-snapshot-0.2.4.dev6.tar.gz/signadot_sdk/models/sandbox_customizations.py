# coding: utf-8

"""
    Signadot API

    API for Signadot Sandboxes  # noqa: E501

    OpenAPI spec version: 1.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from signadot_sdk.configuration import Configuration


class SandboxCustomizations(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'env': 'list[EnvOp]',
        'images': 'list[Image]',
        'patch': 'CustomPatch'
    }

    attribute_map = {
        'env': 'env',
        'images': 'images',
        'patch': 'patch'
    }

    def __init__(self, env=None, images=None, patch=None, _configuration=None):  # noqa: E501
        """SandboxCustomizations - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._env = None
        self._images = None
        self._patch = None
        self.discriminator = None

        if env is not None:
            self.env = env
        if images is not None:
            self.images = images
        if patch is not None:
            self.patch = patch

    @property
    def env(self):
        """Gets the env of this SandboxCustomizations.  # noqa: E501

        Env var modifications that will be applied to the forked workload  # noqa: E501

        :return: The env of this SandboxCustomizations.  # noqa: E501
        :rtype: list[EnvOp]
        """
        return self._env

    @env.setter
    def env(self, env):
        """Sets the env of this SandboxCustomizations.

        Env var modifications that will be applied to the forked workload  # noqa: E501

        :param env: The env of this SandboxCustomizations.  # noqa: E501
        :type: list[EnvOp]
        """

        self._env = env

    @property
    def images(self):
        """Gets the images of this SandboxCustomizations.  # noqa: E501

        One or more docker images that will be applied to the forked workload  # noqa: E501

        :return: The images of this SandboxCustomizations.  # noqa: E501
        :rtype: list[Image]
        """
        return self._images

    @images.setter
    def images(self, images):
        """Sets the images of this SandboxCustomizations.

        One or more docker images that will be applied to the forked workload  # noqa: E501

        :param images: The images of this SandboxCustomizations.  # noqa: E501
        :type: list[Image]
        """

        self._images = images

    @property
    def patch(self):
        """Gets the patch of this SandboxCustomizations.  # noqa: E501


        :return: The patch of this SandboxCustomizations.  # noqa: E501
        :rtype: CustomPatch
        """
        return self._patch

    @patch.setter
    def patch(self, patch):
        """Sets the patch of this SandboxCustomizations.


        :param patch: The patch of this SandboxCustomizations.  # noqa: E501
        :type: CustomPatch
        """

        self._patch = patch

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
        if issubclass(SandboxCustomizations, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, SandboxCustomizations):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, SandboxCustomizations):
            return True

        return self.to_dict() != other.to_dict()
