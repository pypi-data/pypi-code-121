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

from signadot_sdk_snapshot.configuration import Configuration


class SandboxInfo(object):
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
        'cluster_name': 'str',
        'created_at': 'str',
        'default_service': 'str',
        'default_service_port': 'int',
        'description': 'str',
        'id': 'str',
        'name': 'str',
        'namespace': 'str',
        'preview_endpoints': 'list[PreviewEndpoint]',
        'preview_url': 'str',
        'updated_at': 'str'
    }

    attribute_map = {
        'cluster_name': 'clusterName',
        'created_at': 'createdAt',
        'default_service': 'defaultService',
        'default_service_port': 'defaultServicePort',
        'description': 'description',
        'id': 'id',
        'name': 'name',
        'namespace': 'namespace',
        'preview_endpoints': 'previewEndpoints',
        'preview_url': 'previewURL',
        'updated_at': 'updatedAt'
    }

    def __init__(self, cluster_name=None, created_at=None, default_service=None, default_service_port=None, description=None, id=None, name=None, namespace=None, preview_endpoints=None, preview_url=None, updated_at=None, _configuration=None):  # noqa: E501
        """SandboxInfo - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._cluster_name = None
        self._created_at = None
        self._default_service = None
        self._default_service_port = None
        self._description = None
        self._id = None
        self._name = None
        self._namespace = None
        self._preview_endpoints = None
        self._preview_url = None
        self._updated_at = None
        self.discriminator = None

        if cluster_name is not None:
            self.cluster_name = cluster_name
        if created_at is not None:
            self.created_at = created_at
        if default_service is not None:
            self.default_service = default_service
        if default_service_port is not None:
            self.default_service_port = default_service_port
        if description is not None:
            self.description = description
        if id is not None:
            self.id = id
        if name is not None:
            self.name = name
        if namespace is not None:
            self.namespace = namespace
        if preview_endpoints is not None:
            self.preview_endpoints = preview_endpoints
        if preview_url is not None:
            self.preview_url = preview_url
        if updated_at is not None:
            self.updated_at = updated_at

    @property
    def cluster_name(self):
        """Gets the cluster_name of this SandboxInfo.  # noqa: E501


        :return: The cluster_name of this SandboxInfo.  # noqa: E501
        :rtype: str
        """
        return self._cluster_name

    @cluster_name.setter
    def cluster_name(self, cluster_name):
        """Sets the cluster_name of this SandboxInfo.


        :param cluster_name: The cluster_name of this SandboxInfo.  # noqa: E501
        :type: str
        """

        self._cluster_name = cluster_name

    @property
    def created_at(self):
        """Gets the created_at of this SandboxInfo.  # noqa: E501


        :return: The created_at of this SandboxInfo.  # noqa: E501
        :rtype: str
        """
        return self._created_at

    @created_at.setter
    def created_at(self, created_at):
        """Sets the created_at of this SandboxInfo.


        :param created_at: The created_at of this SandboxInfo.  # noqa: E501
        :type: str
        """

        self._created_at = created_at

    @property
    def default_service(self):
        """Gets the default_service of this SandboxInfo.  # noqa: E501


        :return: The default_service of this SandboxInfo.  # noqa: E501
        :rtype: str
        """
        return self._default_service

    @default_service.setter
    def default_service(self, default_service):
        """Sets the default_service of this SandboxInfo.


        :param default_service: The default_service of this SandboxInfo.  # noqa: E501
        :type: str
        """

        self._default_service = default_service

    @property
    def default_service_port(self):
        """Gets the default_service_port of this SandboxInfo.  # noqa: E501


        :return: The default_service_port of this SandboxInfo.  # noqa: E501
        :rtype: int
        """
        return self._default_service_port

    @default_service_port.setter
    def default_service_port(self, default_service_port):
        """Sets the default_service_port of this SandboxInfo.


        :param default_service_port: The default_service_port of this SandboxInfo.  # noqa: E501
        :type: int
        """

        self._default_service_port = default_service_port

    @property
    def description(self):
        """Gets the description of this SandboxInfo.  # noqa: E501


        :return: The description of this SandboxInfo.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this SandboxInfo.


        :param description: The description of this SandboxInfo.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def id(self):
        """Gets the id of this SandboxInfo.  # noqa: E501


        :return: The id of this SandboxInfo.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this SandboxInfo.


        :param id: The id of this SandboxInfo.  # noqa: E501
        :type: str
        """

        self._id = id

    @property
    def name(self):
        """Gets the name of this SandboxInfo.  # noqa: E501


        :return: The name of this SandboxInfo.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this SandboxInfo.


        :param name: The name of this SandboxInfo.  # noqa: E501
        :type: str
        """

        self._name = name

    @property
    def namespace(self):
        """Gets the namespace of this SandboxInfo.  # noqa: E501


        :return: The namespace of this SandboxInfo.  # noqa: E501
        :rtype: str
        """
        return self._namespace

    @namespace.setter
    def namespace(self, namespace):
        """Sets the namespace of this SandboxInfo.


        :param namespace: The namespace of this SandboxInfo.  # noqa: E501
        :type: str
        """

        self._namespace = namespace

    @property
    def preview_endpoints(self):
        """Gets the preview_endpoints of this SandboxInfo.  # noqa: E501


        :return: The preview_endpoints of this SandboxInfo.  # noqa: E501
        :rtype: list[PreviewEndpoint]
        """
        return self._preview_endpoints

    @preview_endpoints.setter
    def preview_endpoints(self, preview_endpoints):
        """Sets the preview_endpoints of this SandboxInfo.


        :param preview_endpoints: The preview_endpoints of this SandboxInfo.  # noqa: E501
        :type: list[PreviewEndpoint]
        """

        self._preview_endpoints = preview_endpoints

    @property
    def preview_url(self):
        """Gets the preview_url of this SandboxInfo.  # noqa: E501


        :return: The preview_url of this SandboxInfo.  # noqa: E501
        :rtype: str
        """
        return self._preview_url

    @preview_url.setter
    def preview_url(self, preview_url):
        """Sets the preview_url of this SandboxInfo.


        :param preview_url: The preview_url of this SandboxInfo.  # noqa: E501
        :type: str
        """

        self._preview_url = preview_url

    @property
    def updated_at(self):
        """Gets the updated_at of this SandboxInfo.  # noqa: E501


        :return: The updated_at of this SandboxInfo.  # noqa: E501
        :rtype: str
        """
        return self._updated_at

    @updated_at.setter
    def updated_at(self, updated_at):
        """Sets the updated_at of this SandboxInfo.


        :param updated_at: The updated_at of this SandboxInfo.  # noqa: E501
        :type: str
        """

        self._updated_at = updated_at

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
        if issubclass(SandboxInfo, dict):
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
        if not isinstance(other, SandboxInfo):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, SandboxInfo):
            return True

        return self.to_dict() != other.to_dict()
