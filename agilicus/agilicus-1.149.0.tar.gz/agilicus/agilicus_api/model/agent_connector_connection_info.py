"""
    Agilicus API

    Agilicus is API-first. Modern software is controlled by other software, is open, is available for you to use the way you want, securely, simply.  A rendered, online viewable and usable version of this specification is available at [api](https://www.agilicus.com/api). You may try the API inline directly in the web page. To do so, first obtain an Authentication Token (the simplest way is to install the Python SDK, and then run `agilicus-cli --issuer https://MYISSUER get-token`). You will need an org-id for most calls (and can obtain from `agilicus-cli --issuer https://MYISSUER list-orgs`). The `MYISSUER` will typically be `auth.MYDOMAIN`, and you will see it as you sign-in to the administrative UI.  This API releases on Bearer-Token authentication. To obtain a valid bearer token you will need to Authenticate to an Issuer with OpenID Connect (a superset of OAUTH2).  Your \"issuer\" will look like https://auth.MYDOMAIN. For example, when you signed-up, if you said \"use my own domain name\" and assigned a CNAME of cloud.example.com, then your issuer would be https://auth.cloud.example.com.  If you selected \"use an Agilicus supplied domain name\", your issuer would look like https://auth.myorg.agilicus.cloud.  For test purposes you can use our [Python SDK](https://pypi.org/project/agilicus/) and run `agilicus-cli --issuer https://auth.MYDOMAIN get-token`.  This API may be used in any language runtime that supports OpenAPI 3.0, or, you may use our [Python SDK](https://pypi.org/project/agilicus/), our [Typescript SDK](https://www.npmjs.com/package/@agilicus/angular), or our [Golang SDK](https://git.agilicus.com/pub/sdk-go).  100% of the activities in our system our API-driven, from our web-admin, through our progressive web applications, to all internals: there is nothing that is not accessible.  For more information, see [developer resources](https://www.agilicus.com/developer).   # noqa: E501

    The version of the OpenAPI document: 2022.05.18
    Contact: dev@agilicus.com
    Generated by: https://openapi-generator.tech
"""


import re  # noqa: F401
import sys  # noqa: F401

from agilicus_api.model_utils import (  # noqa: F401
    ApiTypeError,
    ModelComposed,
    ModelNormal,
    ModelSimple,
    cached_property,
    change_keys_js_to_python,
    convert_js_args_to_python_args,
    date,
    datetime,
    file_type,
    none_type,
    validate_get_composed_info,
)
from ..model_utils import OpenApiModel
from agilicus_api.exceptions import ApiAttributeError


def lazy_import():
    from agilicus_api.model.application_config import ApplicationConfig
    from agilicus_api.model.application_service import ApplicationService
    from agilicus_api.model.desktop_resource import DesktopResource
    from agilicus_api.model.file_share_service import FileShareService
    globals()['ApplicationConfig'] = ApplicationConfig
    globals()['ApplicationService'] = ApplicationService
    globals()['DesktopResource'] = DesktopResource
    globals()['FileShareService'] = FileShareService


