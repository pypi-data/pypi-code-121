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
    from agilicus_api.model.application_service_assignment import ApplicationServiceAssignment
    from agilicus_api.model.application_service_stats import ApplicationServiceStats
    from agilicus_api.model.application_service_status import ApplicationServiceStatus
    from agilicus_api.model.network_service_config import NetworkServiceConfig
    globals()['ApplicationServiceAssignment'] = ApplicationServiceAssignment
    globals()['ApplicationServiceStats'] = ApplicationServiceStats
    globals()['ApplicationServiceStatus'] = ApplicationServiceStatus
    globals()['NetworkServiceConfig'] = NetworkServiceConfig


class ApplicationService(ModelNormal):
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
        ('name_resolution',): {
            'STATIC': "static",
            'DNS': "dns",
        },
        ('protocol',): {
            'TCP': "tcp",
        },
        ('service_type',): {
            'VPN': "vpn",
            'INTERNET': "internet",
            'AGENT': "agent",
            'IPSEC': "ipsec",
        },
        ('service_protocol_type',): {
            'IP': "ip",
            'FILESHARE': "fileshare",
            'DESKTOP': "desktop",
        },
    }

    validations = {
        ('name',): {
            'regex': {
                'pattern': r'^[a-zA-Z0-9-_.:]+$',  # noqa: E501
            },
        },
        ('connection_uri',): {
            'max_length': 1024,
        },
    }

    @property
    def created(self):
       return self.get("created")

    @created.setter
    def created(self, new_value):
       self.created = new_value

    @property
    def id(self):
       return self.get("id")

    @id.setter
    def id(self, new_value):
       self.id = new_value

    @property
    def name(self):
       return self.get("name")

    @name.setter
    def name(self, new_value):
       self.name = new_value

    @property
    def org_id(self):
       return self.get("org_id")

    @org_id.setter
    def org_id(self, new_value):
       self.org_id = new_value

    @property
    def hostname(self):
       return self.get("hostname")

    @hostname.setter
    def hostname(self, new_value):
       self.hostname = new_value

    @property
    def ipv4_addresses(self):
       return self.get("ipv4_addresses")

    @ipv4_addresses.setter
    def ipv4_addresses(self, new_value):
       self.ipv4_addresses = new_value

    @property
    def name_resolution(self):
       return self.get("name_resolution")

    @name_resolution.setter
    def name_resolution(self, new_value):
       self.name_resolution = new_value

    @property
    def config(self):
       return self.get("config")

    @config.setter
    def config(self, new_value):
       self.config = new_value

    @property
    def port(self):
       return self.get("port")

    @port.setter
    def port(self, new_value):
       self.port = new_value

    @property
    def protocol(self):
       return self.get("protocol")

    @protocol.setter
    def protocol(self, new_value):
       self.protocol = new_value

    @property
    def assignments(self):
       return self.get("assignments")

    @assignments.setter
    def assignments(self, new_value):
       self.assignments = new_value

    @property
    def updated(self):
       return self.get("updated")

    @updated.setter
    def updated(self, new_value):
       self.updated = new_value

    @property
    def service_type(self):
       return self.get("service_type")

    @service_type.setter
    def service_type(self, new_value):
       self.service_type = new_value

    @property
    def service_protocol_type(self):
       return self.get("service_protocol_type")

    @service_protocol_type.setter
    def service_protocol_type(self, new_value):
       self.service_protocol_type = new_value

    @property
    def tls_enabled(self):
       return self.get("tls_enabled")

    @tls_enabled.setter
    def tls_enabled(self, new_value):
       self.tls_enabled = new_value

    @property
    def tls_verify(self):
       return self.get("tls_verify")

    @tls_verify.setter
    def tls_verify(self, new_value):
       self.tls_verify = new_value

    @property
    def connector_id(self):
       return self.get("connector_id")

    @connector_id.setter
    def connector_id(self, new_value):
       self.connector_id = new_value

    @property
    def connection_uri(self):
       return self.get("connection_uri")

    @connection_uri.setter
    def connection_uri(self, new_value):
       self.connection_uri = new_value

    @property
    def connection_host_aliases(self):
       return self.get("connection_host_aliases")

    @connection_host_aliases.setter
    def connection_host_aliases(self, new_value):
       self.connection_host_aliases = new_value

    @property
    def stats(self):
       return self.get("stats")

    @stats.setter
    def stats(self, new_value):
       self.stats = new_value

    @property
    def status(self):
       return self.get("status")

    @status.setter
    def status(self, new_value):
       self.status = new_value

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
            'name': (str,),  # noqa: E501
            'org_id': (str,),  # noqa: E501
            'created': (datetime,),  # noqa: E501
            'id': (str,),  # noqa: E501
            'hostname': (str,),  # noqa: E501
            'ipv4_addresses': ([str],),  # noqa: E501
            'name_resolution': (str,),  # noqa: E501
            'config': (NetworkServiceConfig,),  # noqa: E501
            'port': (int,),  # noqa: E501
            'protocol': (str,),  # noqa: E501
            'assignments': ([ApplicationServiceAssignment],),  # noqa: E501
            'updated': (datetime,),  # noqa: E501
            'service_type': (str,),  # noqa: E501
            'service_protocol_type': (str,),  # noqa: E501
            'tls_enabled': (bool,),  # noqa: E501
            'tls_verify': (bool,),  # noqa: E501
            'connector_id': (str,),  # noqa: E501
            'connection_uri': (str,),  # noqa: E501
            'connection_host_aliases': ([str],),  # noqa: E501
            'stats': (ApplicationServiceStats,),  # noqa: E501
            'status': (ApplicationServiceStatus,),  # noqa: E501
        }

    @cached_property
    def discriminator():
        return None



    attribute_map = {
        'name': 'name',  # noqa: E501
        'org_id': 'org_id',  # noqa: E501
        'created': 'created',  # noqa: E501
        'id': 'id',  # noqa: E501
        'hostname': 'hostname',  # noqa: E501
        'ipv4_addresses': 'ipv4_addresses',  # noqa: E501
        'name_resolution': 'name_resolution',  # noqa: E501
        'config': 'config',  # noqa: E501
        'port': 'port',  # noqa: E501
        'protocol': 'protocol',  # noqa: E501
        'assignments': 'assignments',  # noqa: E501
        'updated': 'updated',  # noqa: E501
        'service_type': 'service_type',  # noqa: E501
        'service_protocol_type': 'service_protocol_type',  # noqa: E501
        'tls_enabled': 'tls_enabled',  # noqa: E501
        'tls_verify': 'tls_verify',  # noqa: E501
        'connector_id': 'connector_id',  # noqa: E501
        'connection_uri': 'connection_uri',  # noqa: E501
        'connection_host_aliases': 'connection_host_aliases',  # noqa: E501
        'stats': 'stats',  # noqa: E501
        'status': 'status',  # noqa: E501
    }

    read_only_vars = {
        'created',  # noqa: E501
        'id',  # noqa: E501
        'updated',  # noqa: E501
        'service_protocol_type',  # noqa: E501
        'connection_uri',  # noqa: E501
        'connection_host_aliases',  # noqa: E501
    }

    _composed_schemas = {}

    @classmethod
    @convert_js_args_to_python_args
    def _from_openapi_data(cls, name, org_id, *args, **kwargs):  # noqa: E501
        """ApplicationService - a model defined in OpenAPI

        Args:
            name (str): The name of the service. Services will be selected and assigned using this. This value must be unique within an organisation. 
            org_id (str): The organisation which owns this service.

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
            created (datetime): Creation time. [optional]  # noqa: E501
            id (str): Unique identifier. [optional]  # noqa: E501
            hostname (str): The hostname of the service. Your applications will refer to this service using its hostname. This can also be the IP Address of the service. If the address is an IPv4 Address it will add the IP to the ipv4_addresses field and set the name_resolution to static . [optional]  # noqa: E501
            ipv4_addresses ([str]): The IPv4 addresses of `hostname` within the data center.. [optional]  # noqa: E501
            name_resolution (str): How to resolve the hostname of the service. If static, then ipv4_address will be used. Otherwise, if dns the Organisation's dns services will be queried. . [optional] if omitted the server will use the default value of "static"  # noqa: E501
            config (NetworkServiceConfig): [optional]  # noqa: E501
            port (int): The transport-layer port on which to access the service. exclusiveMinimum: 0 exclusiveMaximum: 65536 . [optional]  # noqa: E501
            protocol (str): The transport-layer protocol over which to communicate with the service. . [optional] if omitted the server will use the default value of "tcp"  # noqa: E501
            assignments ([ApplicationServiceAssignment]): The Application Environments which have access to this ApplicationService. Manipulate this list to add or remove access to the ApplicationService. . [optional]  # noqa: E501
            updated (datetime): Update time. [optional]  # noqa: E501
            service_type (str): The type of application service. This refers to how the application connects to the service. [optional]  # noqa: E501
            service_protocol_type (str): The protocol carried by this service. This indicates to the Agilicus infrastructure how to interpret the data being transmitted to the service. Different protocols have different subclasses of an ApplicationService used to configure that protocol's details. This field may take on the following values:   - ip: Any upper layer protocols are transparent to the Agilicus infrastructure.     Agilicus does not participate in the protocol.   - fileshare: The service is a fileshare. Agilicus will participate in the file sharing     protocol in order to expose the fileshare to the Internet.   - desktop: The service is a desktop. Agilicus provides a Desktop Gateway allowing users to access     their Desktop without them being directly exposed to the internet. Users connect to this service     through the Desktop Gateway, using a protocol such as the Remote Desktop Protocol. . [optional]  # noqa: E501
            tls_enabled (bool): Whether Transport Layer Security (TLS) is enabled for this ip service running over tcp. This field has no meaning for non-ip services, or services using a transport protocol other than tcp. . [optional]  # noqa: E501
            tls_verify (bool): Whether the certificate presented by the Service is verified by the infrastructure. This can be useful when interacting with a test server which may not have a production certificate signed by a public certificate authority. . [optional]  # noqa: E501
            connector_id (str): Unique identifier. [optional]  # noqa: E501
            connection_uri (str): The URI by which this service can be directly accessed. Depending on the type of connector associated with this service, the URI could be public or internal to the Agilicus infrastructure. In both cases, valid credentials proving permission to access this service are necessary to access the service. If this field is empty, then it cannot be accessed directly.. . [optional]  # noqa: E501
            connection_host_aliases ([str]): A list of hosts for which the assigned connector will also forward requests for this application service. . [optional]  # noqa: E501
            stats (ApplicationServiceStats): [optional]  # noqa: E501
            status (ApplicationServiceStatus): [optional]  # noqa: E501
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

        self.name = name
        self.org_id = org_id
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
    def __init__(self, name, org_id, *args, **kwargs):  # noqa: E501
        """ApplicationService - a model defined in OpenAPI

        Args:
            name (str): The name of the service. Services will be selected and assigned using this. This value must be unique within an organisation. 
            org_id (str): The organisation which owns this service.

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
            created (datetime): Creation time. [optional]  # noqa: E501
            id (str): Unique identifier. [optional]  # noqa: E501
            hostname (str): The hostname of the service. Your applications will refer to this service using its hostname. This can also be the IP Address of the service. If the address is an IPv4 Address it will add the IP to the ipv4_addresses field and set the name_resolution to static . [optional]  # noqa: E501
            ipv4_addresses ([str]): The IPv4 addresses of `hostname` within the data center.. [optional]  # noqa: E501
            name_resolution (str): How to resolve the hostname of the service. If static, then ipv4_address will be used. Otherwise, if dns the Organisation's dns services will be queried. . [optional] if omitted the server will use the default value of "static"  # noqa: E501
            config (NetworkServiceConfig): [optional]  # noqa: E501
            port (int): The transport-layer port on which to access the service. exclusiveMinimum: 0 exclusiveMaximum: 65536 . [optional]  # noqa: E501
            protocol (str): The transport-layer protocol over which to communicate with the service. . [optional] if omitted the server will use the default value of "tcp"  # noqa: E501
            assignments ([ApplicationServiceAssignment]): The Application Environments which have access to this ApplicationService. Manipulate this list to add or remove access to the ApplicationService. . [optional]  # noqa: E501
            updated (datetime): Update time. [optional]  # noqa: E501
            service_type (str): The type of application service. This refers to how the application connects to the service. [optional]  # noqa: E501
            service_protocol_type (str): The protocol carried by this service. This indicates to the Agilicus infrastructure how to interpret the data being transmitted to the service. Different protocols have different subclasses of an ApplicationService used to configure that protocol's details. This field may take on the following values:   - ip: Any upper layer protocols are transparent to the Agilicus infrastructure.     Agilicus does not participate in the protocol.   - fileshare: The service is a fileshare. Agilicus will participate in the file sharing     protocol in order to expose the fileshare to the Internet.   - desktop: The service is a desktop. Agilicus provides a Desktop Gateway allowing users to access     their Desktop without them being directly exposed to the internet. Users connect to this service     through the Desktop Gateway, using a protocol such as the Remote Desktop Protocol. . [optional]  # noqa: E501
            tls_enabled (bool): Whether Transport Layer Security (TLS) is enabled for this ip service running over tcp. This field has no meaning for non-ip services, or services using a transport protocol other than tcp. . [optional]  # noqa: E501
            tls_verify (bool): Whether the certificate presented by the Service is verified by the infrastructure. This can be useful when interacting with a test server which may not have a production certificate signed by a public certificate authority. . [optional]  # noqa: E501
            connector_id (str): Unique identifier. [optional]  # noqa: E501
            connection_uri (str): The URI by which this service can be directly accessed. Depending on the type of connector associated with this service, the URI could be public or internal to the Agilicus infrastructure. In both cases, valid credentials proving permission to access this service are necessary to access the service. If this field is empty, then it cannot be accessed directly.. . [optional]  # noqa: E501
            connection_host_aliases ([str]): A list of hosts for which the assigned connector will also forward requests for this application service. . [optional]  # noqa: E501
            stats (ApplicationServiceStats): [optional]  # noqa: E501
            status (ApplicationServiceStatus): [optional]  # noqa: E501
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

        self.name = name
        self.org_id = org_id
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

