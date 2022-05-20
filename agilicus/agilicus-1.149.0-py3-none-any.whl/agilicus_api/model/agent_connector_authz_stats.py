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



class AgentConnectorAuthzStats(ModelNormal):
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
        ('allowed',): {
            'inclusive_minimum': 0,
        },
        ('allowed_app_handled',): {
            'inclusive_minimum': 0,
        },
        ('denied',): {
            'inclusive_minimum': 0,
        },
        ('token_cached_failed',): {
            'inclusive_minimum': 0,
        },
        ('token_cached_success',): {
            'inclusive_minimum': 0,
        },
        ('token_parse_failed',): {
            'inclusive_minimum': 0,
        },
        ('token_static_token',): {
            'inclusive_minimum': 0,
        },
        ('token_bad_jti',): {
            'inclusive_minimum': 0,
        },
        ('token_lookup_success',): {
            'inclusive_minimum': 0,
        },
        ('token_lookup_notfound',): {
            'inclusive_minimum': 0,
        },
        ('token_lookup_badrequest',): {
            'inclusive_minimum': 0,
        },
        ('token_lookup_4xx_other',): {
            'inclusive_minimum': 0,
        },
        ('token_lookup_error',): {
            'inclusive_minimum': 0,
        },
        ('token_lookup_revoked',): {
            'inclusive_minimum': 0,
        },
        ('token_basic_auth_decode_fail',): {
            'inclusive_minimum': 0,
        },
        ('token_basic_auth_too_long',): {
            'inclusive_minimum': 0,
        },
        ('token_basic_auth_no_password',): {
            'inclusive_minimum': 0,
        },
        ('token_basic_auth_cached_success',): {
            'inclusive_minimum': 0,
        },
        ('token_basic_auth_cached_failed',): {
            'inclusive_minimum': 0,
        },
    }

    @property
    def allowed(self):
       return self.get("allowed")

    @allowed.setter
    def allowed(self, new_value):
       self.allowed = new_value

    @property
    def allowed_app_handled(self):
       return self.get("allowed_app_handled")

    @allowed_app_handled.setter
    def allowed_app_handled(self, new_value):
       self.allowed_app_handled = new_value

    @property
    def denied(self):
       return self.get("denied")

    @denied.setter
    def denied(self, new_value):
       self.denied = new_value

    @property
    def token_cached_failed(self):
       return self.get("token_cached_failed")

    @token_cached_failed.setter
    def token_cached_failed(self, new_value):
       self.token_cached_failed = new_value

    @property
    def token_cached_success(self):
       return self.get("token_cached_success")

    @token_cached_success.setter
    def token_cached_success(self, new_value):
       self.token_cached_success = new_value

    @property
    def token_parse_failed(self):
       return self.get("token_parse_failed")

    @token_parse_failed.setter
    def token_parse_failed(self, new_value):
       self.token_parse_failed = new_value

    @property
    def token_static_token(self):
       return self.get("token_static_token")

    @token_static_token.setter
    def token_static_token(self, new_value):
       self.token_static_token = new_value

    @property
    def token_bad_jti(self):
       return self.get("token_bad_jti")

    @token_bad_jti.setter
    def token_bad_jti(self, new_value):
       self.token_bad_jti = new_value

    @property
    def token_lookup_success(self):
       return self.get("token_lookup_success")

    @token_lookup_success.setter
    def token_lookup_success(self, new_value):
       self.token_lookup_success = new_value

    @property
    def token_lookup_notfound(self):
       return self.get("token_lookup_notfound")

    @token_lookup_notfound.setter
    def token_lookup_notfound(self, new_value):
       self.token_lookup_notfound = new_value

    @property
    def token_lookup_badrequest(self):
       return self.get("token_lookup_badrequest")

    @token_lookup_badrequest.setter
    def token_lookup_badrequest(self, new_value):
       self.token_lookup_badrequest = new_value

    @property
    def token_lookup_4xx_other(self):
       return self.get("token_lookup_4xx_other")

    @token_lookup_4xx_other.setter
    def token_lookup_4xx_other(self, new_value):
       self.token_lookup_4xx_other = new_value

    @property
    def token_lookup_error(self):
       return self.get("token_lookup_error")

    @token_lookup_error.setter
    def token_lookup_error(self, new_value):
       self.token_lookup_error = new_value

    @property
    def token_lookup_revoked(self):
       return self.get("token_lookup_revoked")

    @token_lookup_revoked.setter
    def token_lookup_revoked(self, new_value):
       self.token_lookup_revoked = new_value

    @property
    def token_basic_auth_decode_fail(self):
       return self.get("token_basic_auth_decode_fail")

    @token_basic_auth_decode_fail.setter
    def token_basic_auth_decode_fail(self, new_value):
       self.token_basic_auth_decode_fail = new_value

    @property
    def token_basic_auth_too_long(self):
       return self.get("token_basic_auth_too_long")

    @token_basic_auth_too_long.setter
    def token_basic_auth_too_long(self, new_value):
       self.token_basic_auth_too_long = new_value

    @property
    def token_basic_auth_no_password(self):
       return self.get("token_basic_auth_no_password")

    @token_basic_auth_no_password.setter
    def token_basic_auth_no_password(self, new_value):
       self.token_basic_auth_no_password = new_value

    @property
    def token_basic_auth_cached_success(self):
       return self.get("token_basic_auth_cached_success")

    @token_basic_auth_cached_success.setter
    def token_basic_auth_cached_success(self, new_value):
       self.token_basic_auth_cached_success = new_value

    @property
    def token_basic_auth_cached_failed(self):
       return self.get("token_basic_auth_cached_failed")

    @token_basic_auth_cached_failed.setter
    def token_basic_auth_cached_failed(self, new_value):
       self.token_basic_auth_cached_failed = new_value

    @cached_property
    def additional_properties_type():
        """
        This must be a method because a model may have properties that are
        of type self, this must run after the class is loaded
        """
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
        return {
            'allowed': (int,),  # noqa: E501
            'allowed_app_handled': (int,),  # noqa: E501
            'denied': (int,),  # noqa: E501
            'token_cached_failed': (int,),  # noqa: E501
            'token_cached_success': (int,),  # noqa: E501
            'token_parse_failed': (int,),  # noqa: E501
            'token_static_token': (int,),  # noqa: E501
            'token_bad_jti': (int,),  # noqa: E501
            'token_lookup_success': (int,),  # noqa: E501
            'token_lookup_notfound': (int,),  # noqa: E501
            'token_lookup_badrequest': (int,),  # noqa: E501
            'token_lookup_4xx_other': (int,),  # noqa: E501
            'token_lookup_error': (int,),  # noqa: E501
            'token_lookup_revoked': (int,),  # noqa: E501
            'token_basic_auth_decode_fail': (int,),  # noqa: E501
            'token_basic_auth_too_long': (int,),  # noqa: E501
            'token_basic_auth_no_password': (int,),  # noqa: E501
            'token_basic_auth_cached_success': (int,),  # noqa: E501
            'token_basic_auth_cached_failed': (int,),  # noqa: E501
        }

    @cached_property
    def discriminator():
        return None



    attribute_map = {
        'allowed': 'allowed',  # noqa: E501
        'allowed_app_handled': 'allowed_app_handled',  # noqa: E501
        'denied': 'denied',  # noqa: E501
        'token_cached_failed': 'token_cached_failed',  # noqa: E501
        'token_cached_success': 'token_cached_success',  # noqa: E501
        'token_parse_failed': 'token_parse_failed',  # noqa: E501
        'token_static_token': 'token_static_token',  # noqa: E501
        'token_bad_jti': 'token_bad_jti',  # noqa: E501
        'token_lookup_success': 'token_lookup_success',  # noqa: E501
        'token_lookup_notfound': 'token_lookup_notfound',  # noqa: E501
        'token_lookup_badrequest': 'token_lookup_badrequest',  # noqa: E501
        'token_lookup_4xx_other': 'token_lookup_4xx_other',  # noqa: E501
        'token_lookup_error': 'token_lookup_error',  # noqa: E501
        'token_lookup_revoked': 'token_lookup_revoked',  # noqa: E501
        'token_basic_auth_decode_fail': 'token_basic_auth_decode_fail',  # noqa: E501
        'token_basic_auth_too_long': 'token_basic_auth_too_long',  # noqa: E501
        'token_basic_auth_no_password': 'token_basic_auth_no_password',  # noqa: E501
        'token_basic_auth_cached_success': 'token_basic_auth_cached_success',  # noqa: E501
        'token_basic_auth_cached_failed': 'token_basic_auth_cached_failed',  # noqa: E501
    }

    read_only_vars = {
    }

    _composed_schemas = {}

    @classmethod
    @convert_js_args_to_python_args
    def _from_openapi_data(cls, allowed, allowed_app_handled, denied, token_cached_failed, token_cached_success, token_parse_failed, token_static_token, token_bad_jti, token_lookup_success, token_lookup_notfound, token_lookup_badrequest, token_lookup_4xx_other, token_lookup_error, token_lookup_revoked, token_basic_auth_decode_fail, token_basic_auth_too_long, token_basic_auth_no_password, token_basic_auth_cached_success, token_basic_auth_cached_failed, *args, **kwargs):  # noqa: E501
        """AgentConnectorAuthzStats - a model defined in OpenAPI

        Args:
            allowed (int): The number of allowed requests. 
            allowed_app_handled (int): The authz has been allowed due to the authentication handled by the application. 
            denied (int): The number of denied requests. 
            token_cached_failed (int): The number of times a failed lookup response was returned that had been cached. 
            token_cached_success (int): The number of times a successful lookup response was returned that had been cached. 
            token_parse_failed (int): The number of times a there was a failure parsing the token. This is due to missing claims in the token. 
            token_static_token (int): The number of times a static token was used in a request. 
            token_bad_jti (int): The number of times the token JTI was missing. 
            token_lookup_success (int): The number of times a token introspect was performed and the result was success. 
            token_lookup_notfound (int): The number of times a token introspect was performed and the result was not found. 
            token_lookup_badrequest (int): The number of times a token introspect was performed and the result was a bad request 
            token_lookup_4xx_other (int): The number of times a token introspect was performed and the result was a 4xx result that was not a 404, 410 or 400. 
            token_lookup_error (int): The number of times a token introspect was performed and the result was an error. 
            token_lookup_revoked (int): The number of times a token introspect was performed and the result returned was that the token has been revoked. 
            token_basic_auth_decode_fail (int): The number of times a request was made with basic auth and the base64 decode failed. 
            token_basic_auth_too_long (int): The number of times a request was made with basic auth and the basic auth string was too long. The maximum size permitted is 141 characters. 
            token_basic_auth_no_password (int): The number of times a request was made with basic auth and the password was missing. 
            token_basic_auth_cached_success (int): The number of times a request was made with basic auth and the successful result was returned from the cache. 
            token_basic_auth_cached_failed (int): The number of times a request was made with basic auth and the failed result was returned from the cache. 

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

        self.allowed = allowed
        self.allowed_app_handled = allowed_app_handled
        self.denied = denied
        self.token_cached_failed = token_cached_failed
        self.token_cached_success = token_cached_success
        self.token_parse_failed = token_parse_failed
        self.token_static_token = token_static_token
        self.token_bad_jti = token_bad_jti
        self.token_lookup_success = token_lookup_success
        self.token_lookup_notfound = token_lookup_notfound
        self.token_lookup_badrequest = token_lookup_badrequest
        self.token_lookup_4xx_other = token_lookup_4xx_other
        self.token_lookup_error = token_lookup_error
        self.token_lookup_revoked = token_lookup_revoked
        self.token_basic_auth_decode_fail = token_basic_auth_decode_fail
        self.token_basic_auth_too_long = token_basic_auth_too_long
        self.token_basic_auth_no_password = token_basic_auth_no_password
        self.token_basic_auth_cached_success = token_basic_auth_cached_success
        self.token_basic_auth_cached_failed = token_basic_auth_cached_failed
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
    def __init__(self, allowed, allowed_app_handled, denied, token_cached_failed, token_cached_success, token_parse_failed, token_static_token, token_bad_jti, token_lookup_success, token_lookup_notfound, token_lookup_badrequest, token_lookup_4xx_other, token_lookup_error, token_lookup_revoked, token_basic_auth_decode_fail, token_basic_auth_too_long, token_basic_auth_no_password, token_basic_auth_cached_success, token_basic_auth_cached_failed, *args, **kwargs):  # noqa: E501
        """AgentConnectorAuthzStats - a model defined in OpenAPI

        Args:
            allowed (int): The number of allowed requests. 
            allowed_app_handled (int): The authz has been allowed due to the authentication handled by the application. 
            denied (int): The number of denied requests. 
            token_cached_failed (int): The number of times a failed lookup response was returned that had been cached. 
            token_cached_success (int): The number of times a successful lookup response was returned that had been cached. 
            token_parse_failed (int): The number of times a there was a failure parsing the token. This is due to missing claims in the token. 
            token_static_token (int): The number of times a static token was used in a request. 
            token_bad_jti (int): The number of times the token JTI was missing. 
            token_lookup_success (int): The number of times a token introspect was performed and the result was success. 
            token_lookup_notfound (int): The number of times a token introspect was performed and the result was not found. 
            token_lookup_badrequest (int): The number of times a token introspect was performed and the result was a bad request 
            token_lookup_4xx_other (int): The number of times a token introspect was performed and the result was a 4xx result that was not a 404, 410 or 400. 
            token_lookup_error (int): The number of times a token introspect was performed and the result was an error. 
            token_lookup_revoked (int): The number of times a token introspect was performed and the result returned was that the token has been revoked. 
            token_basic_auth_decode_fail (int): The number of times a request was made with basic auth and the base64 decode failed. 
            token_basic_auth_too_long (int): The number of times a request was made with basic auth and the basic auth string was too long. The maximum size permitted is 141 characters. 
            token_basic_auth_no_password (int): The number of times a request was made with basic auth and the password was missing. 
            token_basic_auth_cached_success (int): The number of times a request was made with basic auth and the successful result was returned from the cache. 
            token_basic_auth_cached_failed (int): The number of times a request was made with basic auth and the failed result was returned from the cache. 

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

        self.allowed = allowed
        self.allowed_app_handled = allowed_app_handled
        self.denied = denied
        self.token_cached_failed = token_cached_failed
        self.token_cached_success = token_cached_success
        self.token_parse_failed = token_parse_failed
        self.token_static_token = token_static_token
        self.token_bad_jti = token_bad_jti
        self.token_lookup_success = token_lookup_success
        self.token_lookup_notfound = token_lookup_notfound
        self.token_lookup_badrequest = token_lookup_badrequest
        self.token_lookup_4xx_other = token_lookup_4xx_other
        self.token_lookup_error = token_lookup_error
        self.token_lookup_revoked = token_lookup_revoked
        self.token_basic_auth_decode_fail = token_basic_auth_decode_fail
        self.token_basic_auth_too_long = token_basic_auth_too_long
        self.token_basic_auth_no_password = token_basic_auth_no_password
        self.token_basic_auth_cached_success = token_basic_auth_cached_success
        self.token_basic_auth_cached_failed = token_basic_auth_cached_failed
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