class AgentConnectorConnectionInfo(ModelNormal):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.

    Attributes:
      allowed_values (dict): The key is the tuple path to the attribute
          and the for var_name this is (var_name,). The value is a dict
          with a capitalized key describing the allowed value and an allowed
          value. These dicts store the allowed enum values.
      attribute_map (dict): The key is attribute name
          and the value is json key in definition.
      discriminator_value_class_map (dict): A dict to go from the discriminator
          variable value to the discriminator class name.
      validations (dict): The key is the tuple path to the attribute
          and the for var_name this is (var_name,). The value is a dict
          that stores validations for max_length, min_length, max_items,
          min_items, exclusive_maximum, inclusive_maximum, exclusive_minimum,
          inclusive_minimum, and regex.
      additional_properties_type (tuple): A tuple of classes accepted
          as additional properties values.
    """

    allowed_values = {
    }

    validations = {
        ('connection_org_id',): {
            'max_length': 40,
        },
        ('connection_app_name',): {
            'max_length': 63,
            'min_length': 1,
            'regex': {
                'pattern': r'^[a-zA-Z0-9-:]+$',  # noqa: E501
            },
        },
        ('max_number_connections',): {
            'inclusive_maximum': 64,
            'inclusive_minimum': 0,
        },
        ('connection_env_name',): {
            'max_length': 40,
            'min_length': 1,
        },
    }

    @property
    def connection_uri(self):
       return self.get("connection_uri")

    @connection_uri.setter
    def connection_uri(self, new_value):
       self.connection_uri = new_value

    @property
    def connection_location(self):
       return self.get("connection_location")

    @connection_location.setter
    def connection_location(self, new_value):
       self.connection_location = new_value

    @property
    def connection_path(self):
       return self.get("connection_path")

    @connection_path.setter
    def connection_path(self, new_value):
       self.connection_path = new_value

    @property
    def connection_org_id(self):
       return self.get("connection_org_id")

    @connection_org_id.setter
    def connection_org_id(self, new_value):
       self.connection_org_id = new_value

    @property
    def connection_app_name(self):
       return self.get("connection_app_name")

    @connection_app_name.setter
    def connection_app_name(self, new_value):
       self.connection_app_name = new_value

    @property
    def is_an_auth_service(self):
       return self.get("is_an_auth_service")

    @is_an_auth_service.setter
    def is_an_auth_service(self, new_value):
       self.is_an_auth_service = new_value

    @property
    def end_to_end_tls(self):
       return self.get("end_to_end_tls")

    @end_to_end_tls.setter
    def end_to_end_tls(self, new_value):
       self.end_to_end_tls = new_value

    @property
    def max_number_connections(self):
       return self.get("max_number_connections")

    @max_number_connections.setter
    def max_number_connections(self, new_value):
       self.max_number_connections = new_value

    @property
    def ip_services(self):
       return self.get("ip_services")

    @ip_services.setter
    def ip_services(self, new_value):
       self.ip_services = new_value

    @property
    def file_share_services(self):
       return self.get("file_share_services")

    @file_share_services.setter
    def file_share_services(self, new_value):
       self.file_share_services = new_value

    @property
    def desktop_services(self):
       return self.get("desktop_services")

    @desktop_services.setter
    def desktop_services(self, new_value):
       self.desktop_services = new_value

    @property
    def application_config(self):
       return self.get("application_config")

    @application_config.setter
    def application_config(self, new_value):
       self.application_config = new_value

    @property
    def application_scopes(self):
       return self.get("application_scopes")

    @application_scopes.setter
    def application_scopes(self, new_value):
       self.application_scopes = new_value

    @property
    def connection_app_id(self):
       return self.get("connection_app_id")

    @connection_app_id.setter
    def connection_app_id(self, new_value):
       self.connection_app_id = new_value

    @property
    def connection_env_name(self):
       return self.get("connection_env_name")

    @connection_env_name.setter
    def connection_env_name(self, new_value):
       self.connection_env_name = new_value

    @cached_property
    def additional_properties_type():
        """
        This must be a method because a model may have properties that are
        of type self, this must run after the class is loaded
        """
        lazy_import()
        return (bool, date, datetime, dict, float, int, list, str, none_type,)  # noqa: E501

    _nullable = False

    @cached_property
    def openapi_types():
        """
        This must be a method because a model may have properties that are
        of type self, this must run after the class is loaded

        Returns
            openapi_types (dict): The key is attribute name
                and the value is attribute type.
        """
        lazy_import()
        return {
            'connection_uri': (str,),  # noqa: E501
            'connection_location': (str,),  # noqa: E501
            'connection_path': (str,),  # noqa: E501
            'connection_org_id': (str,),  # noqa: E501
            'connection_app_name': (str,),  # noqa: E501
            'is_an_auth_service': (bool,),  # noqa: E501
            'end_to_end_tls': (bool,),  # noqa: E501
            'max_number_connections': (int,),  # noqa: E501
            'ip_services': ([ApplicationService],),  # noqa: E501
            'file_share_services': ([FileShareService],),  # noqa: E501
            'desktop_services': ([DesktopResource],),  # noqa: E501
            'application_config': (ApplicationConfig,),  # noqa: E501
            'application_scopes': ([str],),  # noqa: E501
            'connection_app_id': (str,),  # noqa: E501
            'connection_env_name': (str,),  # noqa: E501
        }

    @cached_property
    def discriminator():
        return None



    attribute_map = {
        'connection_uri': 'connection_uri',  # noqa: E501
        'connection_location': 'connection_location',  # noqa: E501
        'connection_path': 'connection_path',  # noqa: E501
        'connection_org_id': 'connection_org_id',  # noqa: E501
        'connection_app_name': 'connection_app_name',  # noqa: E501
        'is_an_auth_service': 'is_an_auth_service',  # noqa: E501
        'end_to_end_tls': 'end_to_end_tls',  # noqa: E501
        'max_number_connections': 'max_number_connections',  # noqa: E501
        'ip_services': 'ip_services',  # noqa: E501
        'file_share_services': 'file_share_services',  # noqa: E501
        'desktop_services': 'desktop_services',  # noqa: E501
        'application_config': 'application_config',  # noqa: E501
        'application_scopes': 'application_scopes',  # noqa: E501
        'connection_app_id': 'connection_app_id',  # noqa: E501
        'connection_env_name': 'connection_env_name',  # noqa: E501
    }

    read_only_vars = {
        'application_scopes',  # noqa: E501
    }

    _composed_schemas = {}

    @classmethod
    @convert_js_args_to_python_args
    def _from_openapi_data(cls, *args, **kwargs):  # noqa: E501
        """AgentConnectorConnectionInfo - a model defined in OpenAPI

        Keyword Args:
            _check_type (bool): if True, values for parameters in openapi_types
                                will be type checked and a TypeError will be
                                raised if the wrong type is input.
                                Defaults to True
            _path_to_item (tuple/list): This is a list of keys or values to
                                drill down to the model in received_data
                                when deserializing a response
            _spec_property_naming (bool): True if the variable names in the input data
                                are serialized names, as specified in the OpenAPI document.
                                False if the variable names in the input data
                                are pythonic names, e.g. snake case (default)
            _configuration (Configuration): the instance to use when
                                deserializing a file_type parameter.
                                If passed, type conversion is attempted
                                If omitted no type conversion is done.
            _visited_composed_classes (tuple): This stores a tuple of
                                classes that we have traveled through so that
                                if we see that class again we will not use its
                                discriminator again.
                                When traveling through a discriminator, the
                                composed schema that is
                                is traveled through is added to this set.
                                For example if Animal has a discriminator
                                petType and we pass in "Dog", and the class Dog
                                allOf includes Animal, we move through Animal
                                once using the discriminator, and pick Dog.
                                Then in Dog, we will make an instance of the
                                Animal class but this time we won't travel
                                through its discriminator because we passed in
                                _visited_composed_classes = (Animal,)
            connection_uri (str): The URI used to establish a connection to the connector.. [optional]  # noqa: E501
            connection_location (str): The location (e.g. fully qualified domain name) of the connection. While this matches the location in the `connection_uri`, it is provided separately for convenience. . [optional]  # noqa: E501
            connection_path (str): The path of the connection. While this matches the path in the `connection_uri`, it is provided separately for convenience. . [optional]  # noqa: E501
            connection_org_id (str): The identifier for the organisation hosting the server side of this connection. . [optional]  # noqa: E501
            connection_app_name (str): The name of the Application (if any) hosting the server side of this connection. Note that not all servers will be hosted by an Application, in which case this will be empty. . [optional]  # noqa: E501
            is_an_auth_service (bool): Indicates that the connection is exposing an authentication service . [optional] if omitted the server will use the default value of False  # noqa: E501
            end_to_end_tls (bool): Controls if the connection is end to end TLS. . [optional]  # noqa: E501
            max_number_connections (int): The maximum number of connections to maintain to the cluster when stable. Note that this value may be exceeded during times of reconfiguration. A value of zero means that the connection is effectively unused by this Secure Agent. . [optional] if omitted the server will use the default value of 16  # noqa: E501
            ip_services ([ApplicationService]): The list of ip services associated with this connection. [optional]  # noqa: E501
            file_share_services ([FileShareService]): The list of fileshare services associated with this connection. [optional]  # noqa: E501
            desktop_services ([DesktopResource]): The list of (vnc) Desktop services. [optional]  # noqa: E501
            application_config (ApplicationConfig): [optional]  # noqa: E501
            application_scopes ([str]): A list of scopes to be requested on behalf of the user of the application and as well as configured based on the application launchers that launch this application/environment. This field is only populated on a GET request when the query parameter get_scopes=True is passed. . [optional]  # noqa: E501
            connection_app_id (str): Unique identifier. [optional]  # noqa: E501
            connection_env_name (str): The name of the Environment utilized for this application instance. . [optional]  # noqa: E501
        """

        _check_type = kwargs.pop('_check_type', True)
        _spec_property_naming = kwargs.pop('_spec_property_naming', False)
        _path_to_item = kwargs.pop('_path_to_item', ())
        _configuration = kwargs.pop('_configuration', None)
        _visited_composed_classes = kwargs.pop('_visited_composed_classes', ())

        self = super(OpenApiModel, cls).__new__(cls)

        if args:
            raise ApiTypeError(
                "Invalid positional arguments=%s passed to %s. Remove those invalid positional arguments." % (
                    args,
                    self.__class__.__name__,
                ),
                path_to_item=_path_to_item,
                valid_classes=(self.__class__,),
            )

        self._data_store = {}
        self._check_type = _check_type
        self._spec_property_naming = _spec_property_naming
        self._path_to_item = _path_to_item
        self._configuration = _configuration
        self._visited_composed_classes = _visited_composed_classes + (self.__class__,)

        for var_name, var_value in kwargs.items():
            if var_name not in self.attribute_map and \
                        self._configuration is not None and \
                        self._configuration.discard_unknown_keys and \
                        self.additional_properties_type is None:
                # discard variable.
                continue
            setattr(self, var_name, var_value)
        return self

    def __python_set(val):
        return set(val)
 
    required_properties = __python_set([
        '_data_store',
        '_check_type',
        '_spec_property_naming',
        '_path_to_item',
        '_configuration',
        '_visited_composed_classes',
    ])

    @convert_js_args_to_python_args
    def __init__(self, *args, **kwargs):  # noqa: E501
        """AgentConnectorConnectionInfo - a model defined in OpenAPI

        Keyword Args:
            _check_type (bool): if True, values for parameters in openapi_types
                                will be type checked and a TypeError will be
                                raised if the wrong type is input.
                                Defaults to True
            _path_to_item (tuple/list): This is a list of keys or values to
                                drill down to the model in received_data
                                when deserializing a response
            _spec_property_naming (bool): True if the variable names in the input data
                                are serialized names, as specified in the OpenAPI document.
                                False if the variable names in the input data
                                are pythonic names, e.g. snake case (default)
            _configuration (Configuration): the instance to use when
                                deserializing a file_type parameter.
                                If passed, type conversion is attempted
                                If omitted no type conversion is done.
            _visited_composed_classes (tuple): This stores a tuple of
                                classes that we have traveled through so that
                                if we see that class again we will not use its
                                discriminator again.
                                When traveling through a discriminator, the
                                composed schema that is
                                is traveled through is added to this set.
                                For example if Animal has a discriminator
                                petType and we pass in "Dog", and the class Dog
                                allOf includes Animal, we move through Animal
                                once using the discriminator, and pick Dog.
                                Then in Dog, we will make an instance of the
                                Animal class but this time we won't travel
                                through its discriminator because we passed in
                                _visited_composed_classes = (Animal,)
            connection_uri (str): The URI used to establish a connection to the connector.. [optional]  # noqa: E501
            connection_location (str): The location (e.g. fully qualified domain name) of the connection. While this matches the location in the `connection_uri`, it is provided separately for convenience. . [optional]  # noqa: E501
            connection_path (str): The path of the connection. While this matches the path in the `connection_uri`, it is provided separately for convenience. . [optional]  # noqa: E501
            connection_org_id (str): The identifier for the organisation hosting the server side of this connection. . [optional]  # noqa: E501
            connection_app_name (str): The name of the Application (if any) hosting the server side of this connection. Note that not all servers will be hosted by an Application, in which case this will be empty. . [optional]  # noqa: E501
            is_an_auth_service (bool): Indicates that the connection is exposing an authentication service . [optional] if omitted the server will use the default value of False  # noqa: E501
            end_to_end_tls (bool): Controls if the connection is end to end TLS. . [optional]  # noqa: E501
            max_number_connections (int): The maximum number of connections to maintain to the cluster when stable. Note that this value may be exceeded during times of reconfiguration. A value of zero means that the connection is effectively unused by this Secure Agent. . [optional] if omitted the server will use the default value of 16  # noqa: E501
            ip_services ([ApplicationService]): The list of ip services associated with this connection. [optional]  # noqa: E501
            file_share_services ([FileShareService]): The list of fileshare services associated with this connection. [optional]  # noqa: E501
            desktop_services ([DesktopResource]): The list of (vnc) Desktop services. [optional]  # noqa: E501
            application_config (ApplicationConfig): [optional]  # noqa: E501
            application_scopes ([str]): A list of scopes to be requested on behalf of the user of the application and as well as configured based on the application launchers that launch this application/environment. This field is only populated on a GET request when the query parameter get_scopes=True is passed. . [optional]  # noqa: E501
            connection_app_id (str): Unique identifier. [optional]  # noqa: E501
            connection_env_name (str): The name of the Environment utilized for this application instance. . [optional]  # noqa: E501
        """

        _check_type = kwargs.pop('_check_type', True)
        _spec_property_naming = kwargs.pop('_spec_property_naming', False)
        _path_to_item = kwargs.pop('_path_to_item', ())
        _configuration = kwargs.pop('_configuration', None)
        _visited_composed_classes = kwargs.pop('_visited_composed_classes', ())

        if args:
            raise ApiTypeError(
                "Invalid positional arguments=%s passed to %s. Remove those invalid positional arguments." % (
                    args,
                    self.__class__.__name__,
                ),
                path_to_item=_path_to_item,
                valid_classes=(self.__class__,),
            )

        self._data_store = {}
        self._check_type = _check_type
        self._spec_property_naming = _spec_property_naming
        self._path_to_item = _path_to_item
        self._configuration = _configuration
        self._visited_composed_classes = _visited_composed_classes + (self.__class__,)

        for var_name, var_value in kwargs.items():
            if var_name not in self.attribute_map and \
                        self._configuration is not None and \
                        self._configuration.discard_unknown_keys and \
                        self.additional_properties_type is None:
                # discard variable.
                continue
            setattr(self, var_name, var_value)
            if var_name in self.read_only_vars:
                raise ApiAttributeError(f"`{var_name}` is a read-only attribute. Use `from_openapi_data` to instantiate "
                                     f"class with read only attributes.")

