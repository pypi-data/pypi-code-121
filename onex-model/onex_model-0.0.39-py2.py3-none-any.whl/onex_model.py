# ONEx API 0.0.1
# License: MIT

import importlib
import logging
import json
import yaml
import requests
import urllib3
import io
import sys
import time
import re

try:
    from typing import Union, Dict, List, Any, Literal
except ImportError:
    from typing_extensions import Literal

if sys.version_info[0] == 3:
    unicode = str


def api(location=None, verify=True, logger=None, loglevel=logging.INFO, ext=None):
    """Create an instance of an Api class

    generator.Generator outputs a base Api class with the following:
    - an abstract method for each OpenAPI path item object
    - a concrete properties for each unique OpenAPI path item parameter.

    generator.Generator also outputs an HttpApi class that inherits the base
    Api class, implements the abstract methods and uses the common HttpTransport
    class send_recv method to communicate with a REST based server.

    Args
    ----
    - location (str): The location of an Open Traffic Generator server.
    - verify (bool): Verify the server's TLS certificate, or a string, in which
      case it must be a path to a CA bundle to use. Defaults to `True`.
      When set to `False`, requests will accept any TLS certificate presented by
      the server, and will ignore hostname mismatches and/or expired
      certificates, which will make your application vulnerable to
      man-in-the-middle (MitM) attacks. Setting verify to `False`
      may be useful during local development or testing.
    - logger (logging.Logger): A user defined logging.logger, if none is provided
      then a default logger with a stdout handler will be provided
    - loglevel (logging.loglevel): The logging package log level.
      The default loglevel is logging.INFO
    - ext (str): Name of an extension package
    """
    params = locals()
    if ext is None:
        return HttpApi(**params)
    try:
        lib = importlib.import_module("sanity_{}.onex_model_api".format(ext))
        return lib.Api(**params)
    except ImportError as err:
        msg = "Extension %s is not installed or invalid: %s"
        raise Exception(msg % (ext, err))


class HttpTransport(object):
    def __init__(self, **kwargs):
        """Use args from api() method to instantiate an HTTP transport"""
        self.location = (
            kwargs["location"]
            if "location" in kwargs and kwargs["location"] is not None
            else "https://localhost:443"
        )
        self.verify = kwargs["verify"] if "verify" in kwargs else False
        self.logger = kwargs["logger"] if "logger" in kwargs else None
        self.loglevel = kwargs["loglevel"] if "loglevel" in kwargs else logging.DEBUG
        if self.logger is None:
            stdout_handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(fmt="%(asctime)s [%(name)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
            formatter.converter = time.gmtime
            stdout_handler.setFormatter(formatter)
            self.logger = logging.Logger(self.__module__, level=self.loglevel)
            self.logger.addHandler(stdout_handler)
        self.logger.debug("HttpTransport args: {}".format(", ".join(["{}={!r}".format(k, v) for k, v in kwargs.items()])))
        if self.verify is False:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            self.logger.warning("Certificate verification is disabled")
        self._session = requests.Session()

    def send_recv(self, method, relative_url, payload=None, return_object=None, headers=None):
        url = "%s%s" % (self.location, relative_url)
        data = None
        headers = headers or {"Content-Type": "application/json"}
        if payload is not None:
            if isinstance(payload, bytes):
                data = payload
                headers["Content-Type"] = "application/octet-stream"
            elif isinstance(payload, (str, unicode)):
                data = payload
            elif isinstance(payload, OpenApiBase):
                data = payload.serialize()
            else:
                raise Exception("Type of payload provided is unknown")
        response = self._session.request(
            method=method,
            url=url,
            data=data,
            verify=False,
            allow_redirects=True,
            # TODO: add a timeout here
            headers=headers,
        )
        if response.ok:
            if "application/json" in response.headers["content-type"]:
                # TODO: we might want to check for utf-8 charset and decode
                # accordingly, but current impl works for now
                response_dict = yaml.safe_load(response.text)
                if return_object is None:
                    # if response type is not provided, return dictionary
                    # instead of python object
                    return response_dict
                else:
                    return return_object.deserialize(response_dict)
            elif "application/octet-stream" in response.headers["content-type"]:
                return io.BytesIO(response.content)
            else:
                # TODO: for now, return bare response object for unknown
                # content types
                return response
        else:
            raise Exception(response.status_code, yaml.safe_load(response.text))


class OpenApiBase(object):
    """Base class for all generated classes"""

    JSON = "json"
    YAML = "yaml"
    DICT = "dict"

    __slots__ = ()

    def __init__(self):
        pass

    def serialize(self, encoding=JSON):
        """Serialize the current object according to a specified encoding.

        Args
        ----
        - encoding (str[json, yaml, dict]): The object will be recursively
            serialized according to the specified encoding.
            The supported encodings are json, yaml and python dict.

        Returns
        -------
        - obj(Union[str, dict]): A str or dict object depending on the specified
            encoding. The json and yaml encodings will return a str object and
            the dict encoding will return a python dict object.
        """
        if encoding == OpenApiBase.JSON:
            return json.dumps(self._encode(), indent=2, sort_keys=True)
        elif encoding == OpenApiBase.YAML:
            return yaml.safe_dump(self._encode())
        elif encoding == OpenApiBase.DICT:
            return self._encode()
        else:
            raise NotImplementedError("Encoding %s not supported" % encoding)

    def _encode(self):
        raise NotImplementedError()

    def deserialize(self, serialized_object):
        """Deserialize a python object into the current object.

        If the input `serialized_object` does not match the current
        openapi object an exception will be raised.

        Args
        ----
        - serialized_object (Union[str, dict]): The object to deserialize.
            If the serialized_object is of type str then the internal encoding
            of the serialized_object must be json or yaml.

        Returns
        -------
        - obj(OpenApiObject): This object with all the
            serialized_object deserialized within.
        """
        if isinstance(serialized_object, (str, unicode)):
            serialized_object = yaml.safe_load(serialized_object)
        self._decode(serialized_object)
        return self

    def _decode(self, dict_object):
        raise NotImplementedError()


class OpenApiValidator(object):

    __slots__ = ()

    def __init__(self):
        pass

    def validate_mac(self, mac):
        if mac is None or not isinstance(mac, (str, unicode)) or mac.count(" ") != 0:
            return False
        try:
            if len(mac) != 17:
                return False
            return all([0 <= int(oct, 16) <= 255 for oct in mac.split(":")])
        except Exception:
            return False

    def validate_ipv4(self, ip):
        if ip is None or not isinstance(ip, (str, unicode)) or ip.count(" ") != 0:
            return False
        if len(ip.split(".")) != 4:
            return False
        try:
            return all([0 <= int(oct) <= 255 for oct in ip.split(".", 3)])
        except Exception:
            return False

    def validate_ipv6(self, ip):
        if ip is None or not isinstance(ip, (str, unicode)):
            return False
        ip = ip.strip()
        if ip.count(" ") > 0 or ip.count(":") > 7 or ip.count("::") > 1 or ip.count(":::") > 0:
            return False
        if (ip[0] == ":" and ip[:2] != "::") or (ip[-1] == ":" and ip[-2:] != "::"):
            return False
        if ip.count("::") == 0 and ip.count(":") != 7:
            return False
        if ip == "::":
            return True
        if ip[:2] == "::":
            ip = ip.replace("::", "0:")
        elif ip[-2:] == "::":
            ip = ip.replace("::", ":0")
        else:
            ip = ip.replace("::", ":0:")
        try:
            return all([True if (0 <= int(oct, 16) <= 65535) and (1 <= len(oct) <= 4) else False for oct in ip.split(":")])
        except Exception:
            return False

    def validate_hex(self, hex):
        if hex is None or not isinstance(hex, (str, unicode)):
            return False
        try:
            int(hex, 16)
            return True
        except Exception:
            return False

    def validate_integer(self, value, min, max):
        if value is None or not isinstance(value, int):
            return False
        if value < 0:
            return False
        if min is not None and value < min:
            return False
        if max is not None and value > max:
            return False
        return True

    def validate_float(self, value):
        return isinstance(value, (int, float))

    def validate_string(self, value, min_length, max_length):
        if value is None or not isinstance(value, (str, unicode)):
            return False
        if min_length is not None and len(value) < min_length:
            return False
        if max_length is not None and len(value) > max_length:
            return False
        return True

    def validate_bool(self, value):
        return isinstance(value, bool)

    def validate_list(self, value, itemtype, min, max, min_length, max_length):
        if value is None or not isinstance(value, list):
            return False
        v_obj = getattr(self, "validate_{}".format(itemtype), None)
        if v_obj is None:
            raise AttributeError("{} is not a valid attribute".format(itemtype))
        v_obj_lst = []
        for item in value:
            if itemtype == "integer":
                v_obj_lst.append(v_obj(item, min, max))
            elif itemtype == "string":
                v_obj_lst.append(v_obj(item, min_length, max_length))
            else:
                v_obj_lst.append(v_obj(item))
        return v_obj_lst

    def validate_binary(self, value):
        if value is None or not isinstance(value, (str, unicode)):
            return False
        return all([True if int(bin) == 0 or int(bin) == 1 else False for bin in value])

    def types_validation(self, value, type_, err_msg, itemtype=None, min=None, max=None, min_length=None, max_length=None):
        type_map = {int: "integer", str: "string", float: "float", bool: "bool", list: "list", "int64": "integer", "int32": "integer", "double": "float"}
        if type_ in type_map:
            type_ = type_map[type_]
        if itemtype is not None and itemtype in type_map:
            itemtype = type_map[itemtype]
        v_obj = getattr(self, "validate_{}".format(type_), None)
        if v_obj is None:
            msg = "{} is not a valid or unsupported format".format(type_)
            raise TypeError(msg)
        if type_ == "list":
            verdict = v_obj(value, itemtype, min, max, min_length, max_length)
            if all(verdict) is True:
                return
            err_msg = "{} \n {} are not valid".format(err_msg, [value[index] for index, item in enumerate(verdict) if item is False])
            verdict = False
        elif type_ == "integer":
            verdict = v_obj(value, min, max)
            if verdict is True:
                return
            min_max = ""
            if min is not None:
                min_max = ", expected min {}".format(min)
            if max is not None:
                min_max = min_max + ", expected max {}".format(max)
            err_msg = "{} \n got {} of type {} {}".format(err_msg, value, type(value), min_max)
        elif type_ == "string":
            verdict = v_obj(value, min_length, max_length)
            if verdict is True:
                return
            msg = ""
            if min_length is not None:
                msg = ", expected min {}".format(min_length)
            if max_length is not None:
                msg = msg + ", expected max {}".format(max_length)
            err_msg = "{} \n got {} of type {} {}".format(err_msg, value, type(value), msg)
        else:
            verdict = v_obj(value)
        if verdict is False:
            raise TypeError(err_msg)


class OpenApiObject(OpenApiBase, OpenApiValidator):
    """Base class for any /components/schemas object

    Every OpenApiObject is reuseable within the schema so it can
    exist in multiple locations within the hierarchy.
    That means it can exist in multiple locations as a
    leaf, parent/choice or parent.
    """

    __slots__ = ("_properties", "_parent", "_choice")
    _DEFAULTS = {}
    _TYPES = {}
    _REQUIRED = []

    def __init__(self, parent=None, choice=None):
        super(OpenApiObject, self).__init__()
        self._parent = parent
        self._choice = choice
        self._properties = {}

    @property
    def parent(self):
        return self._parent

    def _set_choice(self, name):
        if self._has_choice(name):
            for enum in self._TYPES["choice"]["enum"]:
                if enum in self._properties and name != enum:
                    self._properties.pop(enum)
            self._properties["choice"] = name

    def _has_choice(self, name):
        if "choice" in dir(self) and "_TYPES" in dir(self) and "choice" in self._TYPES and name in self._TYPES["choice"]["enum"]:
            return True
        else:
            return False

    def _get_property(self, name, default_value=None, parent=None, choice=None):
        if name in self._properties and self._properties[name] is not None:
            return self._properties[name]
        if isinstance(default_value, type) is True:
            self._set_choice(name)
            if "_choice" in default_value.__slots__:
                self._properties[name] = default_value(parent=parent, choice=choice)
            else:
                self._properties[name] = default_value(parent=parent)
            if "_DEFAULTS" in dir(self._properties[name]) and "choice" in self._properties[name]._DEFAULTS:
                getattr(self._properties[name], self._properties[name]._DEFAULTS["choice"])
        else:
            if default_value is None and name in self._DEFAULTS:
                self._set_choice(name)
                self._properties[name] = self._DEFAULTS[name]
            else:
                self._properties[name] = default_value
        return self._properties[name]

    def _set_property(self, name, value, choice=None):
        if name in self._DEFAULTS and value is None:
            self._set_choice(name)
            self._properties[name] = self._DEFAULTS[name]
        else:
            self._set_choice(name)
            self._properties[name] = value
        if self._parent is not None and self._choice is not None and value is not None:
            self._parent._set_property("choice", self._choice)

    def _encode(self):
        """Helper method for serialization"""
        output = {}
        self._validate_required()
        for key, value in self._properties.items():
            self._validate_types(key, value)
            if isinstance(value, (OpenApiObject, OpenApiIter)):
                output[key] = value._encode()
            elif value is not None:
                if key in self._TYPES and "format" in self._TYPES[key] and self._TYPES[key]["format"] == "int64":
                    value = str(value)
                output[key] = value
        return output

    def _decode(self, obj):
        dtypes = [list, str, int, float, bool]
        for property_name, property_value in obj.items():
            if property_name in self._TYPES:
                if isinstance(property_value, dict):
                    child = self._get_child_class(property_name)
                    if "choice" in child[1]._TYPES and "_parent" in child[1].__slots__:
                        property_value = child[1](self, property_name)._decode(property_value)
                    elif "_parent" in child[1].__slots__:
                        property_value = child[1](self)._decode(property_value)
                    else:
                        property_value = child[1]()._decode(property_value)
                elif isinstance(property_value, list) and property_name in self._TYPES and self._TYPES[property_name]["type"] not in dtypes:
                    child = self._get_child_class(property_name, True)
                    openapi_list = child[0]()
                    for item in property_value:
                        item = child[1]()._decode(item)
                        openapi_list._items.append(item)
                    property_value = openapi_list
                elif property_name in self._DEFAULTS and property_value is None:
                    if isinstance(self._DEFAULTS[property_name], tuple(dtypes)):
                        property_value = self._DEFAULTS[property_name]
                self._set_choice(property_name)
                if "format" in self._TYPES[property_name] and self._TYPES[property_name]["format"] == "int64":
                    property_value = int(property_value)
                self._properties[property_name] = property_value
            self._validate_types(property_name, property_value)
        self._validate_required()
        return self

    def _get_child_class(self, property_name, is_property_list=False):
        list_class = None
        class_name = self._TYPES[property_name]["type"]
        module = importlib.import_module(self.__module__)
        object_class = getattr(module, class_name)
        if is_property_list is True:
            list_class = object_class
            object_class = getattr(module, class_name[0:-4])
        return (list_class, object_class)

    def __str__(self):
        return self.serialize(encoding=self.YAML)

    def __deepcopy__(self, memo):
        """Creates a deep copy of the current object"""
        return self.__class__().deserialize(self.serialize())

    def __copy__(self):
        """Creates a deep copy of the current object"""
        return self.__deepcopy__(None)

    def __eq__(self, other):
        return self.__str__() == other.__str__()

    def clone(self):
        """Creates a deep copy of the current object"""
        return self.__deepcopy__(None)

    def _validate_required(self):
        """Validates the required properties are set
        Use getattr as it will set any defaults prior to validating
        """
        if getattr(self, "_REQUIRED", None) is None:
            return
        for name in self._REQUIRED:
            if getattr(self, name, None) is None:
                msg = "{} is a mandatory property of {}" " and should not be set to None".format(
                    name,
                    self.__class__,
                )
                raise ValueError(msg)

    def _validate_types(self, property_name, property_value):
        common_data_types = [list, str, int, float, bool]
        if property_name not in self._TYPES:
            # raise ValueError("Invalid Property {}".format(property_name))
            return
        details = self._TYPES[property_name]
        if property_value is None and property_name not in self._DEFAULTS and property_name not in self._REQUIRED:
            return
        if "enum" in details and property_value not in details["enum"]:
            msg = "property {} shall be one of these" " {} enum, but got {} at {}"
            raise TypeError(msg.format(property_name, details["enum"], property_value, self.__class__))
        if details["type"] in common_data_types and "format" not in details:
            msg = "property {} shall be of type {} at {}".format(property_name, details["type"], self.__class__)
            self.types_validation(property_value, details["type"], msg, details.get("itemtype"), details.get("minimum"), details.get("maximum"),
                                  details.get("minLength"), details.get("maxLength"))

        if details["type"] not in common_data_types:
            class_name = details["type"]
            # TODO Need to revisit importlib
            module = importlib.import_module(self.__module__)
            object_class = getattr(module, class_name)
            if not isinstance(property_value, object_class):
                msg = "property {} shall be of type {}," " but got {} at {}"
                raise TypeError(msg.format(property_name, class_name, type(property_value), self.__class__))
        if "format" in details:
            msg = "Invalid {} format, expected {} at {}".format(property_value, details["format"], self.__class__)
            _type = details["type"] if details["type"] is list else details["format"]
            self.types_validation(property_value, _type, msg, details["format"], details.get("minimum"), details.get("maximum"),
                                  details.get("minLength"), details.get("maxLength"))

    def validate(self):
        self._validate_required()
        for key, value in self._properties.items():
            self._validate_types(key, value)

    def get(self, name, with_default=False):
        """
        getattr for openapi object
        """
        if self._properties.get(name) is not None:
            return self._properties[name]
        elif with_default:
            # TODO need to find a way to avoid getattr
            choice = self._properties.get("choice") if "choice" in dir(self) else None
            getattr(self, name)
            if "choice" in dir(self):
                if choice is None and "choice" in self._properties:
                    self._properties.pop("choice")
                else:
                    self._properties["choice"] = choice
            return self._properties.pop(name)
        return None


class OpenApiIter(OpenApiBase):
    """Container class for OpenApiObject

    Inheriting classes contain 0..n instances of an OpenAPI components/schemas
    object.
    - config.flows.flow(name="1").flow(name="2").flow(name="3")

    The __getitem__ method allows getting an instance using ordinal.
    - config.flows[0]
    - config.flows[1:]
    - config.flows[0:1]
    - f1, f2, f3 = config.flows

    The __iter__ method allows for iterating across the encapsulated contents
    - for flow in config.flows:
    """

    __slots__ = ("_index", "_items")
    _GETITEM_RETURNS_CHOICE_OBJECT = False

    def __init__(self):
        super(OpenApiIter, self).__init__()
        self._index = -1
        self._items = []

    def __len__(self):
        return len(self._items)

    def _getitem(self, key):
        found = None
        if isinstance(key, int):
            found = self._items[key]
        elif isinstance(key, slice) is True:
            start, stop, step = key.indices(len(self))
            sliced = self.__class__()
            for i in range(start, stop, step):
                sliced._items.append(self._items[i])
            return sliced
        elif isinstance(key, str):
            for item in self._items:
                if item.name == key:
                    found = item
        if found is None:
            raise IndexError()
        if self._GETITEM_RETURNS_CHOICE_OBJECT is True and found._properties.get("choice") is not None:
            return found._properties[found._properties["choice"]]
        return found

    def _iter(self):
        self._index = -1
        return self

    def _next(self):
        if self._index + 1 >= len(self._items):
            raise StopIteration
        else:
            self._index += 1
        return self.__getitem__(self._index)

    def __getitem__(self, key):
        raise NotImplementedError("This should be overridden by the generator")

    def _add(self, item):
        self._items.append(item)
        self._index = len(self._items) - 1

    def remove(self, index):
        del self._items[index]
        self._index = len(self._items) - 1

    def append(self, item):
        """Append an item to the end of OpenApiIter
        TBD: type check, raise error on mismatch
        """
        if isinstance(item, OpenApiObject) is False:
            raise Exception("Item is not an instance of OpenApiObject")
        self._add(item)
        return self

    def clear(self):
        del self._items[:]
        self._index = -1

    def _encode(self):
        return [item._encode() for item in self._items]

    def _decode(self, encoded_list):
        item_class_name = self.__class__.__name__.replace("Iter", "")
        module = importlib.import_module(self.__module__)
        object_class = getattr(module, item_class_name)
        self.clear()
        for item in encoded_list:
            self._add(object_class()._decode(item))

    def __copy__(self):
        raise NotImplementedError("Shallow copy of OpenApiIter objects is not supported")

    def __deepcopy__(self, memo):
        raise NotImplementedError("Deep copy of OpenApiIter objects is not supported")

    def __str__(self):
        return yaml.safe_dump(self._encode())

    def __eq__(self, other):
        return self.__str__() == other.__str__()


class Config(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'name': {'type': str},
        'hosts': {'type': 'HostIter'},
        'fabric': {'type': 'Fabric'},
        'dataflow': {'type': 'Dataflow'},
        'chaos': {'type': 'Chaos'},
        'insights': {'type': 'Insights'},
        'layer1_profiles': {'type': 'L1SettingsProfileIter'},
        'annotations': {'type': str},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None, name=None, annotations=None):
        super(Config, self).__init__()
        self._parent = parent
        self._set_property('name', name)
        self._set_property('annotations', annotations)

    @property
    def name(self):
        # type: () -> str
        """name getter

        TBD

        Returns: str
        """
        return self._get_property('name')

    @name.setter
    def name(self, value):
        """name setter

        TBD

        value: str
        """
        self._set_property('name', value)

    @property
    def hosts(self):
        # type: () -> HostIter
        """hosts getter

        TBD

        Returns: HostIter
        """
        return self._get_property('hosts', HostIter, self._parent, self._choice)

    @property
    def fabric(self):
        # type: () -> Fabric
        """fabric getter

        

        Returns: Fabric
        """
        return self._get_property('fabric', Fabric)

    @property
    def dataflow(self):
        # type: () -> Dataflow
        """dataflow getter

        

        Returns: Dataflow
        """
        return self._get_property('dataflow', Dataflow)

    @property
    def chaos(self):
        # type: () -> Chaos
        """chaos getter

        Configuration of chaos experimentsConfiguration of chaos experiments

        Returns: Chaos
        """
        return self._get_property('chaos', Chaos)

    @property
    def insights(self):
        # type: () -> Insights
        """insights getter

        Configuration of insights providing methodsConfiguration of insights providing methods

        Returns: Insights
        """
        return self._get_property('insights', Insights)

    @property
    def layer1_profiles(self):
        # type: () -> L1SettingsProfileIter
        """layer1_profiles getter

        A list of Layer 1 settings profiles

        Returns: L1SettingsProfileIter
        """
        return self._get_property('layer1_profiles', L1SettingsProfileIter, self._parent, self._choice)

    @property
    def annotations(self):
        # type: () -> str
        """annotations getter

        TBD

        Returns: str
        """
        return self._get_property('annotations')

    @annotations.setter
    def annotations(self, value):
        """annotations setter

        TBD

        value: str
        """
        self._set_property('annotations', value)


class Host(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'name': {'type': str},
        'address': {'type': str},
        'prefix': {'type': int},
        'l1_profile_name': {'type': str},
        'annotations': {'type': str},
    } # type: Dict[str, str]

    _REQUIRED = ('address', 'name') # type: tuple(str)

    _DEFAULTS = {
        'prefix': 24,
    } # type: Dict[str, Union(type)]

    def __init__(self, parent=None, name=None, address=None, prefix=24, l1_profile_name=None, annotations=None):
        super(Host, self).__init__()
        self._parent = parent
        self._set_property('name', name)
        self._set_property('address', address)
        self._set_property('prefix', prefix)
        self._set_property('l1_profile_name', l1_profile_name)
        self._set_property('annotations', annotations)

    @property
    def name(self):
        # type: () -> str
        """name getter

        The name, uniquely identifying the host

        Returns: str
        """
        return self._get_property('name')

    @name.setter
    def name(self, value):
        """name setter

        The name, uniquely identifying the host

        value: str
        """
        self._set_property('name', value)

    @property
    def address(self):
        # type: () -> str
        """address getter

        The test address of the host

        Returns: str
        """
        return self._get_property('address')

    @address.setter
    def address(self, value):
        """address setter

        The test address of the host

        value: str
        """
        self._set_property('address', value)

    @property
    def prefix(self):
        # type: () -> int
        """prefix getter

        The prefix of the host

        Returns: int
        """
        return self._get_property('prefix')

    @prefix.setter
    def prefix(self, value):
        """prefix setter

        The prefix of the host

        value: int
        """
        self._set_property('prefix', value)

    @property
    def l1_profile_name(self):
        # type: () -> str
        """l1_profile_name getter

        The layer 1 settings profile associated with the host/front panel port.. . x-constraint:. - ../l1settings/l1_profiles.yaml#/components/schemas/L1SettingsProfile/properties/name. 

        Returns: str
        """
        return self._get_property('l1_profile_name')

    @l1_profile_name.setter
    def l1_profile_name(self, value):
        """l1_profile_name setter

        The layer 1 settings profile associated with the host/front panel port.. . x-constraint:. - ../l1settings/l1_profiles.yaml#/components/schemas/L1SettingsProfile/properties/name. 

        value: str
        """
        self._set_property('l1_profile_name', value)

    @property
    def annotations(self):
        # type: () -> str
        """annotations getter

        TBD

        Returns: str
        """
        return self._get_property('annotations')

    @annotations.setter
    def annotations(self, value):
        """annotations setter

        TBD

        value: str
        """
        self._set_property('annotations', value)


class HostIter(OpenApiIter):
    __slots__ = ('_parent', '_choice')

    _GETITEM_RETURNS_CHOICE_OBJECT = False

    def __init__(self, parent=None, choice=None):
        super(HostIter, self).__init__()
        self._parent = parent
        self._choice = choice

    def __getitem__(self, key):
        # type: (str) -> Union[Host]
        return self._getitem(key)

    def __iter__(self):
        # type: () -> HostIter
        return self._iter()

    def __next__(self):
        # type: () -> Host
        return self._next()

    def next(self):
        # type: () -> Host
        return self._next()

    def host(self, name=None, address=None, prefix=24, l1_profile_name=None, annotations=None):
        # type: (str,str,int,str,str) -> HostIter
        """Factory method that creates an instance of the Host class

        TBD

        Returns: HostIter
        """
        item = Host(parent=self._parent, name=name, address=address, prefix=prefix, l1_profile_name=l1_profile_name, annotations=annotations)
        self._add(item)
        return self

    def add(self, name=None, address=None, prefix=24, l1_profile_name=None, annotations=None):
        # type: (str,str,int,str,str) -> Host
        """Add method that creates and returns an instance of the Host class

        TBD

        Returns: Host
        """
        item = Host(parent=self._parent, name=name, address=address, prefix=prefix, l1_profile_name=l1_profile_name, annotations=annotations)
        self._add(item)
        return item


class Fabric(OpenApiObject):
    __slots__ = ('_parent','_choice')

    _TYPES = {
        'choice': {
            'type': str,
            'enum': [
                'clos',
            ],
        },
        'clos': {'type': 'FabricClos'},
        'qos_profiles': {'type': 'FabricQosProfileIter'},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    CLOS = 'clos' # type: str

    def __init__(self, parent=None, choice=None):
        super(Fabric, self).__init__()
        self._parent = parent
        if 'choice' in self._DEFAULTS and choice is None:
            getattr(self, self._DEFAULTS['choice'])
        else:
            self.choice = choice

    @property
    def clos(self):
        # type: () -> FabricClos
        """Factory property that returns an instance of the FabricClos class

        An emulation of a multistage switch topology. When folded, results in a topology with (up to) 3 tiers identified as . spine, pod and tor tier.

        Returns: FabricClos
        """
        return self._get_property('clos', FabricClos, self, 'clos')

    @property
    def choice(self):
        # type: () -> Union[Literal["clos"]]
        """choice getter

        TBD

        Returns: Union[Literal["clos"]]
        """
        return self._get_property('choice')

    @choice.setter
    def choice(self, value):
        """choice setter

        TBD

        value: Union[Literal["clos"]]
        """
        self._set_property('choice', value)

    @property
    def qos_profiles(self):
        # type: () -> FabricQosProfileIter
        """qos_profiles getter

        A list of Quality of Service (QoS) profiles

        Returns: FabricQosProfileIter
        """
        return self._get_property('qos_profiles', FabricQosProfileIter, self._parent, self._choice)


class FabricClos(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'spine': {'type': 'FabricSpine'},
        'pods': {'type': 'FabricPodIter'},
        'host_links': {'type': 'SwitchHostLinkIter'},
        'pod_profiles': {'type': 'FabricPodProfileIter'},
        'tor_profiles': {'type': 'FabricTorProfileIter'},
        'parallel_fabric_count': {'type': int},
        'annotations': {'type': str},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS = {
        'parallel_fabric_count': 1,
    } # type: Dict[str, Union(type)]

    def __init__(self, parent=None, parallel_fabric_count=1, annotations=None):
        super(FabricClos, self).__init__()
        self._parent = parent
        self._set_property('parallel_fabric_count', parallel_fabric_count)
        self._set_property('annotations', annotations)

    @property
    def spine(self):
        # type: () -> FabricSpine
        """spine getter

        

        Returns: FabricSpine
        """
        return self._get_property('spine', FabricSpine)

    @property
    def pods(self):
        # type: () -> FabricPodIter
        """pods getter

        The pods in the topology.

        Returns: FabricPodIter
        """
        return self._get_property('pods', FabricPodIter, self._parent, self._choice)

    @property
    def host_links(self):
        # type: () -> SwitchHostLinkIter
        """host_links getter

        TBD

        Returns: SwitchHostLinkIter
        """
        return self._get_property('host_links', SwitchHostLinkIter, self._parent, self._choice)

    @property
    def pod_profiles(self):
        # type: () -> FabricPodProfileIter
        """pod_profiles getter

        A list of pod profiles

        Returns: FabricPodProfileIter
        """
        return self._get_property('pod_profiles', FabricPodProfileIter, self._parent, self._choice)

    @property
    def tor_profiles(self):
        # type: () -> FabricTorProfileIter
        """tor_profiles getter

        A list of ToR switch profiles

        Returns: FabricTorProfileIter
        """
        return self._get_property('tor_profiles', FabricTorProfileIter, self._parent, self._choice)

    @property
    def parallel_fabric_count(self):
        # type: () -> int
        """parallel_fabric_count getter

        Number of parallel fabrics (aka fabric colors). Spine and pod switches . are fully meshed within a fabric

        Returns: int
        """
        return self._get_property('parallel_fabric_count')

    @parallel_fabric_count.setter
    def parallel_fabric_count(self, value):
        """parallel_fabric_count setter

        Number of parallel fabrics (aka fabric colors). Spine and pod switches . are fully meshed within a fabric

        value: int
        """
        self._set_property('parallel_fabric_count', value)

    @property
    def annotations(self):
        # type: () -> str
        """annotations getter

        TBD

        Returns: str
        """
        return self._get_property('annotations')

    @annotations.setter
    def annotations(self, value):
        """annotations setter

        TBD

        value: str
        """
        self._set_property('annotations', value)


class FabricSpine(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'count': {'type': int},
        'downlink_ecmp_mode': {
            'type': str,
            'enum': [
                'random_spray',
                'hash_3_tuple',
                'hash_5_tuple',
            ],
        },
        'qos_profile_name': {'type': str},
        'annotations': {'type': str},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS = {
        'count': 1,
    } # type: Dict[str, Union(type)]

    RANDOM_SPRAY = 'random_spray' # type: str
    HASH_3_TUPLE = 'hash_3_tuple' # type: str
    HASH_5_TUPLE = 'hash_5_tuple' # type: str

    def __init__(self, parent=None, count=1, downlink_ecmp_mode=None, qos_profile_name=None, annotations=None):
        super(FabricSpine, self).__init__()
        self._parent = parent
        self._set_property('count', count)
        self._set_property('downlink_ecmp_mode', downlink_ecmp_mode)
        self._set_property('qos_profile_name', qos_profile_name)
        self._set_property('annotations', annotations)

    @property
    def count(self):
        # type: () -> int
        """count getter

        The number of spines to be created with each spine sharing the same. downlink_ecmp_mode and qos_profile_name properties.

        Returns: int
        """
        return self._get_property('count')

    @count.setter
    def count(self, value):
        """count setter

        The number of spines to be created with each spine sharing the same. downlink_ecmp_mode and qos_profile_name properties.

        value: int
        """
        self._set_property('count', value)

    @property
    def downlink_ecmp_mode(self):
        # type: () -> Union[Literal["hash_3_tuple"], Literal["hash_5_tuple"], Literal["random_spray"]]
        """downlink_ecmp_mode getter

        The algorithm for packet distribution over ECMP links.. - random_spray randomly puts each packet on an ECMP member links . - hash_3_tuple is a 3 tuple hash of ipv4 src, dst, protocol. - hash_5_tuple is static_hash_ipv4_l4 but a different resulting RTAG7 hash mode

        Returns: Union[Literal["hash_3_tuple"], Literal["hash_5_tuple"], Literal["random_spray"]]
        """
        return self._get_property('downlink_ecmp_mode')

    @downlink_ecmp_mode.setter
    def downlink_ecmp_mode(self, value):
        """downlink_ecmp_mode setter

        The algorithm for packet distribution over ECMP links.. - random_spray randomly puts each packet on an ECMP member links . - hash_3_tuple is a 3 tuple hash of ipv4 src, dst, protocol. - hash_5_tuple is static_hash_ipv4_l4 but a different resulting RTAG7 hash mode

        value: Union[Literal["hash_3_tuple"], Literal["hash_5_tuple"], Literal["random_spray"]]
        """
        self._set_property('downlink_ecmp_mode', value)

    @property
    def qos_profile_name(self):
        # type: () -> str
        """qos_profile_name getter

        The name of a qos profile shared by the spines.. . x-constraint:. - #/components/schemas/QosProfile/properties/name. 

        Returns: str
        """
        return self._get_property('qos_profile_name')

    @qos_profile_name.setter
    def qos_profile_name(self, value):
        """qos_profile_name setter

        The name of a qos profile shared by the spines.. . x-constraint:. - #/components/schemas/QosProfile/properties/name. 

        value: str
        """
        self._set_property('qos_profile_name', value)

    @property
    def annotations(self):
        # type: () -> str
        """annotations getter

        TBD

        Returns: str
        """
        return self._get_property('annotations')

    @annotations.setter
    def annotations(self, value):
        """annotations setter

        TBD

        value: str
        """
        self._set_property('annotations', value)


class FabricPod(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'count': {'type': int},
        'pod_profile_name': {'type': str},
        'annotations': {'type': str},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS = {
        'count': 1,
    } # type: Dict[str, Union(type)]

    def __init__(self, parent=None, count=1, pod_profile_name=None, annotations=None):
        super(FabricPod, self).__init__()
        self._parent = parent
        self._set_property('count', count)
        self._set_property('pod_profile_name', pod_profile_name)
        self._set_property('annotations', annotations)

    @property
    def count(self):
        # type: () -> int
        """count getter

        The number of pods that will share the same profile

        Returns: int
        """
        return self._get_property('count')

    @count.setter
    def count(self, value):
        """count setter

        The number of pods that will share the same profile

        value: int
        """
        self._set_property('count', value)

    @property
    def pod_profile_name(self):
        # type: () -> str
        """pod_profile_name getter

        The pod profile associated with the pod(s).. . x-constraint:. - #/components/schemas/PodProfile/properties/name. 

        Returns: str
        """
        return self._get_property('pod_profile_name')

    @pod_profile_name.setter
    def pod_profile_name(self, value):
        """pod_profile_name setter

        The pod profile associated with the pod(s).. . x-constraint:. - #/components/schemas/PodProfile/properties/name. 

        value: str
        """
        self._set_property('pod_profile_name', value)

    @property
    def annotations(self):
        # type: () -> str
        """annotations getter

        TBD

        Returns: str
        """
        return self._get_property('annotations')

    @annotations.setter
    def annotations(self, value):
        """annotations setter

        TBD

        value: str
        """
        self._set_property('annotations', value)


class FabricPodIter(OpenApiIter):
    __slots__ = ('_parent', '_choice')

    _GETITEM_RETURNS_CHOICE_OBJECT = False

    def __init__(self, parent=None, choice=None):
        super(FabricPodIter, self).__init__()
        self._parent = parent
        self._choice = choice

    def __getitem__(self, key):
        # type: (str) -> Union[FabricPod]
        return self._getitem(key)

    def __iter__(self):
        # type: () -> FabricPodIter
        return self._iter()

    def __next__(self):
        # type: () -> FabricPod
        return self._next()

    def next(self):
        # type: () -> FabricPod
        return self._next()

    def pod(self, count=1, pod_profile_name=None, annotations=None):
        # type: (int,str,str) -> FabricPodIter
        """Factory method that creates an instance of the FabricPod class

        TBD

        Returns: FabricPodIter
        """
        item = FabricPod(parent=self._parent, count=count, pod_profile_name=pod_profile_name, annotations=annotations)
        self._add(item)
        return self

    def add(self, count=1, pod_profile_name=None, annotations=None):
        # type: (int,str,str) -> FabricPod
        """Add method that creates and returns an instance of the FabricPod class

        TBD

        Returns: FabricPod
        """
        item = FabricPod(parent=self._parent, count=count, pod_profile_name=pod_profile_name, annotations=annotations)
        self._add(item)
        return item


class SwitchHostLink(OpenApiObject):
    __slots__ = ('_parent','_choice')

    _TYPES = {
        'host_name': {'type': str},
        'host_type': {
            'type': str,
            'enum': [
                'external',
                'internal_traffic_sink',
            ],
        },
        'front_panel_port': {'type': int},
        'choice': {
            'type': str,
            'enum': [
                'spine',
                'pod',
                'tor',
            ],
        },
        'spine': {
            'type': int,
            'minimum': 1,
        },
        'pod': {'type': 'SwitchHostLinkSwitchRef'},
        'tor': {'type': 'SwitchHostLinkSwitchRef'},
        'annotations': {'type': str},
    } # type: Dict[str, str]

    _REQUIRED = ('host_name',) # type: tuple(str)

    _DEFAULTS = {
        'host_type': 'external',
        'choice': 'tor',
    } # type: Dict[str, Union(type)]

    EXTERNAL = 'external' # type: str
    INTERNAL_TRAFFIC_SINK = 'internal_traffic_sink' # type: str

    SPINE = 'spine' # type: str
    POD = 'pod' # type: str
    TOR = 'tor' # type: str

    def __init__(self, parent=None, choice=None, host_name=None, host_type='external', front_panel_port=None, spine=None, annotations=None):
        super(SwitchHostLink, self).__init__()
        self._parent = parent
        self._set_property('host_name', host_name)
        self._set_property('host_type', host_type)
        self._set_property('front_panel_port', front_panel_port)
        self._set_property('spine', spine)
        self._set_property('annotations', annotations)
        if 'choice' in self._DEFAULTS and choice is None:
            getattr(self, self._DEFAULTS['choice'])
        else:
            self.choice = choice

    @property
    def pod(self):
        # type: () -> SwitchHostLinkSwitchRef
        """Factory property that returns an instance of the SwitchHostLinkSwitchRef class

        Location of the switch based on pod and switch index

        Returns: SwitchHostLinkSwitchRef
        """
        return self._get_property('pod', SwitchHostLinkSwitchRef, self, 'pod')

    @property
    def tor(self):
        # type: () -> SwitchHostLinkSwitchRef
        """Factory property that returns an instance of the SwitchHostLinkSwitchRef class

        Location of the switch based on pod and switch index

        Returns: SwitchHostLinkSwitchRef
        """
        return self._get_property('tor', SwitchHostLinkSwitchRef, self, 'tor')

    @property
    def host_name(self):
        # type: () -> str
        """host_name getter

        TBD. . x-constraint:. - #components/schemas/Host/properties/name. 

        Returns: str
        """
        return self._get_property('host_name')

    @host_name.setter
    def host_name(self, value):
        """host_name setter

        TBD. . x-constraint:. - #components/schemas/Host/properties/name. 

        value: str
        """
        self._set_property('host_name', value)

    @property
    def host_type(self):
        # type: () -> Union[Literal["external"], Literal["internal_traffic_sink"]]
        """host_type getter

        Optional host type, if fabric is rendered on physical box.. - external for hosts/servers physically connected to front panel ports. - internal_traffic_sink for an emulated server that acts as a traffic sink (i.e. packets sent to its IP address will be routed through the emulated fabric)

        Returns: Union[Literal["external"], Literal["internal_traffic_sink"]]
        """
        return self._get_property('host_type')

    @host_type.setter
    def host_type(self, value):
        """host_type setter

        Optional host type, if fabric is rendered on physical box.. - external for hosts/servers physically connected to front panel ports. - internal_traffic_sink for an emulated server that acts as a traffic sink (i.e. packets sent to its IP address will be routed through the emulated fabric)

        value: Union[Literal["external"], Literal["internal_traffic_sink"]]
        """
        self._set_property('host_type', value)

    @property
    def front_panel_port(self):
        # type: () -> int
        """front_panel_port getter

        Optional front panel port number, if fabric is rendered on physical box

        Returns: int
        """
        return self._get_property('front_panel_port')

    @front_panel_port.setter
    def front_panel_port(self, value):
        """front_panel_port setter

        Optional front panel port number, if fabric is rendered on physical box

        value: int
        """
        self._set_property('front_panel_port', value)

    @property
    def choice(self):
        # type: () -> Union[Literal["pod"], Literal["spine"], Literal["tor"]]
        """choice getter

        TBD

        Returns: Union[Literal["pod"], Literal["spine"], Literal["tor"]]
        """
        return self._get_property('choice')

    @choice.setter
    def choice(self, value):
        """choice setter

        TBD

        value: Union[Literal["pod"], Literal["spine"], Literal["tor"]]
        """
        self._set_property('choice', value)

    @property
    def spine(self):
        # type: () -> int
        """spine getter

        One based index of the spine switch based on the number of spines . configured in the clos topology.

        Returns: int
        """
        return self._get_property('spine')

    @spine.setter
    def spine(self, value):
        """spine setter

        One based index of the spine switch based on the number of spines . configured in the clos topology.

        value: int
        """
        self._set_property('spine', value, 'spine')

    @property
    def annotations(self):
        # type: () -> str
        """annotations getter

        TBD

        Returns: str
        """
        return self._get_property('annotations')

    @annotations.setter
    def annotations(self, value):
        """annotations setter

        TBD

        value: str
        """
        self._set_property('annotations', value)


class SwitchHostLinkSwitchRef(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'pod_index': {
            'type': int,
            'minimum': 1,
        },
        'switch_index': {
            'type': int,
            'minimum': 1,
        },
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS = {
        'pod_index': 1,
        'switch_index': 1,
    } # type: Dict[str, Union(type)]

    def __init__(self, parent=None, pod_index=1, switch_index=1):
        super(SwitchHostLinkSwitchRef, self).__init__()
        self._parent = parent
        self._set_property('pod_index', pod_index)
        self._set_property('switch_index', switch_index)

    @property
    def pod_index(self):
        # type: () -> int
        """pod_index getter

        One-based index of the pod based on the number of pods in the fabric

        Returns: int
        """
        return self._get_property('pod_index')

    @pod_index.setter
    def pod_index(self, value):
        """pod_index setter

        One-based index of the pod based on the number of pods in the fabric

        value: int
        """
        self._set_property('pod_index', value)

    @property
    def switch_index(self):
        # type: () -> int
        """switch_index getter

        One-based index of the pod or ToR switch in the indicated pod

        Returns: int
        """
        return self._get_property('switch_index')

    @switch_index.setter
    def switch_index(self, value):
        """switch_index setter

        One-based index of the pod or ToR switch in the indicated pod

        value: int
        """
        self._set_property('switch_index', value)


class SwitchHostLinkIter(OpenApiIter):
    __slots__ = ('_parent', '_choice')

    _GETITEM_RETURNS_CHOICE_OBJECT = False

    def __init__(self, parent=None, choice=None):
        super(SwitchHostLinkIter, self).__init__()
        self._parent = parent
        self._choice = choice

    def __getitem__(self, key):
        # type: (str) -> Union[SwitchHostLink, SwitchHostLinkSwitchRef]
        return self._getitem(key)

    def __iter__(self):
        # type: () -> SwitchHostLinkIter
        return self._iter()

    def __next__(self):
        # type: () -> SwitchHostLink
        return self._next()

    def next(self):
        # type: () -> SwitchHostLink
        return self._next()

    def switchhostlink(self, host_name=None, host_type='external', front_panel_port=None, spine=None, annotations=None):
        # type: (str,Union[Literal["external"], Literal["internal_traffic_sink"]],int,int,str) -> SwitchHostLinkIter
        """Factory method that creates an instance of the SwitchHostLink class

        The ingress point of a host which is the index of a spine, pod or tor switch.

        Returns: SwitchHostLinkIter
        """
        item = SwitchHostLink(parent=self._parent, choice=self._choice, host_name=host_name, host_type=host_type, front_panel_port=front_panel_port, spine=spine, annotations=annotations)
        self._add(item)
        return self

    def add(self, host_name=None, host_type='external', front_panel_port=None, spine=None, annotations=None):
        # type: (str,Union[Literal["external"], Literal["internal_traffic_sink"]],int,int,str) -> SwitchHostLink
        """Add method that creates and returns an instance of the SwitchHostLink class

        The ingress point of a host which is the index of a spine, pod or tor switch.

        Returns: SwitchHostLink
        """
        item = SwitchHostLink(parent=self._parent, choice=self._choice, host_name=host_name, host_type=host_type, front_panel_port=front_panel_port, spine=spine, annotations=annotations)
        self._add(item)
        return item


class FabricPodProfile(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'name': {'type': str},
        'pod_switch': {'type': 'FabricPodSwitch'},
        'tors': {'type': 'FabricTorIter'},
        'pod_to_spine_oversubscription': {'type': str},
        'annotations': {'type': str},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None, name=None, pod_to_spine_oversubscription=None, annotations=None):
        super(FabricPodProfile, self).__init__()
        self._parent = parent
        self._set_property('name', name)
        self._set_property('pod_to_spine_oversubscription', pod_to_spine_oversubscription)
        self._set_property('annotations', annotations)

    @property
    def name(self):
        # type: () -> str
        """name getter

        Uniquely identifies a pod profile

        Returns: str
        """
        return self._get_property('name')

    @name.setter
    def name(self, value):
        """name setter

        Uniquely identifies a pod profile

        value: str
        """
        self._set_property('name', value)

    @property
    def pod_switch(self):
        # type: () -> FabricPodSwitch
        """pod_switch getter

        

        Returns: FabricPodSwitch
        """
        return self._get_property('pod_switch', FabricPodSwitch)

    @property
    def tors(self):
        # type: () -> FabricTorIter
        """tors getter

        The ToRs in the pod

        Returns: FabricTorIter
        """
        return self._get_property('tors', FabricTorIter, self._parent, self._choice)

    @property
    def pod_to_spine_oversubscription(self):
        # type: () -> str
        """pod_to_spine_oversubscription getter

        Oversubscription ratio of the pod switches

        Returns: str
        """
        return self._get_property('pod_to_spine_oversubscription')

    @pod_to_spine_oversubscription.setter
    def pod_to_spine_oversubscription(self, value):
        """pod_to_spine_oversubscription setter

        Oversubscription ratio of the pod switches

        value: str
        """
        self._set_property('pod_to_spine_oversubscription', value)

    @property
    def annotations(self):
        # type: () -> str
        """annotations getter

        TBD

        Returns: str
        """
        return self._get_property('annotations')

    @annotations.setter
    def annotations(self, value):
        """annotations setter

        TBD

        value: str
        """
        self._set_property('annotations', value)


class FabricPodSwitch(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'count': {'type': int},
        'uplink_ecmp_mode': {
            'type': str,
            'enum': [
                'random_spray',
                'hash_3_tuple',
                'hash_5_tuple',
            ],
        },
        'downlink_ecmp_mode': {
            'type': str,
            'enum': [
                'random_spray',
                'hash_3_tuple',
                'hash_5_tuple',
            ],
        },
        'qos_profile_name': {'type': str},
        'annotations': {'type': str},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS = {
        'count': 1,
    } # type: Dict[str, Union(type)]

    RANDOM_SPRAY = 'random_spray' # type: str
    HASH_3_TUPLE = 'hash_3_tuple' # type: str
    HASH_5_TUPLE = 'hash_5_tuple' # type: str

    RANDOM_SPRAY = 'random_spray' # type: str
    HASH_3_TUPLE = 'hash_3_tuple' # type: str
    HASH_5_TUPLE = 'hash_5_tuple' # type: str

    def __init__(self, parent=None, count=1, uplink_ecmp_mode=None, downlink_ecmp_mode=None, qos_profile_name=None, annotations=None):
        super(FabricPodSwitch, self).__init__()
        self._parent = parent
        self._set_property('count', count)
        self._set_property('uplink_ecmp_mode', uplink_ecmp_mode)
        self._set_property('downlink_ecmp_mode', downlink_ecmp_mode)
        self._set_property('qos_profile_name', qos_profile_name)
        self._set_property('annotations', annotations)

    @property
    def count(self):
        # type: () -> int
        """count getter

        TBD

        Returns: int
        """
        return self._get_property('count')

    @count.setter
    def count(self, value):
        """count setter

        TBD

        value: int
        """
        self._set_property('count', value)

    @property
    def uplink_ecmp_mode(self):
        # type: () -> Union[Literal["hash_3_tuple"], Literal["hash_5_tuple"], Literal["random_spray"]]
        """uplink_ecmp_mode getter

        The algorithm for packet distribution over ECMP links.. - random_spray randomly puts each packet on an ECMP member links . - hash_3_tuple is a 3 tuple hash of ipv4 src, dst, protocol. - hash_5_tuple is static_hash_ipv4_l4 but a different resulting RTAG7 hash mode

        Returns: Union[Literal["hash_3_tuple"], Literal["hash_5_tuple"], Literal["random_spray"]]
        """
        return self._get_property('uplink_ecmp_mode')

    @uplink_ecmp_mode.setter
    def uplink_ecmp_mode(self, value):
        """uplink_ecmp_mode setter

        The algorithm for packet distribution over ECMP links.. - random_spray randomly puts each packet on an ECMP member links . - hash_3_tuple is a 3 tuple hash of ipv4 src, dst, protocol. - hash_5_tuple is static_hash_ipv4_l4 but a different resulting RTAG7 hash mode

        value: Union[Literal["hash_3_tuple"], Literal["hash_5_tuple"], Literal["random_spray"]]
        """
        self._set_property('uplink_ecmp_mode', value)

    @property
    def downlink_ecmp_mode(self):
        # type: () -> Union[Literal["hash_3_tuple"], Literal["hash_5_tuple"], Literal["random_spray"]]
        """downlink_ecmp_mode getter

        The algorithm for packet distribution over ECMP links.. - random_spray randomly puts each packet on an ECMP member links . - hash_3_tuple is a 3 tuple hash of ipv4 src, dst, protocol. - hash_5_tuple is static_hash_ipv4_l4 but a different resulting RTAG7 hash mode

        Returns: Union[Literal["hash_3_tuple"], Literal["hash_5_tuple"], Literal["random_spray"]]
        """
        return self._get_property('downlink_ecmp_mode')

    @downlink_ecmp_mode.setter
    def downlink_ecmp_mode(self, value):
        """downlink_ecmp_mode setter

        The algorithm for packet distribution over ECMP links.. - random_spray randomly puts each packet on an ECMP member links . - hash_3_tuple is a 3 tuple hash of ipv4 src, dst, protocol. - hash_5_tuple is static_hash_ipv4_l4 but a different resulting RTAG7 hash mode

        value: Union[Literal["hash_3_tuple"], Literal["hash_5_tuple"], Literal["random_spray"]]
        """
        self._set_property('downlink_ecmp_mode', value)

    @property
    def qos_profile_name(self):
        # type: () -> str
        """qos_profile_name getter

        The name of a qos profile associated with the switches in this pod.. . x-constraint:. - #/components/schemas/QosProfile/properties/name. 

        Returns: str
        """
        return self._get_property('qos_profile_name')

    @qos_profile_name.setter
    def qos_profile_name(self, value):
        """qos_profile_name setter

        The name of a qos profile associated with the switches in this pod.. . x-constraint:. - #/components/schemas/QosProfile/properties/name. 

        value: str
        """
        self._set_property('qos_profile_name', value)

    @property
    def annotations(self):
        # type: () -> str
        """annotations getter

        TBD

        Returns: str
        """
        return self._get_property('annotations')

    @annotations.setter
    def annotations(self, value):
        """annotations setter

        TBD

        value: str
        """
        self._set_property('annotations', value)


class FabricTor(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'count': {'type': int},
        'tor_profile_name': {'type': str},
        'annotations': {'type': str},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS = {
        'count': 1,
    } # type: Dict[str, Union(type)]

    def __init__(self, parent=None, count=1, tor_profile_name=None, annotations=None):
        super(FabricTor, self).__init__()
        self._parent = parent
        self._set_property('count', count)
        self._set_property('tor_profile_name', tor_profile_name)
        self._set_property('annotations', annotations)

    @property
    def count(self):
        # type: () -> int
        """count getter

        number of ToR switches that will share the same profile

        Returns: int
        """
        return self._get_property('count')

    @count.setter
    def count(self, value):
        """count setter

        number of ToR switches that will share the same profile

        value: int
        """
        self._set_property('count', value)

    @property
    def tor_profile_name(self):
        # type: () -> str
        """tor_profile_name getter

        The names of ToR profiles associated with the ToR switch(es). . x-constraint:. - #/components/schemas/TorProfile/properties/name. 

        Returns: str
        """
        return self._get_property('tor_profile_name')

    @tor_profile_name.setter
    def tor_profile_name(self, value):
        """tor_profile_name setter

        The names of ToR profiles associated with the ToR switch(es). . x-constraint:. - #/components/schemas/TorProfile/properties/name. 

        value: str
        """
        self._set_property('tor_profile_name', value)

    @property
    def annotations(self):
        # type: () -> str
        """annotations getter

        TBD

        Returns: str
        """
        return self._get_property('annotations')

    @annotations.setter
    def annotations(self, value):
        """annotations setter

        TBD

        value: str
        """
        self._set_property('annotations', value)


class FabricTorIter(OpenApiIter):
    __slots__ = ('_parent', '_choice')

    _GETITEM_RETURNS_CHOICE_OBJECT = False

    def __init__(self, parent=None, choice=None):
        super(FabricTorIter, self).__init__()
        self._parent = parent
        self._choice = choice

    def __getitem__(self, key):
        # type: (str) -> Union[FabricTor]
        return self._getitem(key)

    def __iter__(self):
        # type: () -> FabricTorIter
        return self._iter()

    def __next__(self):
        # type: () -> FabricTor
        return self._next()

    def next(self):
        # type: () -> FabricTor
        return self._next()

    def tor(self, count=1, tor_profile_name=None, annotations=None):
        # type: (int,str,str) -> FabricTorIter
        """Factory method that creates an instance of the FabricTor class

        TBD

        Returns: FabricTorIter
        """
        item = FabricTor(parent=self._parent, count=count, tor_profile_name=tor_profile_name, annotations=annotations)
        self._add(item)
        return self

    def add(self, count=1, tor_profile_name=None, annotations=None):
        # type: (int,str,str) -> FabricTor
        """Add method that creates and returns an instance of the FabricTor class

        TBD

        Returns: FabricTor
        """
        item = FabricTor(parent=self._parent, count=count, tor_profile_name=tor_profile_name, annotations=annotations)
        self._add(item)
        return item


class FabricPodProfileIter(OpenApiIter):
    __slots__ = ('_parent', '_choice')

    _GETITEM_RETURNS_CHOICE_OBJECT = False

    def __init__(self, parent=None, choice=None):
        super(FabricPodProfileIter, self).__init__()
        self._parent = parent
        self._choice = choice

    def __getitem__(self, key):
        # type: (str) -> Union[FabricPodProfile]
        return self._getitem(key)

    def __iter__(self):
        # type: () -> FabricPodProfileIter
        return self._iter()

    def __next__(self):
        # type: () -> FabricPodProfile
        return self._next()

    def next(self):
        # type: () -> FabricPodProfile
        return self._next()

    def podprofile(self, name=None, pod_to_spine_oversubscription=None, annotations=None):
        # type: (str,str,str) -> FabricPodProfileIter
        """Factory method that creates an instance of the FabricPodProfile class

        TBD

        Returns: FabricPodProfileIter
        """
        item = FabricPodProfile(parent=self._parent, name=name, pod_to_spine_oversubscription=pod_to_spine_oversubscription, annotations=annotations)
        self._add(item)
        return self

    def add(self, name=None, pod_to_spine_oversubscription=None, annotations=None):
        # type: (str,str,str) -> FabricPodProfile
        """Add method that creates and returns an instance of the FabricPodProfile class

        TBD

        Returns: FabricPodProfile
        """
        item = FabricPodProfile(parent=self._parent, name=name, pod_to_spine_oversubscription=pod_to_spine_oversubscription, annotations=annotations)
        self._add(item)
        return item


class FabricTorProfile(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'name': {'type': str},
        'tor_mode': {
            'type': str,
            'enum': [
                'layer2',
                'layer3',
            ],
        },
        'uplink_ecmp_mode': {
            'type': str,
            'enum': [
                'random_spray',
                'hash_3_tuple',
                'hash_5_tuple',
            ],
        },
        'qos_profile_name': {'type': str},
        'tor_to_pod_oversubscription': {'type': 'FabricTorProfileOversubscription'},
        'annotations': {'type': str},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    LAYER2 = 'layer2' # type: str
    LAYER3 = 'layer3' # type: str

    RANDOM_SPRAY = 'random_spray' # type: str
    HASH_3_TUPLE = 'hash_3_tuple' # type: str
    HASH_5_TUPLE = 'hash_5_tuple' # type: str

    def __init__(self, parent=None, name=None, tor_mode=None, uplink_ecmp_mode=None, qos_profile_name=None, annotations=None):
        super(FabricTorProfile, self).__init__()
        self._parent = parent
        self._set_property('name', name)
        self._set_property('tor_mode', tor_mode)
        self._set_property('uplink_ecmp_mode', uplink_ecmp_mode)
        self._set_property('qos_profile_name', qos_profile_name)
        self._set_property('annotations', annotations)

    @property
    def name(self):
        # type: () -> str
        """name getter

        TBD

        Returns: str
        """
        return self._get_property('name')

    @name.setter
    def name(self, value):
        """name setter

        TBD

        value: str
        """
        self._set_property('name', value)

    @property
    def tor_mode(self):
        # type: () -> Union[Literal["layer2"], Literal["layer3"]]
        """tor_mode getter

        ToR switch mode

        Returns: Union[Literal["layer2"], Literal["layer3"]]
        """
        return self._get_property('tor_mode')

    @tor_mode.setter
    def tor_mode(self, value):
        """tor_mode setter

        ToR switch mode

        value: Union[Literal["layer2"], Literal["layer3"]]
        """
        self._set_property('tor_mode', value)

    @property
    def uplink_ecmp_mode(self):
        # type: () -> Union[Literal["hash_3_tuple"], Literal["hash_5_tuple"], Literal["random_spray"]]
        """uplink_ecmp_mode getter

        The algorithm for packet distribution over ECMP links.. - random_spray randomly puts each packet on an ECMP member links . - hash_3_tuple is a 3 tuple hash of ipv4 src, dst, protocol. - hash_5_tuple is static_hash_ipv4_l4 but a different resulting RTAG7 hash mode

        Returns: Union[Literal["hash_3_tuple"], Literal["hash_5_tuple"], Literal["random_spray"]]
        """
        return self._get_property('uplink_ecmp_mode')

    @uplink_ecmp_mode.setter
    def uplink_ecmp_mode(self, value):
        """uplink_ecmp_mode setter

        The algorithm for packet distribution over ECMP links.. - random_spray randomly puts each packet on an ECMP member links . - hash_3_tuple is a 3 tuple hash of ipv4 src, dst, protocol. - hash_5_tuple is static_hash_ipv4_l4 but a different resulting RTAG7 hash mode

        value: Union[Literal["hash_3_tuple"], Literal["hash_5_tuple"], Literal["random_spray"]]
        """
        self._set_property('uplink_ecmp_mode', value)

    @property
    def qos_profile_name(self):
        # type: () -> str
        """qos_profile_name getter

        The name of a qos profile associated with the ToR switch(es). . x-constraint:. - #/components/schemas/QosProfile/properties/name. 

        Returns: str
        """
        return self._get_property('qos_profile_name')

    @qos_profile_name.setter
    def qos_profile_name(self, value):
        """qos_profile_name setter

        The name of a qos profile associated with the ToR switch(es). . x-constraint:. - #/components/schemas/QosProfile/properties/name. 

        value: str
        """
        self._set_property('qos_profile_name', value)

    @property
    def tor_to_pod_oversubscription(self):
        # type: () -> FabricTorProfileOversubscription
        """tor_to_pod_oversubscription getter

        The oversubscription of the ToR switch(es)The oversubscription of the ToR switch(es)

        Returns: FabricTorProfileOversubscription
        """
        return self._get_property('tor_to_pod_oversubscription', FabricTorProfileOversubscription)

    @property
    def annotations(self):
        # type: () -> str
        """annotations getter

        TBD

        Returns: str
        """
        return self._get_property('annotations')

    @annotations.setter
    def annotations(self, value):
        """annotations setter

        TBD

        value: str
        """
        self._set_property('annotations', value)


class FabricTorProfileOversubscription(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'ratio': {'type': str},
        'mode': {
            'type': str,
            'enum': [
                'use_host_capacity',
                'use_fabric_host_links',
            ],
        },
        'host_capacity': {'type': int},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS = {
        'mode': 'use_host_capacity',
        'host_capacity': 1,
    } # type: Dict[str, Union(type)]

    USE_HOST_CAPACITY = 'use_host_capacity' # type: str
    USE_FABRIC_HOST_LINKS = 'use_fabric_host_links' # type: str

    def __init__(self, parent=None, ratio=None, mode='use_host_capacity', host_capacity=1):
        super(FabricTorProfileOversubscription, self).__init__()
        self._parent = parent
        self._set_property('ratio', ratio)
        self._set_property('mode', mode)
        self._set_property('host_capacity', host_capacity)

    @property
    def ratio(self):
        # type: () -> str
        """ratio getter

        TBD

        Returns: str
        """
        return self._get_property('ratio')

    @ratio.setter
    def ratio(self, value):
        """ratio setter

        TBD

        value: str
        """
        self._set_property('ratio', value)

    @property
    def mode(self):
        # type: () -> Union[Literal["use_fabric_host_links"], Literal["use_host_capacity"]]
        """mode getter

        TBD

        Returns: Union[Literal["use_fabric_host_links"], Literal["use_host_capacity"]]
        """
        return self._get_property('mode')

    @mode.setter
    def mode(self, value):
        """mode setter

        TBD

        value: Union[Literal["use_fabric_host_links"], Literal["use_host_capacity"]]
        """
        self._set_property('mode', value)

    @property
    def host_capacity(self):
        # type: () -> int
        """host_capacity getter

        TBD

        Returns: int
        """
        return self._get_property('host_capacity')

    @host_capacity.setter
    def host_capacity(self, value):
        """host_capacity setter

        TBD

        value: int
        """
        self._set_property('host_capacity', value)


class FabricTorProfileIter(OpenApiIter):
    __slots__ = ('_parent', '_choice')

    _GETITEM_RETURNS_CHOICE_OBJECT = False

    def __init__(self, parent=None, choice=None):
        super(FabricTorProfileIter, self).__init__()
        self._parent = parent
        self._choice = choice

    def __getitem__(self, key):
        # type: (str) -> Union[FabricTorProfile]
        return self._getitem(key)

    def __iter__(self):
        # type: () -> FabricTorProfileIter
        return self._iter()

    def __next__(self):
        # type: () -> FabricTorProfile
        return self._next()

    def next(self):
        # type: () -> FabricTorProfile
        return self._next()

    def torprofile(self, name=None, tor_mode=None, uplink_ecmp_mode=None, qos_profile_name=None, annotations=None):
        # type: (str,Union[Literal["layer2"], Literal["layer3"]],Union[Literal["hash_3_tuple"], Literal["hash_5_tuple"], Literal["random_spray"]],str,str) -> FabricTorProfileIter
        """Factory method that creates an instance of the FabricTorProfile class

        TBD

        Returns: FabricTorProfileIter
        """
        item = FabricTorProfile(parent=self._parent, name=name, tor_mode=tor_mode, uplink_ecmp_mode=uplink_ecmp_mode, qos_profile_name=qos_profile_name, annotations=annotations)
        self._add(item)
        return self

    def add(self, name=None, tor_mode=None, uplink_ecmp_mode=None, qos_profile_name=None, annotations=None):
        # type: (str,Union[Literal["layer2"], Literal["layer3"]],Union[Literal["hash_3_tuple"], Literal["hash_5_tuple"], Literal["random_spray"]],str,str) -> FabricTorProfile
        """Add method that creates and returns an instance of the FabricTorProfile class

        TBD

        Returns: FabricTorProfile
        """
        item = FabricTorProfile(parent=self._parent, name=name, tor_mode=tor_mode, uplink_ecmp_mode=uplink_ecmp_mode, qos_profile_name=qos_profile_name, annotations=annotations)
        self._add(item)
        return item


class FabricQosProfile(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'name': {'type': str},
        'ingress_admission': {'type': 'FabricQosProfileIngressAdmission'},
        'scheduler': {'type': 'FabricQosProfileScheduler'},
        'packet_classification': {'type': 'FabricQosProfilePacketClassification'},
        'wred': {'type': 'FabricQosProfileWred'},
        'pfc': {'type': 'FabricQosProfilePfc'},
        'annotations': {'type': str},
    } # type: Dict[str, str]

    _REQUIRED = ('name',) # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None, name=None, annotations=None):
        super(FabricQosProfile, self).__init__()
        self._parent = parent
        self._set_property('name', name)
        self._set_property('annotations', annotations)

    @property
    def name(self):
        # type: () -> str
        """name getter

        TBD

        Returns: str
        """
        return self._get_property('name')

    @name.setter
    def name(self, value):
        """name setter

        TBD

        value: str
        """
        self._set_property('name', value)

    @property
    def ingress_admission(self):
        # type: () -> FabricQosProfileIngressAdmission
        """ingress_admission getter

        

        Returns: FabricQosProfileIngressAdmission
        """
        return self._get_property('ingress_admission', FabricQosProfileIngressAdmission)

    @property
    def scheduler(self):
        # type: () -> FabricQosProfileScheduler
        """scheduler getter

        

        Returns: FabricQosProfileScheduler
        """
        return self._get_property('scheduler', FabricQosProfileScheduler)

    @property
    def packet_classification(self):
        # type: () -> FabricQosProfilePacketClassification
        """packet_classification getter

        

        Returns: FabricQosProfilePacketClassification
        """
        return self._get_property('packet_classification', FabricQosProfilePacketClassification)

    @property
    def wred(self):
        # type: () -> FabricQosProfileWred
        """wred getter

        WRED (weighted random early detection) configurationWRED (weighted random early detection) configuration

        Returns: FabricQosProfileWred
        """
        return self._get_property('wred', FabricQosProfileWred)

    @property
    def pfc(self):
        # type: () -> FabricQosProfilePfc
        """pfc getter

        PFC (Priority based flow control) configurationPFC (Priority based flow control) configuration

        Returns: FabricQosProfilePfc
        """
        return self._get_property('pfc', FabricQosProfilePfc)

    @property
    def annotations(self):
        # type: () -> str
        """annotations getter

        TBD

        Returns: str
        """
        return self._get_property('annotations')

    @annotations.setter
    def annotations(self, value):
        """annotations setter

        TBD

        value: str
        """
        self._set_property('annotations', value)


class FabricQosProfileIngressAdmission(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'reserved_buffer_bytes': {'type': int},
        'shared_buffer_bytes': {'type': int},
        'priority_list': {
            'type': list,
            'itemtype': str,
        },
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS = {
        'reserved_buffer_bytes': 0,
        'shared_buffer_bytes': 0,
    } # type: Dict[str, Union(type)]

    def __init__(self, parent=None, reserved_buffer_bytes=0, shared_buffer_bytes=0, priority_list=None):
        super(FabricQosProfileIngressAdmission, self).__init__()
        self._parent = parent
        self._set_property('reserved_buffer_bytes', reserved_buffer_bytes)
        self._set_property('shared_buffer_bytes', shared_buffer_bytes)
        self._set_property('priority_list', priority_list)

    @property
    def reserved_buffer_bytes(self):
        # type: () -> int
        """reserved_buffer_bytes getter

        Buffer space (in bytes) reserved for each port that this Qos profile applies to

        Returns: int
        """
        return self._get_property('reserved_buffer_bytes')

    @reserved_buffer_bytes.setter
    def reserved_buffer_bytes(self, value):
        """reserved_buffer_bytes setter

        Buffer space (in bytes) reserved for each port that this Qos profile applies to

        value: int
        """
        self._set_property('reserved_buffer_bytes', value)

    @property
    def shared_buffer_bytes(self):
        # type: () -> int
        """shared_buffer_bytes getter

        Amount of shared buffer space (in bytes) available

        Returns: int
        """
        return self._get_property('shared_buffer_bytes')

    @shared_buffer_bytes.setter
    def shared_buffer_bytes(self, value):
        """shared_buffer_bytes setter

        Amount of shared buffer space (in bytes) available

        value: int
        """
        self._set_property('shared_buffer_bytes', value)

    @property
    def priority_list(self):
        # type: () -> List[str]
        """priority_list getter

        List of priorities for which the buffer sizes should be applied

        Returns: List[str]
        """
        return self._get_property('priority_list')

    @priority_list.setter
    def priority_list(self, value):
        """priority_list setter

        List of priorities for which the buffer sizes should be applied

        value: List[str]
        """
        self._set_property('priority_list', value)


class FabricQosProfileScheduler(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'scheduler_mode': {
            'type': str,
            'enum': [
                'strict_priority',
                'weighted_round_robin',
            ],
        },
        'weight_list': {
            'type': list,
            'itemtype': int,
        },
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    STRICT_PRIORITY = 'strict_priority' # type: str
    WEIGHTED_ROUND_ROBIN = 'weighted_round_robin' # type: str

    def __init__(self, parent=None, scheduler_mode=None, weight_list=None):
        super(FabricQosProfileScheduler, self).__init__()
        self._parent = parent
        self._set_property('scheduler_mode', scheduler_mode)
        self._set_property('weight_list', weight_list)

    @property
    def scheduler_mode(self):
        # type: () -> Union[Literal["strict_priority"], Literal["weighted_round_robin"]]
        """scheduler_mode getter

        The queue scheduling discipline 

        Returns: Union[Literal["strict_priority"], Literal["weighted_round_robin"]]
        """
        return self._get_property('scheduler_mode')

    @scheduler_mode.setter
    def scheduler_mode(self, value):
        """scheduler_mode setter

        The queue scheduling discipline 

        value: Union[Literal["strict_priority"], Literal["weighted_round_robin"]]
        """
        self._set_property('scheduler_mode', value)

    @property
    def weight_list(self):
        # type: () -> List[int]
        """weight_list getter

        A list of egress queue weights for weighted round robin scheduler mode

        Returns: List[int]
        """
        return self._get_property('weight_list')

    @weight_list.setter
    def weight_list(self, value):
        """weight_list setter

        A list of egress queue weights for weighted round robin scheduler mode

        value: List[int]
        """
        self._set_property('weight_list', value)


class FabricQosProfilePacketClassification(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'map_dscp_to_traffic_class': {'type': 'FabricQosProfilePacketClassificationMap'},
        'map_traffic_class_to_queue': {'type': 'FabricQosProfilePacketClassificationMap'},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None):
        super(FabricQosProfilePacketClassification, self).__init__()
        self._parent = parent

    @property
    def map_dscp_to_traffic_class(self):
        # type: () -> FabricQosProfilePacketClassificationMap
        """map_dscp_to_traffic_class getter

        

        Returns: FabricQosProfilePacketClassificationMap
        """
        return self._get_property('map_dscp_to_traffic_class', FabricQosProfilePacketClassificationMap)

    @property
    def map_traffic_class_to_queue(self):
        # type: () -> FabricQosProfilePacketClassificationMap
        """map_traffic_class_to_queue getter

        

        Returns: FabricQosProfilePacketClassificationMap
        """
        return self._get_property('map_traffic_class_to_queue', FabricQosProfilePacketClassificationMap)


class FabricQosProfilePacketClassificationMap(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {} # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None):
        super(FabricQosProfilePacketClassificationMap, self).__init__()
        self._parent = parent


class FabricQosProfileWred(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'queue_list': {
            'type': list,
            'itemtype': int,
        },
        'ecn_marking_enabled': {'type': bool},
        'min_threshold_bytes': {'type': int},
        'max_threshold_bytes': {'type': int},
        'max_probability_percent': {'type': int},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS = {
        'ecn_marking_enabled': False,
        'min_threshold_bytes': 1,
        'max_threshold_bytes': 2,
        'max_probability_percent': 100,
    } # type: Dict[str, Union(type)]

    def __init__(self, parent=None, queue_list=None, ecn_marking_enabled=False, min_threshold_bytes=1, max_threshold_bytes=2, max_probability_percent=100):
        super(FabricQosProfileWred, self).__init__()
        self._parent = parent
        self._set_property('queue_list', queue_list)
        self._set_property('ecn_marking_enabled', ecn_marking_enabled)
        self._set_property('min_threshold_bytes', min_threshold_bytes)
        self._set_property('max_threshold_bytes', max_threshold_bytes)
        self._set_property('max_probability_percent', max_probability_percent)

    @property
    def queue_list(self):
        # type: () -> List[int]
        """queue_list getter

        List of queues for which WRED is enabled

        Returns: List[int]
        """
        return self._get_property('queue_list')

    @queue_list.setter
    def queue_list(self, value):
        """queue_list setter

        List of queues for which WRED is enabled

        value: List[int]
        """
        self._set_property('queue_list', value)

    @property
    def ecn_marking_enabled(self):
        # type: () -> bool
        """ecn_marking_enabled getter

        TBD

        Returns: bool
        """
        return self._get_property('ecn_marking_enabled')

    @ecn_marking_enabled.setter
    def ecn_marking_enabled(self, value):
        """ecn_marking_enabled setter

        TBD

        value: bool
        """
        self._set_property('ecn_marking_enabled', value)

    @property
    def min_threshold_bytes(self):
        # type: () -> int
        """min_threshold_bytes getter

        Egress queue threshold beyond which packets will be droppes or marked

        Returns: int
        """
        return self._get_property('min_threshold_bytes')

    @min_threshold_bytes.setter
    def min_threshold_bytes(self, value):
        """min_threshold_bytes setter

        Egress queue threshold beyond which packets will be droppes or marked

        value: int
        """
        self._set_property('min_threshold_bytes', value)

    @property
    def max_threshold_bytes(self):
        # type: () -> int
        """max_threshold_bytes getter

        Egress queue threshold beyond which packets will be droppes or marked

        Returns: int
        """
        return self._get_property('max_threshold_bytes')

    @max_threshold_bytes.setter
    def max_threshold_bytes(self, value):
        """max_threshold_bytes setter

        Egress queue threshold beyond which packets will be droppes or marked

        value: int
        """
        self._set_property('max_threshold_bytes', value)

    @property
    def max_probability_percent(self):
        # type: () -> int
        """max_probability_percent getter

        Probability of dropping/marking packets at max threshold

        Returns: int
        """
        return self._get_property('max_probability_percent')

    @max_probability_percent.setter
    def max_probability_percent(self, value):
        """max_probability_percent setter

        Probability of dropping/marking packets at max threshold

        value: int
        """
        self._set_property('max_probability_percent', value)


class FabricQosProfilePfc(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'enabled': {'type': bool},
        'priority_list': {
            'type': list,
            'itemtype': int,
        },
        'headroom_buffer_bytes': {'type': int},
        'resume_threshold_bytes': {'type': int},
    } # type: Dict[str, str]

    _REQUIRED = ('priority_list', 'headroom_buffer_bytes', 'resume_threshold_bytes') # type: tuple(str)

    _DEFAULTS = {
        'enabled': False,
    } # type: Dict[str, Union(type)]

    def __init__(self, parent=None, enabled=False, priority_list=None, headroom_buffer_bytes=None, resume_threshold_bytes=None):
        super(FabricQosProfilePfc, self).__init__()
        self._parent = parent
        self._set_property('enabled', enabled)
        self._set_property('priority_list', priority_list)
        self._set_property('headroom_buffer_bytes', headroom_buffer_bytes)
        self._set_property('resume_threshold_bytes', resume_threshold_bytes)

    @property
    def enabled(self):
        # type: () -> bool
        """enabled getter

        TBD

        Returns: bool
        """
        return self._get_property('enabled')

    @enabled.setter
    def enabled(self, value):
        """enabled setter

        TBD

        value: bool
        """
        self._set_property('enabled', value)

    @property
    def priority_list(self):
        # type: () -> List[int]
        """priority_list getter

        TBD

        Returns: List[int]
        """
        return self._get_property('priority_list')

    @priority_list.setter
    def priority_list(self, value):
        """priority_list setter

        TBD

        value: List[int]
        """
        self._set_property('priority_list', value)

    @property
    def headroom_buffer_bytes(self):
        # type: () -> int
        """headroom_buffer_bytes getter

        Headroom buffer per PFC priority

        Returns: int
        """
        return self._get_property('headroom_buffer_bytes')

    @headroom_buffer_bytes.setter
    def headroom_buffer_bytes(self, value):
        """headroom_buffer_bytes setter

        Headroom buffer per PFC priority

        value: int
        """
        self._set_property('headroom_buffer_bytes', value)

    @property
    def resume_threshold_bytes(self):
        # type: () -> int
        """resume_threshold_bytes getter

        Space required before sending Resume frame

        Returns: int
        """
        return self._get_property('resume_threshold_bytes')

    @resume_threshold_bytes.setter
    def resume_threshold_bytes(self, value):
        """resume_threshold_bytes setter

        Space required before sending Resume frame

        value: int
        """
        self._set_property('resume_threshold_bytes', value)


class FabricQosProfileIter(OpenApiIter):
    __slots__ = ('_parent', '_choice')

    _GETITEM_RETURNS_CHOICE_OBJECT = False

    def __init__(self, parent=None, choice=None):
        super(FabricQosProfileIter, self).__init__()
        self._parent = parent
        self._choice = choice

    def __getitem__(self, key):
        # type: (str) -> Union[FabricQosProfile]
        return self._getitem(key)

    def __iter__(self):
        # type: () -> FabricQosProfileIter
        return self._iter()

    def __next__(self):
        # type: () -> FabricQosProfile
        return self._next()

    def next(self):
        # type: () -> FabricQosProfile
        return self._next()

    def qosprofile(self, name=None, annotations=None):
        # type: (str,str) -> FabricQosProfileIter
        """Factory method that creates an instance of the FabricQosProfile class

        TBD

        Returns: FabricQosProfileIter
        """
        item = FabricQosProfile(parent=self._parent, name=name, annotations=annotations)
        self._add(item)
        return self

    def add(self, name=None, annotations=None):
        # type: (str,str) -> FabricQosProfile
        """Add method that creates and returns an instance of the FabricQosProfile class

        TBD

        Returns: FabricQosProfile
        """
        item = FabricQosProfile(parent=self._parent, name=name, annotations=annotations)
        self._add(item)
        return item


class Dataflow(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'host_management': {'type': 'DataflowHostManagementIter'},
        'workload': {'type': 'DataflowWorkloadItemIter'},
        'flow_profiles': {'type': 'DataflowFlowProfileIter'},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None):
        super(Dataflow, self).__init__()
        self._parent = parent

    @property
    def host_management(self):
        # type: () -> DataflowHostManagementIter
        """host_management getter

        TBD

        Returns: DataflowHostManagementIter
        """
        return self._get_property('host_management', DataflowHostManagementIter, self._parent, self._choice)

    @property
    def workload(self):
        # type: () -> DataflowWorkloadItemIter
        """workload getter

        The workload items making up the dataflow

        Returns: DataflowWorkloadItemIter
        """
        return self._get_property('workload', DataflowWorkloadItemIter, self._parent, self._choice)

    @property
    def flow_profiles(self):
        # type: () -> DataflowFlowProfileIter
        """flow_profiles getter

        foo

        Returns: DataflowFlowProfileIter
        """
        return self._get_property('flow_profiles', DataflowFlowProfileIter, self._parent, self._choice)


class DataflowHostManagement(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'host_name': {'type': str},
        'nic_rx_buffer': {'type': int},
        'nic_tx_buffer': {'type': int},
        'nic_speed': {'type': int},
        'management_address': {'type': str},
        'nic_name': {'type': str},
    } # type: Dict[str, str]

    _REQUIRED = ('host_name',) # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None, host_name=None, nic_rx_buffer=None, nic_tx_buffer=None, nic_speed=None, management_address=None, nic_name=None):
        super(DataflowHostManagement, self).__init__()
        self._parent = parent
        self._set_property('host_name', host_name)
        self._set_property('nic_rx_buffer', nic_rx_buffer)
        self._set_property('nic_tx_buffer', nic_tx_buffer)
        self._set_property('nic_speed', nic_speed)
        self._set_property('management_address', management_address)
        self._set_property('nic_name', nic_name)

    @property
    def host_name(self):
        # type: () -> str
        """host_name getter

        TBD. . x-constraint:. - #components/schemas/Host/properties/name. 

        Returns: str
        """
        return self._get_property('host_name')

    @host_name.setter
    def host_name(self, value):
        """host_name setter

        TBD. . x-constraint:. - #components/schemas/Host/properties/name. 

        value: str
        """
        self._set_property('host_name', value)

    @property
    def nic_rx_buffer(self):
        # type: () -> int
        """nic_rx_buffer getter

        RX buffer size in bytes

        Returns: int
        """
        return self._get_property('nic_rx_buffer')

    @nic_rx_buffer.setter
    def nic_rx_buffer(self, value):
        """nic_rx_buffer setter

        RX buffer size in bytes

        value: int
        """
        self._set_property('nic_rx_buffer', value)

    @property
    def nic_tx_buffer(self):
        # type: () -> int
        """nic_tx_buffer getter

        TX buffer size in bytes

        Returns: int
        """
        return self._get_property('nic_tx_buffer')

    @nic_tx_buffer.setter
    def nic_tx_buffer(self, value):
        """nic_tx_buffer setter

        TX buffer size in bytes

        value: int
        """
        self._set_property('nic_tx_buffer', value)

    @property
    def nic_speed(self):
        # type: () -> int
        """nic_speed getter

        configured link speed Mbps (e.g. 100000 for 100G)

        Returns: int
        """
        return self._get_property('nic_speed')

    @nic_speed.setter
    def nic_speed(self, value):
        """nic_speed setter

        configured link speed Mbps (e.g. 100000 for 100G)

        value: int
        """
        self._set_property('nic_speed', value)

    @property
    def management_address(self):
        # type: () -> str
        """management_address getter

        Hostname or address of management interface of a server running dataflow traffic

        Returns: str
        """
        return self._get_property('management_address')

    @management_address.setter
    def management_address(self, value):
        """management_address setter

        Hostname or address of management interface of a server running dataflow traffic

        value: str
        """
        self._set_property('management_address', value)

    @property
    def nic_name(self):
        # type: () -> str
        """nic_name getter

        unique idenfier for the network interface card (nic), e.g. "eth1"

        Returns: str
        """
        return self._get_property('nic_name')

    @nic_name.setter
    def nic_name(self, value):
        """nic_name setter

        unique idenfier for the network interface card (nic), e.g. "eth1"

        value: str
        """
        self._set_property('nic_name', value)


class DataflowHostManagementIter(OpenApiIter):
    __slots__ = ('_parent', '_choice')

    _GETITEM_RETURNS_CHOICE_OBJECT = False

    def __init__(self, parent=None, choice=None):
        super(DataflowHostManagementIter, self).__init__()
        self._parent = parent
        self._choice = choice

    def __getitem__(self, key):
        # type: (str) -> Union[DataflowHostManagement]
        return self._getitem(key)

    def __iter__(self):
        # type: () -> DataflowHostManagementIter
        return self._iter()

    def __next__(self):
        # type: () -> DataflowHostManagement
        return self._next()

    def next(self):
        # type: () -> DataflowHostManagement
        return self._next()

    def hostmanagement(self, host_name=None, nic_rx_buffer=None, nic_tx_buffer=None, nic_speed=None, management_address=None, nic_name=None):
        # type: (str,int,int,int,str,str) -> DataflowHostManagementIter
        """Factory method that creates an instance of the DataflowHostManagement class

        auxillary host information needed to run dataflow experiments

        Returns: DataflowHostManagementIter
        """
        item = DataflowHostManagement(parent=self._parent, host_name=host_name, nic_rx_buffer=nic_rx_buffer, nic_tx_buffer=nic_tx_buffer, nic_speed=nic_speed, management_address=management_address, nic_name=nic_name)
        self._add(item)
        return self

    def add(self, host_name=None, nic_rx_buffer=None, nic_tx_buffer=None, nic_speed=None, management_address=None, nic_name=None):
        # type: (str,int,int,int,str,str) -> DataflowHostManagement
        """Add method that creates and returns an instance of the DataflowHostManagement class

        auxillary host information needed to run dataflow experiments

        Returns: DataflowHostManagement
        """
        item = DataflowHostManagement(parent=self._parent, host_name=host_name, nic_rx_buffer=nic_rx_buffer, nic_tx_buffer=nic_tx_buffer, nic_speed=nic_speed, management_address=management_address, nic_name=nic_name)
        self._add(item)
        return item


class DataflowWorkloadItem(OpenApiObject):
    __slots__ = ('_parent','_choice')

    _TYPES = {
        'name': {'type': str},
        'choice': {
            'type': str,
            'enum': [
                'scatter',
                'gather',
                'all_reduce',
                'loop',
                'compute',
                'broadcast',
                'all_to_all',
            ],
        },
        'scatter': {'type': 'DataflowScatterWorkload'},
        'gather': {'type': 'DataflowGatherWorkload'},
        'loop': {'type': 'DataflowLoopWorkload'},
        'compute': {'type': 'DataflowComputeWorkload'},
        'all_reduce': {'type': 'DataflowAllReduceWorkload'},
        'broadcast': {'type': 'DataflowBroadcastWorkload'},
        'all_to_all': {'type': 'DataflowAlltoallWorkload'},
    } # type: Dict[str, str]

    _REQUIRED = ('name', 'choice') # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    SCATTER = 'scatter' # type: str
    GATHER = 'gather' # type: str
    ALL_REDUCE = 'all_reduce' # type: str
    LOOP = 'loop' # type: str
    COMPUTE = 'compute' # type: str
    BROADCAST = 'broadcast' # type: str
    ALL_TO_ALL = 'all_to_all' # type: str

    def __init__(self, parent=None, choice=None, name=None):
        super(DataflowWorkloadItem, self).__init__()
        self._parent = parent
        self._set_property('name', name)
        if 'choice' in self._DEFAULTS and choice is None:
            getattr(self, self._DEFAULTS['choice'])
        else:
            self.choice = choice

    @property
    def scatter(self):
        # type: () -> DataflowScatterWorkload
        """Factory property that returns an instance of the DataflowScatterWorkload class

        TBD

        Returns: DataflowScatterWorkload
        """
        return self._get_property('scatter', DataflowScatterWorkload, self, 'scatter')

    @property
    def gather(self):
        # type: () -> DataflowGatherWorkload
        """Factory property that returns an instance of the DataflowGatherWorkload class

        TBD

        Returns: DataflowGatherWorkload
        """
        return self._get_property('gather', DataflowGatherWorkload, self, 'gather')

    @property
    def all_reduce(self):
        # type: () -> DataflowAllReduceWorkload
        """Factory property that returns an instance of the DataflowAllReduceWorkload class

        TBD

        Returns: DataflowAllReduceWorkload
        """
        return self._get_property('all_reduce', DataflowAllReduceWorkload, self, 'all_reduce')

    @property
    def loop(self):
        # type: () -> DataflowLoopWorkload
        """Factory property that returns an instance of the DataflowLoopWorkload class

        TBD

        Returns: DataflowLoopWorkload
        """
        return self._get_property('loop', DataflowLoopWorkload, self, 'loop')

    @property
    def compute(self):
        # type: () -> DataflowComputeWorkload
        """Factory property that returns an instance of the DataflowComputeWorkload class

        TBD

        Returns: DataflowComputeWorkload
        """
        return self._get_property('compute', DataflowComputeWorkload, self, 'compute')

    @property
    def broadcast(self):
        # type: () -> DataflowBroadcastWorkload
        """Factory property that returns an instance of the DataflowBroadcastWorkload class

        TBD

        Returns: DataflowBroadcastWorkload
        """
        return self._get_property('broadcast', DataflowBroadcastWorkload, self, 'broadcast')

    @property
    def all_to_all(self):
        # type: () -> DataflowAlltoallWorkload
        """Factory property that returns an instance of the DataflowAlltoallWorkload class

        creates full-mesh flows between all nodes

        Returns: DataflowAlltoallWorkload
        """
        return self._get_property('all_to_all', DataflowAlltoallWorkload, self, 'all_to_all')

    @property
    def name(self):
        # type: () -> str
        """name getter

        uniquely identifies the workload item

        Returns: str
        """
        return self._get_property('name')

    @name.setter
    def name(self, value):
        """name setter

        uniquely identifies the workload item

        value: str
        """
        self._set_property('name', value)

    @property
    def choice(self):
        # type: () -> Union[Literal["all_reduce"], Literal["all_to_all"], Literal["broadcast"], Literal["compute"], Literal["gather"], Literal["loop"], Literal["scatter"]]
        """choice getter

        The type of workflow item

        Returns: Union[Literal["all_reduce"], Literal["all_to_all"], Literal["broadcast"], Literal["compute"], Literal["gather"], Literal["loop"], Literal["scatter"]]
        """
        return self._get_property('choice')

    @choice.setter
    def choice(self, value):
        """choice setter

        The type of workflow item

        value: Union[Literal["all_reduce"], Literal["all_to_all"], Literal["broadcast"], Literal["compute"], Literal["gather"], Literal["loop"], Literal["scatter"]]
        """
        self._set_property('choice', value)


class DataflowScatterWorkload(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'sources': {
            'type': list,
            'itemtype': str,
        },
        'destinations': {
            'type': list,
            'itemtype': str,
        },
        'flow_profile_name': {'type': str},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None, sources=None, destinations=None, flow_profile_name=None):
        super(DataflowScatterWorkload, self).__init__()
        self._parent = parent
        self._set_property('sources', sources)
        self._set_property('destinations', destinations)
        self._set_property('flow_profile_name', flow_profile_name)

    @property
    def sources(self):
        # type: () -> List[str]
        """sources getter

        list of host names, indicating the originator of the data

        Returns: List[str]
        """
        return self._get_property('sources')

    @sources.setter
    def sources(self, value):
        """sources setter

        list of host names, indicating the originator of the data

        value: List[str]
        """
        self._set_property('sources', value)

    @property
    def destinations(self):
        # type: () -> List[str]
        """destinations getter

        list of host names, indicating the destination of the data

        Returns: List[str]
        """
        return self._get_property('destinations')

    @destinations.setter
    def destinations(self, value):
        """destinations setter

        list of host names, indicating the destination of the data

        value: List[str]
        """
        self._set_property('destinations', value)

    @property
    def flow_profile_name(self):
        # type: () -> str
        """flow_profile_name getter

        flow profile reference

        Returns: str
        """
        return self._get_property('flow_profile_name')

    @flow_profile_name.setter
    def flow_profile_name(self, value):
        """flow_profile_name setter

        flow profile reference

        value: str
        """
        self._set_property('flow_profile_name', value)


class DataflowGatherWorkload(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'sources': {
            'type': list,
            'itemtype': str,
        },
        'destinations': {
            'type': list,
            'itemtype': str,
        },
        'flow_profile_name': {'type': str},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None, sources=None, destinations=None, flow_profile_name=None):
        super(DataflowGatherWorkload, self).__init__()
        self._parent = parent
        self._set_property('sources', sources)
        self._set_property('destinations', destinations)
        self._set_property('flow_profile_name', flow_profile_name)

    @property
    def sources(self):
        # type: () -> List[str]
        """sources getter

        list of host names, indicating the originator of the data

        Returns: List[str]
        """
        return self._get_property('sources')

    @sources.setter
    def sources(self, value):
        """sources setter

        list of host names, indicating the originator of the data

        value: List[str]
        """
        self._set_property('sources', value)

    @property
    def destinations(self):
        # type: () -> List[str]
        """destinations getter

        list of host names, indicating the destination of the data

        Returns: List[str]
        """
        return self._get_property('destinations')

    @destinations.setter
    def destinations(self, value):
        """destinations setter

        list of host names, indicating the destination of the data

        value: List[str]
        """
        self._set_property('destinations', value)

    @property
    def flow_profile_name(self):
        # type: () -> str
        """flow_profile_name getter

        flow profile reference

        Returns: str
        """
        return self._get_property('flow_profile_name')

    @flow_profile_name.setter
    def flow_profile_name(self, value):
        """flow_profile_name setter

        flow profile reference

        value: str
        """
        self._set_property('flow_profile_name', value)


class DataflowLoopWorkload(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'iterations': {'type': int},
        'children': {'type': 'DataflowWorkloadItemIter'},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None, iterations=None):
        super(DataflowLoopWorkload, self).__init__()
        self._parent = parent
        self._set_property('iterations', iterations)

    @property
    def iterations(self):
        # type: () -> int
        """iterations getter

        number of iterations in the loop

        Returns: int
        """
        return self._get_property('iterations')

    @iterations.setter
    def iterations(self, value):
        """iterations setter

        number of iterations in the loop

        value: int
        """
        self._set_property('iterations', value)

    @property
    def children(self):
        # type: () -> DataflowWorkloadItemIter
        """children getter

        list of workload items that are executed in this loop

        Returns: DataflowWorkloadItemIter
        """
        return self._get_property('children', DataflowWorkloadItemIter, self._parent, self._choice)


class DataflowWorkloadItemIter(OpenApiIter):
    __slots__ = ('_parent', '_choice')

    _GETITEM_RETURNS_CHOICE_OBJECT = False

    def __init__(self, parent=None, choice=None):
        super(DataflowWorkloadItemIter, self).__init__()
        self._parent = parent
        self._choice = choice

    def __getitem__(self, key):
        # type: (str) -> Union[DataflowAllReduceWorkload, DataflowAlltoallWorkload, DataflowBroadcastWorkload, DataflowComputeWorkload, DataflowGatherWorkload, DataflowLoopWorkload, DataflowScatterWorkload, DataflowWorkloadItem]
        return self._getitem(key)

    def __iter__(self):
        # type: () -> DataflowWorkloadItemIter
        return self._iter()

    def __next__(self):
        # type: () -> DataflowWorkloadItem
        return self._next()

    def next(self):
        # type: () -> DataflowWorkloadItem
        return self._next()

    def workloaditem(self, name=None):
        # type: (str) -> DataflowWorkloadItemIter
        """Factory method that creates an instance of the DataflowWorkloadItem class

        TBD

        Returns: DataflowWorkloadItemIter
        """
        item = DataflowWorkloadItem(parent=self._parent, choice=self._choice, name=name)
        self._add(item)
        return self

    def add(self, name=None):
        # type: (str) -> DataflowWorkloadItem
        """Add method that creates and returns an instance of the DataflowWorkloadItem class

        TBD

        Returns: DataflowWorkloadItem
        """
        item = DataflowWorkloadItem(parent=self._parent, choice=self._choice, name=name)
        self._add(item)
        return item


class DataflowComputeWorkload(OpenApiObject):
    __slots__ = ('_parent','_choice')

    _TYPES = {
        'nodes': {
            'type': list,
            'itemtype': str,
        },
        'choice': {
            'type': str,
            'enum': [
                'simulated',
            ],
        },
        'simulated': {'type': 'DataflowSimulatedComputeWorkload'},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    SIMULATED = 'simulated' # type: str

    def __init__(self, parent=None, choice=None, nodes=None):
        super(DataflowComputeWorkload, self).__init__()
        self._parent = parent
        self._set_property('nodes', nodes)
        if 'choice' in self._DEFAULTS and choice is None:
            getattr(self, self._DEFAULTS['choice'])
        else:
            self.choice = choice

    @property
    def simulated(self):
        # type: () -> DataflowSimulatedComputeWorkload
        """Factory property that returns an instance of the DataflowSimulatedComputeWorkload class

        TBD

        Returns: DataflowSimulatedComputeWorkload
        """
        return self._get_property('simulated', DataflowSimulatedComputeWorkload, self, 'simulated')

    @property
    def nodes(self):
        # type: () -> List[str]
        """nodes getter

        TBD

        Returns: List[str]
        """
        return self._get_property('nodes')

    @nodes.setter
    def nodes(self, value):
        """nodes setter

        TBD

        value: List[str]
        """
        self._set_property('nodes', value)

    @property
    def choice(self):
        # type: () -> Union[Literal["simulated"]]
        """choice getter

        type of compute

        Returns: Union[Literal["simulated"]]
        """
        return self._get_property('choice')

    @choice.setter
    def choice(self, value):
        """choice setter

        type of compute

        value: Union[Literal["simulated"]]
        """
        self._set_property('choice', value)


class DataflowSimulatedComputeWorkload(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'duration': {'type': float},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None, duration=None):
        super(DataflowSimulatedComputeWorkload, self).__init__()
        self._parent = parent
        self._set_property('duration', duration)

    @property
    def duration(self):
        # type: () -> float
        """duration getter

        duration of the simulated compute workload in seconds

        Returns: float
        """
        return self._get_property('duration')

    @duration.setter
    def duration(self, value):
        """duration setter

        duration of the simulated compute workload in seconds

        value: float
        """
        self._set_property('duration', value)


class DataflowAllReduceWorkload(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'nodes': {
            'type': list,
            'itemtype': str,
        },
        'flow_profile_name': {'type': str},
        'type': {
            'type': str,
            'enum': [
                'butterfly',
                'ring',
                'tree',
            ],
        },
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS = {
        'type': 'ring',
    } # type: Dict[str, Union(type)]

    BUTTERFLY = 'butterfly' # type: str
    RING = 'ring' # type: str
    TREE = 'tree' # type: str

    def __init__(self, parent=None, nodes=None, flow_profile_name=None, type='ring'):
        super(DataflowAllReduceWorkload, self).__init__()
        self._parent = parent
        self._set_property('nodes', nodes)
        self._set_property('flow_profile_name', flow_profile_name)
        self._set_property('type', type)

    @property
    def nodes(self):
        # type: () -> List[str]
        """nodes getter

        TBD

        Returns: List[str]
        """
        return self._get_property('nodes')

    @nodes.setter
    def nodes(self, value):
        """nodes setter

        TBD

        value: List[str]
        """
        self._set_property('nodes', value)

    @property
    def flow_profile_name(self):
        # type: () -> str
        """flow_profile_name getter

        flow profile reference

        Returns: str
        """
        return self._get_property('flow_profile_name')

    @flow_profile_name.setter
    def flow_profile_name(self, value):
        """flow_profile_name setter

        flow profile reference

        value: str
        """
        self._set_property('flow_profile_name', value)

    @property
    def type(self):
        # type: () -> Union[Literal["butterfly"], Literal["ring"], Literal["tree"]]
        """type getter

        type of all reduce

        Returns: Union[Literal["butterfly"], Literal["ring"], Literal["tree"]]
        """
        return self._get_property('type')

    @type.setter
    def type(self, value):
        """type setter

        type of all reduce

        value: Union[Literal["butterfly"], Literal["ring"], Literal["tree"]]
        """
        self._set_property('type', value)


class DataflowBroadcastWorkload(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'sources': {
            'type': list,
            'itemtype': str,
        },
        'destinations': {
            'type': list,
            'itemtype': str,
        },
        'flow_profile_name': {'type': str},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None, sources=None, destinations=None, flow_profile_name=None):
        super(DataflowBroadcastWorkload, self).__init__()
        self._parent = parent
        self._set_property('sources', sources)
        self._set_property('destinations', destinations)
        self._set_property('flow_profile_name', flow_profile_name)

    @property
    def sources(self):
        # type: () -> List[str]
        """sources getter

        list of host names, indicating the originator of the data

        Returns: List[str]
        """
        return self._get_property('sources')

    @sources.setter
    def sources(self, value):
        """sources setter

        list of host names, indicating the originator of the data

        value: List[str]
        """
        self._set_property('sources', value)

    @property
    def destinations(self):
        # type: () -> List[str]
        """destinations getter

        list of host names, indicating the destination of the data

        Returns: List[str]
        """
        return self._get_property('destinations')

    @destinations.setter
    def destinations(self, value):
        """destinations setter

        list of host names, indicating the destination of the data

        value: List[str]
        """
        self._set_property('destinations', value)

    @property
    def flow_profile_name(self):
        # type: () -> str
        """flow_profile_name getter

        flow profile reference

        Returns: str
        """
        return self._get_property('flow_profile_name')

    @flow_profile_name.setter
    def flow_profile_name(self, value):
        """flow_profile_name setter

        flow profile reference

        value: str
        """
        self._set_property('flow_profile_name', value)


class DataflowAlltoallWorkload(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'nodes': {
            'type': list,
            'itemtype': str,
        },
        'flow_profile_name': {'type': str},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None, nodes=None, flow_profile_name=None):
        super(DataflowAlltoallWorkload, self).__init__()
        self._parent = parent
        self._set_property('nodes', nodes)
        self._set_property('flow_profile_name', flow_profile_name)

    @property
    def nodes(self):
        # type: () -> List[str]
        """nodes getter

        TBD

        Returns: List[str]
        """
        return self._get_property('nodes')

    @nodes.setter
    def nodes(self, value):
        """nodes setter

        TBD

        value: List[str]
        """
        self._set_property('nodes', value)

    @property
    def flow_profile_name(self):
        # type: () -> str
        """flow_profile_name getter

        flow profile reference

        Returns: str
        """
        return self._get_property('flow_profile_name')

    @flow_profile_name.setter
    def flow_profile_name(self, value):
        """flow_profile_name setter

        flow profile reference

        value: str
        """
        self._set_property('flow_profile_name', value)


class DataflowFlowProfile(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'name': {'type': str},
        'data_size': {'type': int},
        'l2_protocol_choice': {
            'type': str,
            'enum': [
                'ethernet',
            ],
        },
        'ethernet': {'type': 'DataflowFlowProfileEthernet'},
        'l4_protocol_choice': {
            'type': str,
            'enum': [
                'tcp',
                'udp',
            ],
        },
        'ip': {'type': 'DataflowFlowProfileIp'},
        'tcp': {'type': 'DataflowFlowProfileTcp'},
        'udp': {'type': 'DataflowFlowProfileUdp'},
    } # type: Dict[str, str]

    _REQUIRED = ('name', 'data_size') # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    ETHERNET = 'ethernet' # type: str

    TCP = 'tcp' # type: str
    UDP = 'udp' # type: str

    def __init__(self, parent=None, name=None, data_size=None, l2_protocol_choice=None, l4_protocol_choice=None):
        super(DataflowFlowProfile, self).__init__()
        self._parent = parent
        self._set_property('name', name)
        self._set_property('data_size', data_size)
        self._set_property('l2_protocol_choice', l2_protocol_choice)
        self._set_property('l4_protocol_choice', l4_protocol_choice)

    @property
    def name(self):
        # type: () -> str
        """name getter

        TBD

        Returns: str
        """
        return self._get_property('name')

    @name.setter
    def name(self, value):
        """name setter

        TBD

        value: str
        """
        self._set_property('name', value)

    @property
    def data_size(self):
        # type: () -> int
        """data_size getter

        TBD

        Returns: int
        """
        return self._get_property('data_size')

    @data_size.setter
    def data_size(self, value):
        """data_size setter

        TBD

        value: int
        """
        self._set_property('data_size', value)

    @property
    def l2_protocol_choice(self):
        # type: () -> Union[Literal["ethernet"]]
        """l2_protocol_choice getter

        layer2 protocol selection

        Returns: Union[Literal["ethernet"]]
        """
        return self._get_property('l2_protocol_choice')

    @l2_protocol_choice.setter
    def l2_protocol_choice(self, value):
        """l2_protocol_choice setter

        layer2 protocol selection

        value: Union[Literal["ethernet"]]
        """
        self._set_property('l2_protocol_choice', value)

    @property
    def ethernet(self):
        # type: () -> DataflowFlowProfileEthernet
        """ethernet getter

        

        Returns: DataflowFlowProfileEthernet
        """
        return self._get_property('ethernet', DataflowFlowProfileEthernet)

    @property
    def l4_protocol_choice(self):
        # type: () -> Union[Literal["tcp"], Literal["udp"]]
        """l4_protocol_choice getter

        layer4 protocol selection

        Returns: Union[Literal["tcp"], Literal["udp"]]
        """
        return self._get_property('l4_protocol_choice')

    @l4_protocol_choice.setter
    def l4_protocol_choice(self, value):
        """l4_protocol_choice setter

        layer4 protocol selection

        value: Union[Literal["tcp"], Literal["udp"]]
        """
        self._set_property('l4_protocol_choice', value)

    @property
    def ip(self):
        # type: () -> DataflowFlowProfileIp
        """ip getter

        

        Returns: DataflowFlowProfileIp
        """
        return self._get_property('ip', DataflowFlowProfileIp)

    @property
    def tcp(self):
        # type: () -> DataflowFlowProfileTcp
        """tcp getter

        

        Returns: DataflowFlowProfileTcp
        """
        return self._get_property('tcp', DataflowFlowProfileTcp)

    @property
    def udp(self):
        # type: () -> DataflowFlowProfileUdp
        """udp getter

        

        Returns: DataflowFlowProfileUdp
        """
        return self._get_property('udp', DataflowFlowProfileUdp)


class DataflowFlowProfileEthernet(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'mtu': {'type': int},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS = {
        'mtu': 1500,
    } # type: Dict[str, Union(type)]

    def __init__(self, parent=None, mtu=1500):
        super(DataflowFlowProfileEthernet, self).__init__()
        self._parent = parent
        self._set_property('mtu', mtu)

    @property
    def mtu(self):
        # type: () -> int
        """mtu getter

        Maximum Transmission Unit

        Returns: int
        """
        return self._get_property('mtu')

    @mtu.setter
    def mtu(self, value):
        """mtu setter

        Maximum Transmission Unit

        value: int
        """
        self._set_property('mtu', value)


class DataflowFlowProfileIp(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'dscp': {'type': int},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None, dscp=None):
        super(DataflowFlowProfileIp, self).__init__()
        self._parent = parent
        self._set_property('dscp', dscp)

    @property
    def dscp(self):
        # type: () -> int
        """dscp getter

        differentiated services code point

        Returns: int
        """
        return self._get_property('dscp')

    @dscp.setter
    def dscp(self, value):
        """dscp setter

        differentiated services code point

        value: int
        """
        self._set_property('dscp', value)


class DataflowFlowProfileTcp(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'congestion_algorithm': {
            'type': str,
            'enum': [
                'bbr',
                'dctcp',
                'cubic',
                'reno',
            ],
        },
        'initcwnd': {'type': int},
        'send_buf': {'type': int},
        'receive_buf': {'type': int},
        'delayed_ack': {'type': int},
        'selective_ack': {'type': bool},
        'min_rto': {'type': int},
        'mss': {'type': int},
        'ecn': {'type': bool},
        'enable_timestamp': {'type': bool},
        'destination_port': {'type': 'L4PortRange'},
        'source_port': {'type': 'L4PortRange'},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS = {
        'congestion_algorithm': 'cubic',
        'mss': 1500,
    } # type: Dict[str, Union(type)]

    BBR = 'bbr' # type: str
    DCTCP = 'dctcp' # type: str
    CUBIC = 'cubic' # type: str
    RENO = 'reno' # type: str

    def __init__(self, parent=None, congestion_algorithm='cubic', initcwnd=None, send_buf=None, receive_buf=None, delayed_ack=None, selective_ack=None, min_rto=None, mss=1500, ecn=None, enable_timestamp=None):
        super(DataflowFlowProfileTcp, self).__init__()
        self._parent = parent
        self._set_property('congestion_algorithm', congestion_algorithm)
        self._set_property('initcwnd', initcwnd)
        self._set_property('send_buf', send_buf)
        self._set_property('receive_buf', receive_buf)
        self._set_property('delayed_ack', delayed_ack)
        self._set_property('selective_ack', selective_ack)
        self._set_property('min_rto', min_rto)
        self._set_property('mss', mss)
        self._set_property('ecn', ecn)
        self._set_property('enable_timestamp', enable_timestamp)

    @property
    def congestion_algorithm(self):
        # type: () -> Union[Literal["bbr"], Literal["cubic"], Literal["dctcp"], Literal["reno"]]
        """congestion_algorithm getter

        The TCP congestion algorithm:. bbr - Bottleneck Bandwidth and Round-trip propagation time. dctcp - Data center TCP. cubic - cubic window increase function. reno - TCP New Reno

        Returns: Union[Literal["bbr"], Literal["cubic"], Literal["dctcp"], Literal["reno"]]
        """
        return self._get_property('congestion_algorithm')

    @congestion_algorithm.setter
    def congestion_algorithm(self, value):
        """congestion_algorithm setter

        The TCP congestion algorithm:. bbr - Bottleneck Bandwidth and Round-trip propagation time. dctcp - Data center TCP. cubic - cubic window increase function. reno - TCP New Reno

        value: Union[Literal["bbr"], Literal["cubic"], Literal["dctcp"], Literal["reno"]]
        """
        self._set_property('congestion_algorithm', value)

    @property
    def initcwnd(self):
        # type: () -> int
        """initcwnd getter

        initial congestion window

        Returns: int
        """
        return self._get_property('initcwnd')

    @initcwnd.setter
    def initcwnd(self, value):
        """initcwnd setter

        initial congestion window

        value: int
        """
        self._set_property('initcwnd', value)

    @property
    def send_buf(self):
        # type: () -> int
        """send_buf getter

        send buffer size

        Returns: int
        """
        return self._get_property('send_buf')

    @send_buf.setter
    def send_buf(self, value):
        """send_buf setter

        send buffer size

        value: int
        """
        self._set_property('send_buf', value)

    @property
    def receive_buf(self):
        # type: () -> int
        """receive_buf getter

        receive buffer size

        Returns: int
        """
        return self._get_property('receive_buf')

    @receive_buf.setter
    def receive_buf(self, value):
        """receive_buf setter

        receive buffer size

        value: int
        """
        self._set_property('receive_buf', value)

    @property
    def delayed_ack(self):
        # type: () -> int
        """delayed_ack getter

        delayed acknowledgment

        Returns: int
        """
        return self._get_property('delayed_ack')

    @delayed_ack.setter
    def delayed_ack(self, value):
        """delayed_ack setter

        delayed acknowledgment

        value: int
        """
        self._set_property('delayed_ack', value)

    @property
    def selective_ack(self):
        # type: () -> bool
        """selective_ack getter

        selective acknowledgment

        Returns: bool
        """
        return self._get_property('selective_ack')

    @selective_ack.setter
    def selective_ack(self, value):
        """selective_ack setter

        selective acknowledgment

        value: bool
        """
        self._set_property('selective_ack', value)

    @property
    def min_rto(self):
        # type: () -> int
        """min_rto getter

        minimum retransmission timeout

        Returns: int
        """
        return self._get_property('min_rto')

    @min_rto.setter
    def min_rto(self, value):
        """min_rto setter

        minimum retransmission timeout

        value: int
        """
        self._set_property('min_rto', value)

    @property
    def mss(self):
        # type: () -> int
        """mss getter

        Maximum Segment Size

        Returns: int
        """
        return self._get_property('mss')

    @mss.setter
    def mss(self, value):
        """mss setter

        Maximum Segment Size

        value: int
        """
        self._set_property('mss', value)

    @property
    def ecn(self):
        # type: () -> bool
        """ecn getter

        early congestion notification

        Returns: bool
        """
        return self._get_property('ecn')

    @ecn.setter
    def ecn(self, value):
        """ecn setter

        early congestion notification

        value: bool
        """
        self._set_property('ecn', value)

    @property
    def enable_timestamp(self):
        # type: () -> bool
        """enable_timestamp getter

        enable tcp timestamping

        Returns: bool
        """
        return self._get_property('enable_timestamp')

    @enable_timestamp.setter
    def enable_timestamp(self, value):
        """enable_timestamp setter

        enable tcp timestamping

        value: bool
        """
        self._set_property('enable_timestamp', value)

    @property
    def destination_port(self):
        # type: () -> L4PortRange
        """destination_port getter

        Layer4 protocol source or destination port valuesLayer4 protocol source or destination port values

        Returns: L4PortRange
        """
        return self._get_property('destination_port', L4PortRange)

    @property
    def source_port(self):
        # type: () -> L4PortRange
        """source_port getter

        Layer4 protocol source or destination port valuesLayer4 protocol source or destination port values

        Returns: L4PortRange
        """
        return self._get_property('source_port', L4PortRange)


class L4PortRange(OpenApiObject):
    __slots__ = ('_parent','_choice')

    _TYPES = {
        'choice': {
            'type': str,
            'enum': [
                'single_value',
                'range',
            ],
        },
        'single_value': {'type': 'L4PortRangeSingleValue'},
        'range': {'type': 'L4PortRangeRange'},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    SINGLE_VALUE = 'single_value' # type: str
    RANGE = 'range' # type: str

    def __init__(self, parent=None, choice=None):
        super(L4PortRange, self).__init__()
        self._parent = parent
        if 'choice' in self._DEFAULTS and choice is None:
            getattr(self, self._DEFAULTS['choice'])
        else:
            self.choice = choice

    @property
    def single_value(self):
        # type: () -> L4PortRangeSingleValue
        """Factory property that returns an instance of the L4PortRangeSingleValue class

        TBD

        Returns: L4PortRangeSingleValue
        """
        return self._get_property('single_value', L4PortRangeSingleValue, self, 'single_value')

    @property
    def range(self):
        # type: () -> L4PortRangeRange
        """Factory property that returns an instance of the L4PortRangeRange class

        TBD

        Returns: L4PortRangeRange
        """
        return self._get_property('range', L4PortRangeRange, self, 'range')

    @property
    def choice(self):
        # type: () -> Union[Literal["range"], Literal["single_value"]]
        """choice getter

        None

        Returns: Union[Literal["range"], Literal["single_value"]]
        """
        return self._get_property('choice')

    @choice.setter
    def choice(self, value):
        """choice setter

        None

        value: Union[Literal["range"], Literal["single_value"]]
        """
        self._set_property('choice', value)


class L4PortRangeSingleValue(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'value': {'type': int},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS = {
        'value': 1,
    } # type: Dict[str, Union(type)]

    def __init__(self, parent=None, value=1):
        super(L4PortRangeSingleValue, self).__init__()
        self._parent = parent
        self._set_property('value', value)

    @property
    def value(self):
        # type: () -> int
        """value getter

        TBD

        Returns: int
        """
        return self._get_property('value')

    @value.setter
    def value(self, value):
        """value setter

        TBD

        value: int
        """
        self._set_property('value', value)


class L4PortRangeRange(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'start_value': {'type': int},
        'increment': {
            'type': int,
            'minimum': 1,
        },
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS = {
        'start_value': 1,
        'increment': 1,
    } # type: Dict[str, Union(type)]

    def __init__(self, parent=None, start_value=1, increment=1):
        super(L4PortRangeRange, self).__init__()
        self._parent = parent
        self._set_property('start_value', start_value)
        self._set_property('increment', increment)

    @property
    def start_value(self):
        # type: () -> int
        """start_value getter

        TBD

        Returns: int
        """
        return self._get_property('start_value')

    @start_value.setter
    def start_value(self, value):
        """start_value setter

        TBD

        value: int
        """
        self._set_property('start_value', value)

    @property
    def increment(self):
        # type: () -> int
        """increment getter

        TBD

        Returns: int
        """
        return self._get_property('increment')

    @increment.setter
    def increment(self, value):
        """increment setter

        TBD

        value: int
        """
        self._set_property('increment', value)


class DataflowFlowProfileUdp(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {} # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None):
        super(DataflowFlowProfileUdp, self).__init__()
        self._parent = parent


class DataflowFlowProfileIter(OpenApiIter):
    __slots__ = ('_parent', '_choice')

    _GETITEM_RETURNS_CHOICE_OBJECT = False

    def __init__(self, parent=None, choice=None):
        super(DataflowFlowProfileIter, self).__init__()
        self._parent = parent
        self._choice = choice

    def __getitem__(self, key):
        # type: (str) -> Union[DataflowFlowProfile]
        return self._getitem(key)

    def __iter__(self):
        # type: () -> DataflowFlowProfileIter
        return self._iter()

    def __next__(self):
        # type: () -> DataflowFlowProfile
        return self._next()

    def next(self):
        # type: () -> DataflowFlowProfile
        return self._next()

    def flowprofile(self, name=None, data_size=None, l2_protocol_choice=None, l4_protocol_choice=None):
        # type: (str,int,Union[Literal["ethernet"]],Union[Literal["tcp"], Literal["udp"]]) -> DataflowFlowProfileIter
        """Factory method that creates an instance of the DataflowFlowProfile class

        TBD

        Returns: DataflowFlowProfileIter
        """
        item = DataflowFlowProfile(parent=self._parent, name=name, data_size=data_size, l2_protocol_choice=l2_protocol_choice, l4_protocol_choice=l4_protocol_choice)
        self._add(item)
        return self

    def add(self, name=None, data_size=None, l2_protocol_choice=None, l4_protocol_choice=None):
        # type: (str,int,Union[Literal["ethernet"]],Union[Literal["tcp"], Literal["udp"]]) -> DataflowFlowProfile
        """Add method that creates and returns an instance of the DataflowFlowProfile class

        TBD

        Returns: DataflowFlowProfile
        """
        item = DataflowFlowProfile(parent=self._parent, name=name, data_size=data_size, l2_protocol_choice=l2_protocol_choice, l4_protocol_choice=l4_protocol_choice)
        self._add(item)
        return item


class Chaos(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'background_traffic': {'type': 'ChaosBackgroundTraffic'},
        'drop_frames': {'type': 'ChaosDropFramesIter'},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None):
        super(Chaos, self).__init__()
        self._parent = parent

    @property
    def background_traffic(self):
        # type: () -> ChaosBackgroundTraffic
        """background_traffic getter

        

        Returns: ChaosBackgroundTraffic
        """
        return self._get_property('background_traffic', ChaosBackgroundTraffic)

    @property
    def drop_frames(self):
        # type: () -> ChaosDropFramesIter
        """drop_frames getter

        TBD

        Returns: ChaosDropFramesIter
        """
        return self._get_property('drop_frames', ChaosDropFramesIter, self._parent, self._choice)


class ChaosBackgroundTraffic(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'flows': {'type': 'ChaosBackgroundTrafficFlowIter'},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None):
        super(ChaosBackgroundTraffic, self).__init__()
        self._parent = parent

    @property
    def flows(self):
        # type: () -> ChaosBackgroundTrafficFlowIter
        """flows getter

        TBD

        Returns: ChaosBackgroundTrafficFlowIter
        """
        return self._get_property('flows', ChaosBackgroundTrafficFlowIter, self._parent, self._choice)


class ChaosBackgroundTrafficFlow(OpenApiObject):
    __slots__ = ('_parent','_choice')

    _TYPES = {
        'name': {'type': str},
        'injection_port': {'type': str},
        'choice': {
            'type': str,
            'enum': [
                'stateless',
            ],
        },
        'stateless': {'type': 'ChaosBackgroundTrafficFlowStateless'},
        'annotations': {'type': str},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    STATELESS = 'stateless' # type: str

    def __init__(self, parent=None, choice=None, name=None, injection_port=None, annotations=None):
        super(ChaosBackgroundTrafficFlow, self).__init__()
        self._parent = parent
        self._set_property('name', name)
        self._set_property('injection_port', injection_port)
        self._set_property('annotations', annotations)
        if 'choice' in self._DEFAULTS and choice is None:
            getattr(self, self._DEFAULTS['choice'])
        else:
            self.choice = choice

    @property
    def stateless(self):
        # type: () -> ChaosBackgroundTrafficFlowStateless
        """Factory property that returns an instance of the ChaosBackgroundTrafficFlowStateless class

        TBD

        Returns: ChaosBackgroundTrafficFlowStateless
        """
        return self._get_property('stateless', ChaosBackgroundTrafficFlowStateless, self, 'stateless')

    @property
    def name(self):
        # type: () -> str
        """name getter

        TBD

        Returns: str
        """
        return self._get_property('name')

    @name.setter
    def name(self, value):
        """name setter

        TBD

        value: str
        """
        self._set_property('name', value)

    @property
    def injection_port(self):
        # type: () -> str
        """injection_port getter

        Emulated port name, e.g. Spine Switch 1 Port 1

        Returns: str
        """
        return self._get_property('injection_port')

    @injection_port.setter
    def injection_port(self, value):
        """injection_port setter

        Emulated port name, e.g. Spine Switch 1 Port 1

        value: str
        """
        self._set_property('injection_port', value)

    @property
    def choice(self):
        # type: () -> Union[Literal["stateless"]]
        """choice getter

        TBD

        Returns: Union[Literal["stateless"]]
        """
        return self._get_property('choice')

    @choice.setter
    def choice(self, value):
        """choice setter

        TBD

        value: Union[Literal["stateless"]]
        """
        self._set_property('choice', value)

    @property
    def annotations(self):
        # type: () -> str
        """annotations getter

        TBD

        Returns: str
        """
        return self._get_property('annotations')

    @annotations.setter
    def annotations(self, value):
        """annotations setter

        TBD

        value: str
        """
        self._set_property('annotations', value)


class ChaosBackgroundTrafficFlowStateless(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'rate': {'type': int},
        'transmission_mode': {
            'type': str,
            'enum': [
                'burst',
                'continuous',
            ],
        },
        'packet': {'type': 'ChaosBackgroundTrafficFlowStatelessPacket'},
        'burst': {'type': 'ChaosBackgroundTrafficFlowStatelessBurst'},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS = {
        'transmission_mode': 'continuous',
    } # type: Dict[str, Union(type)]

    BURST = 'burst' # type: str
    CONTINUOUS = 'continuous' # type: str

    def __init__(self, parent=None, rate=None, transmission_mode='continuous'):
        super(ChaosBackgroundTrafficFlowStateless, self).__init__()
        self._parent = parent
        self._set_property('rate', rate)
        self._set_property('transmission_mode', transmission_mode)

    @property
    def rate(self):
        # type: () -> int
        """rate getter

        Transmission rate specified as a percentage of the injection port speed

        Returns: int
        """
        return self._get_property('rate')

    @rate.setter
    def rate(self, value):
        """rate setter

        Transmission rate specified as a percentage of the injection port speed

        value: int
        """
        self._set_property('rate', value)

    @property
    def transmission_mode(self):
        # type: () -> Union[Literal["burst"], Literal["continuous"]]
        """transmission_mode getter

        TBD

        Returns: Union[Literal["burst"], Literal["continuous"]]
        """
        return self._get_property('transmission_mode')

    @transmission_mode.setter
    def transmission_mode(self, value):
        """transmission_mode setter

        TBD

        value: Union[Literal["burst"], Literal["continuous"]]
        """
        self._set_property('transmission_mode', value)

    @property
    def packet(self):
        # type: () -> ChaosBackgroundTrafficFlowStatelessPacket
        """packet getter

        

        Returns: ChaosBackgroundTrafficFlowStatelessPacket
        """
        return self._get_property('packet', ChaosBackgroundTrafficFlowStatelessPacket)

    @property
    def burst(self):
        # type: () -> ChaosBackgroundTrafficFlowStatelessBurst
        """burst getter

        

        Returns: ChaosBackgroundTrafficFlowStatelessBurst
        """
        return self._get_property('burst', ChaosBackgroundTrafficFlowStatelessBurst)


class ChaosBackgroundTrafficFlowStatelessPacket(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'src_address': {'type': str},
        'dst_address': {'type': str},
        'src_port': {
            'type': int,
            'maximum': 65535,
        },
        'dst_port': {
            'type': int,
            'maximum': 65535,
        },
        'size': {
            'type': int,
            'minimum': 64,
        },
        'l4_protocol': {
            'type': str,
            'enum': [
                'tcp',
                'udp',
            ],
        },
        'ds_field': {'type': 'ChaosBackgroundTrafficFlowStatelessPacketDsField'},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS = {
        'src_port': 1024,
        'dst_port': 1024,
        'size': 1000,
    } # type: Dict[str, Union(type)]

    TCP = 'tcp' # type: str
    UDP = 'udp' # type: str

    def __init__(self, parent=None, src_address=None, dst_address=None, src_port=1024, dst_port=1024, size=1000, l4_protocol=None):
        super(ChaosBackgroundTrafficFlowStatelessPacket, self).__init__()
        self._parent = parent
        self._set_property('src_address', src_address)
        self._set_property('dst_address', dst_address)
        self._set_property('src_port', src_port)
        self._set_property('dst_port', dst_port)
        self._set_property('size', size)
        self._set_property('l4_protocol', l4_protocol)

    @property
    def src_address(self):
        # type: () -> str
        """src_address getter

        source IP address

        Returns: str
        """
        return self._get_property('src_address')

    @src_address.setter
    def src_address(self, value):
        """src_address setter

        source IP address

        value: str
        """
        self._set_property('src_address', value)

    @property
    def dst_address(self):
        # type: () -> str
        """dst_address getter

        destination IP address

        Returns: str
        """
        return self._get_property('dst_address')

    @dst_address.setter
    def dst_address(self, value):
        """dst_address setter

        destination IP address

        value: str
        """
        self._set_property('dst_address', value)

    @property
    def src_port(self):
        # type: () -> int
        """src_port getter

        Layer 4 source port

        Returns: int
        """
        return self._get_property('src_port')

    @src_port.setter
    def src_port(self, value):
        """src_port setter

        Layer 4 source port

        value: int
        """
        self._set_property('src_port', value)

    @property
    def dst_port(self):
        # type: () -> int
        """dst_port getter

        Layer 4 destination port

        Returns: int
        """
        return self._get_property('dst_port')

    @dst_port.setter
    def dst_port(self, value):
        """dst_port setter

        Layer 4 destination port

        value: int
        """
        self._set_property('dst_port', value)

    @property
    def size(self):
        # type: () -> int
        """size getter

        total packet size

        Returns: int
        """
        return self._get_property('size')

    @size.setter
    def size(self, value):
        """size setter

        total packet size

        value: int
        """
        self._set_property('size', value)

    @property
    def l4_protocol(self):
        # type: () -> Union[Literal["tcp"], Literal["udp"]]
        """l4_protocol getter

        Layer 4 transport protocol

        Returns: Union[Literal["tcp"], Literal["udp"]]
        """
        return self._get_property('l4_protocol')

    @l4_protocol.setter
    def l4_protocol(self, value):
        """l4_protocol setter

        Layer 4 transport protocol

        value: Union[Literal["tcp"], Literal["udp"]]
        """
        self._set_property('l4_protocol', value)

    @property
    def ds_field(self):
        # type: () -> ChaosBackgroundTrafficFlowStatelessPacketDsField
        """ds_field getter

        Differentiated Services or Traffic Class fieldDifferentiated Services or Traffic Class field

        Returns: ChaosBackgroundTrafficFlowStatelessPacketDsField
        """
        return self._get_property('ds_field', ChaosBackgroundTrafficFlowStatelessPacketDsField)


class ChaosBackgroundTrafficFlowStatelessPacketDsField(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'dscp': {
            'type': int,
            'minimum': 0,
            'maximum': 63,
        },
        'ecn': {
            'type': int,
            'minimum': 0,
            'maximum': 3,
        },
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS = {
        'dscp': 0,
        'ecn': 0,
    } # type: Dict[str, Union(type)]

    def __init__(self, parent=None, dscp=0, ecn=0):
        super(ChaosBackgroundTrafficFlowStatelessPacketDsField, self).__init__()
        self._parent = parent
        self._set_property('dscp', dscp)
        self._set_property('ecn', ecn)

    @property
    def dscp(self):
        # type: () -> int
        """dscp getter

        Differentiated Service CodePoint filed

        Returns: int
        """
        return self._get_property('dscp')

    @dscp.setter
    def dscp(self, value):
        """dscp setter

        Differentiated Service CodePoint filed

        value: int
        """
        self._set_property('dscp', value)

    @property
    def ecn(self):
        # type: () -> int
        """ecn getter

        Explicit Congestion Notification field

        Returns: int
        """
        return self._get_property('ecn')

    @ecn.setter
    def ecn(self, value):
        """ecn setter

        Explicit Congestion Notification field

        value: int
        """
        self._set_property('ecn', value)


class ChaosBackgroundTrafficFlowStatelessBurst(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'transmit_duration': {'type': int},
        'transmit_gap': {'type': int},
        'unit': {
            'type': str,
            'enum': [
                'ms',
            ],
        },
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS = {
        'unit': 'ms',
    } # type: Dict[str, Union(type)]

    MS = 'ms' # type: str

    def __init__(self, parent=None, transmit_duration=None, transmit_gap=None, unit='ms'):
        super(ChaosBackgroundTrafficFlowStatelessBurst, self).__init__()
        self._parent = parent
        self._set_property('transmit_duration', transmit_duration)
        self._set_property('transmit_gap', transmit_gap)
        self._set_property('unit', unit)

    @property
    def transmit_duration(self):
        # type: () -> int
        """transmit_duration getter

        TBD

        Returns: int
        """
        return self._get_property('transmit_duration')

    @transmit_duration.setter
    def transmit_duration(self, value):
        """transmit_duration setter

        TBD

        value: int
        """
        self._set_property('transmit_duration', value)

    @property
    def transmit_gap(self):
        # type: () -> int
        """transmit_gap getter

        TBD

        Returns: int
        """
        return self._get_property('transmit_gap')

    @transmit_gap.setter
    def transmit_gap(self, value):
        """transmit_gap setter

        TBD

        value: int
        """
        self._set_property('transmit_gap', value)

    @property
    def unit(self):
        # type: () -> Union[Literal["ms"]]
        """unit getter

        TBD

        Returns: Union[Literal["ms"]]
        """
        return self._get_property('unit')

    @unit.setter
    def unit(self, value):
        """unit setter

        TBD

        value: Union[Literal["ms"]]
        """
        self._set_property('unit', value)


class ChaosBackgroundTrafficFlowIter(OpenApiIter):
    __slots__ = ('_parent', '_choice')

    _GETITEM_RETURNS_CHOICE_OBJECT = False

    def __init__(self, parent=None, choice=None):
        super(ChaosBackgroundTrafficFlowIter, self).__init__()
        self._parent = parent
        self._choice = choice

    def __getitem__(self, key):
        # type: (str) -> Union[ChaosBackgroundTrafficFlow, ChaosBackgroundTrafficFlowStateless]
        return self._getitem(key)

    def __iter__(self):
        # type: () -> ChaosBackgroundTrafficFlowIter
        return self._iter()

    def __next__(self):
        # type: () -> ChaosBackgroundTrafficFlow
        return self._next()

    def next(self):
        # type: () -> ChaosBackgroundTrafficFlow
        return self._next()

    def flow(self, name=None, injection_port=None, annotations=None):
        # type: (str,str,str) -> ChaosBackgroundTrafficFlowIter
        """Factory method that creates an instance of the ChaosBackgroundTrafficFlow class

        TBD

        Returns: ChaosBackgroundTrafficFlowIter
        """
        item = ChaosBackgroundTrafficFlow(parent=self._parent, choice=self._choice, name=name, injection_port=injection_port, annotations=annotations)
        self._add(item)
        return self

    def add(self, name=None, injection_port=None, annotations=None):
        # type: (str,str,str) -> ChaosBackgroundTrafficFlow
        """Add method that creates and returns an instance of the ChaosBackgroundTrafficFlow class

        TBD

        Returns: ChaosBackgroundTrafficFlow
        """
        item = ChaosBackgroundTrafficFlow(parent=self._parent, choice=self._choice, name=name, injection_port=injection_port, annotations=annotations)
        self._add(item)
        return item


class ChaosDropFrames(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'name': {'type': str},
        'link': {'type': str},
        'mode': {
            'type': str,
            'enum': [
                'percentage_time',
                'min_time',
            ],
        },
        'percentage': {'type': float},
        'interval': {'type': int},
        'annotations': {'type': str},
    } # type: Dict[str, str]

    _REQUIRED = ('name', 'link') # type: tuple(str)

    _DEFAULTS = {
        'mode': 'percentage_time',
        'percentage': 5.0,
        'interval': 1,
    } # type: Dict[str, Union(type)]

    PERCENTAGE_TIME = 'percentage_time' # type: str
    MIN_TIME = 'min_time' # type: str

    def __init__(self, parent=None, name=None, link=None, mode='percentage_time', percentage=5, interval=1, annotations=None):
        super(ChaosDropFrames, self).__init__()
        self._parent = parent
        self._set_property('name', name)
        self._set_property('link', link)
        self._set_property('mode', mode)
        self._set_property('percentage', percentage)
        self._set_property('interval', interval)
        self._set_property('annotations', annotations)

    @property
    def name(self):
        # type: () -> str
        """name getter

        Uniquely identifies a drop frames config entry

        Returns: str
        """
        return self._get_property('name')

    @name.setter
    def name(self, value):
        """name setter

        Uniquely identifies a drop frames config entry

        value: str
        """
        self._set_property('name', value)

    @property
    def link(self):
        # type: () -> str
        """link getter

        Emulated link name, e.g. Link S.1/2

        Returns: str
        """
        return self._get_property('link')

    @link.setter
    def link(self, value):
        """link setter

        Emulated link name, e.g. Link S.1/2

        value: str
        """
        self._set_property('link', value)

    @property
    def mode(self):
        # type: () -> Union[Literal["min_time"], Literal["percentage_time"]]
        """mode getter

        Mode to express the duration in which frames are dropped, either a percentage of the specified time interval or the min possible time

        Returns: Union[Literal["min_time"], Literal["percentage_time"]]
        """
        return self._get_property('mode')

    @mode.setter
    def mode(self, value):
        """mode setter

        Mode to express the duration in which frames are dropped, either a percentage of the specified time interval or the min possible time

        value: Union[Literal["min_time"], Literal["percentage_time"]]
        """
        self._set_property('mode', value)

    @property
    def percentage(self):
        # type: () -> float
        """percentage getter

        Percentage value, ignored if type is min_time

        Returns: float
        """
        return self._get_property('percentage')

    @percentage.setter
    def percentage(self, value):
        """percentage setter

        Percentage value, ignored if type is min_time

        value: float
        """
        self._set_property('percentage', value)

    @property
    def interval(self):
        # type: () -> int
        """interval getter

        Interval of time (seconds)

        Returns: int
        """
        return self._get_property('interval')

    @interval.setter
    def interval(self, value):
        """interval setter

        Interval of time (seconds)

        value: int
        """
        self._set_property('interval', value)

    @property
    def annotations(self):
        # type: () -> str
        """annotations getter

        TBD

        Returns: str
        """
        return self._get_property('annotations')

    @annotations.setter
    def annotations(self, value):
        """annotations setter

        TBD

        value: str
        """
        self._set_property('annotations', value)


class ChaosDropFramesIter(OpenApiIter):
    __slots__ = ('_parent', '_choice')

    _GETITEM_RETURNS_CHOICE_OBJECT = False

    def __init__(self, parent=None, choice=None):
        super(ChaosDropFramesIter, self).__init__()
        self._parent = parent
        self._choice = choice

    def __getitem__(self, key):
        # type: (str) -> Union[ChaosDropFrames]
        return self._getitem(key)

    def __iter__(self):
        # type: () -> ChaosDropFramesIter
        return self._iter()

    def __next__(self):
        # type: () -> ChaosDropFrames
        return self._next()

    def next(self):
        # type: () -> ChaosDropFrames
        return self._next()

    def dropframes(self, name=None, link=None, mode='percentage_time', percentage=5, interval=1, annotations=None):
        # type: (str,str,Union[Literal["min_time"], Literal["percentage_time"]],float,int,str) -> ChaosDropFramesIter
        """Factory method that creates an instance of the ChaosDropFrames class

        Configures an emulated link to periodically drop frames for a percentage of the specified time interval

        Returns: ChaosDropFramesIter
        """
        item = ChaosDropFrames(parent=self._parent, name=name, link=link, mode=mode, percentage=percentage, interval=interval, annotations=annotations)
        self._add(item)
        return self

    def add(self, name=None, link=None, mode='percentage_time', percentage=5, interval=1, annotations=None):
        # type: (str,str,Union[Literal["min_time"], Literal["percentage_time"]],float,int,str) -> ChaosDropFrames
        """Add method that creates and returns an instance of the ChaosDropFrames class

        Configures an emulated link to periodically drop frames for a percentage of the specified time interval

        Returns: ChaosDropFrames
        """
        item = ChaosDropFrames(parent=self._parent, name=name, link=link, mode=mode, percentage=percentage, interval=interval, annotations=annotations)
        self._add(item)
        return item


class Insights(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'port_mirroring': {'type': 'InsightsPortMirroringIter'},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None):
        super(Insights, self).__init__()
        self._parent = parent

    @property
    def port_mirroring(self):
        # type: () -> InsightsPortMirroringIter
        """port_mirroring getter

        TBD

        Returns: InsightsPortMirroringIter
        """
        return self._get_property('port_mirroring', InsightsPortMirroringIter, self._parent, self._choice)


class InsightsPortMirroring(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'name': {'type': str},
        'source_port': {'type': str},
        'destination_port': {'type': int},
        'mirror_type': {
            'type': str,
            'enum': [
                'ingress_frames',
                'egress_frames',
            ],
        },
        'annotations': {'type': str},
    } # type: Dict[str, str]

    _REQUIRED = ('name', 'source_port', 'destination_port') # type: tuple(str)

    _DEFAULTS = {
        'mirror_type': 'ingress_frames',
    } # type: Dict[str, Union(type)]

    INGRESS_FRAMES = 'ingress_frames' # type: str
    EGRESS_FRAMES = 'egress_frames' # type: str

    def __init__(self, parent=None, name=None, source_port=None, destination_port=None, mirror_type='ingress_frames', annotations=None):
        super(InsightsPortMirroring, self).__init__()
        self._parent = parent
        self._set_property('name', name)
        self._set_property('source_port', source_port)
        self._set_property('destination_port', destination_port)
        self._set_property('mirror_type', mirror_type)
        self._set_property('annotations', annotations)

    @property
    def name(self):
        # type: () -> str
        """name getter

        Uniquely identifies a port port_mirroring entry

        Returns: str
        """
        return self._get_property('name')

    @name.setter
    def name(self, value):
        """name setter

        Uniquely identifies a port port_mirroring entry

        value: str
        """
        self._set_property('name', value)

    @property
    def source_port(self):
        # type: () -> str
        """source_port getter

        Emulated port name, e.g. Spine Switch 1 Port 1 to be mirrored

        Returns: str
        """
        return self._get_property('source_port')

    @source_port.setter
    def source_port(self, value):
        """source_port setter

        Emulated port name, e.g. Spine Switch 1 Port 1 to be mirrored

        value: str
        """
        self._set_property('source_port', value)

    @property
    def destination_port(self):
        # type: () -> int
        """destination_port getter

        Front panel port number of an external host, e.g. 32 on which to mirror

        Returns: int
        """
        return self._get_property('destination_port')

    @destination_port.setter
    def destination_port(self, value):
        """destination_port setter

        Front panel port number of an external host, e.g. 32 on which to mirror

        value: int
        """
        self._set_property('destination_port', value)

    @property
    def mirror_type(self):
        # type: () -> Union[Literal["egress_frames"], Literal["ingress_frames"]]
        """mirror_type getter

        TBD

        Returns: Union[Literal["egress_frames"], Literal["ingress_frames"]]
        """
        return self._get_property('mirror_type')

    @mirror_type.setter
    def mirror_type(self, value):
        """mirror_type setter

        TBD

        value: Union[Literal["egress_frames"], Literal["ingress_frames"]]
        """
        self._set_property('mirror_type', value)

    @property
    def annotations(self):
        # type: () -> str
        """annotations getter

        TBD

        Returns: str
        """
        return self._get_property('annotations')

    @annotations.setter
    def annotations(self, value):
        """annotations setter

        TBD

        value: str
        """
        self._set_property('annotations', value)


class InsightsPortMirroringIter(OpenApiIter):
    __slots__ = ('_parent', '_choice')

    _GETITEM_RETURNS_CHOICE_OBJECT = False

    def __init__(self, parent=None, choice=None):
        super(InsightsPortMirroringIter, self).__init__()
        self._parent = parent
        self._choice = choice

    def __getitem__(self, key):
        # type: (str) -> Union[InsightsPortMirroring]
        return self._getitem(key)

    def __iter__(self):
        # type: () -> InsightsPortMirroringIter
        return self._iter()

    def __next__(self):
        # type: () -> InsightsPortMirroring
        return self._next()

    def next(self):
        # type: () -> InsightsPortMirroring
        return self._next()

    def portmirroring(self, name=None, source_port=None, destination_port=None, mirror_type='ingress_frames', annotations=None):
        # type: (str,str,int,Union[Literal["egress_frames"], Literal["ingress_frames"]],str) -> InsightsPortMirroringIter
        """Factory method that creates an instance of the InsightsPortMirroring class

        TBD

        Returns: InsightsPortMirroringIter
        """
        item = InsightsPortMirroring(parent=self._parent, name=name, source_port=source_port, destination_port=destination_port, mirror_type=mirror_type, annotations=annotations)
        self._add(item)
        return self

    def add(self, name=None, source_port=None, destination_port=None, mirror_type='ingress_frames', annotations=None):
        # type: (str,str,int,Union[Literal["egress_frames"], Literal["ingress_frames"]],str) -> InsightsPortMirroring
        """Add method that creates and returns an instance of the InsightsPortMirroring class

        TBD

        Returns: InsightsPortMirroring
        """
        item = InsightsPortMirroring(parent=self._parent, name=name, source_port=source_port, destination_port=destination_port, mirror_type=mirror_type, annotations=annotations)
        self._add(item)
        return item


class L1SettingsProfile(OpenApiObject):
    __slots__ = ('_parent','_choice')

    _TYPES = {
        'name': {'type': str},
        'link_speed': {
            'type': str,
            'enum': [
                'speed_100_gbps',
                'speed_200_gbps',
                'speed_50_gbps',
                'speed_25_gbps',
            ],
        },
        'choice': {
            'type': str,
            'enum': [
                'autonegotiation',
                'manual',
            ],
        },
        'autonegotiation': {'type': 'L1SettingsProfileAutonegotiation'},
        'manual': {'type': 'L1SettingsProfileManual'},
        'annotations': {'type': str},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS = {
        'link_speed': 'speed_100_gbps',
        'choice': 'autonegotiation',
    } # type: Dict[str, Union(type)]

    SPEED_100_GBPS = 'speed_100_gbps' # type: str
    SPEED_200_GBPS = 'speed_200_gbps' # type: str
    SPEED_50_GBPS = 'speed_50_gbps' # type: str
    SPEED_25_GBPS = 'speed_25_gbps' # type: str

    AUTONEGOTIATION = 'autonegotiation' # type: str
    MANUAL = 'manual' # type: str

    def __init__(self, parent=None, choice=None, name=None, link_speed='speed_100_gbps', annotations=None):
        super(L1SettingsProfile, self).__init__()
        self._parent = parent
        self._set_property('name', name)
        self._set_property('link_speed', link_speed)
        self._set_property('annotations', annotations)
        if 'choice' in self._DEFAULTS and choice is None:
            getattr(self, self._DEFAULTS['choice'])
        else:
            self.choice = choice

    @property
    def autonegotiation(self):
        # type: () -> L1SettingsProfileAutonegotiation
        """Factory property that returns an instance of the L1SettingsProfileAutonegotiation class

        TBD

        Returns: L1SettingsProfileAutonegotiation
        """
        return self._get_property('autonegotiation', L1SettingsProfileAutonegotiation, self, 'autonegotiation')

    @property
    def manual(self):
        # type: () -> L1SettingsProfileManual
        """Factory property that returns an instance of the L1SettingsProfileManual class

        TBD

        Returns: L1SettingsProfileManual
        """
        return self._get_property('manual', L1SettingsProfileManual, self, 'manual')

    @property
    def name(self):
        # type: () -> str
        """name getter

        Uniquely identifies a layer 1 settings profile

        Returns: str
        """
        return self._get_property('name')

    @name.setter
    def name(self, value):
        """name setter

        Uniquely identifies a layer 1 settings profile

        value: str
        """
        self._set_property('name', value)

    @property
    def link_speed(self):
        # type: () -> Union[Literal["speed_100_gbps"], Literal["speed_200_gbps"], Literal["speed_25_gbps"], Literal["speed_50_gbps"]]
        """link_speed getter

        Link speed

        Returns: Union[Literal["speed_100_gbps"], Literal["speed_200_gbps"], Literal["speed_25_gbps"], Literal["speed_50_gbps"]]
        """
        return self._get_property('link_speed')

    @link_speed.setter
    def link_speed(self, value):
        """link_speed setter

        Link speed

        value: Union[Literal["speed_100_gbps"], Literal["speed_200_gbps"], Literal["speed_25_gbps"], Literal["speed_50_gbps"]]
        """
        self._set_property('link_speed', value)

    @property
    def choice(self):
        # type: () -> Union[Literal["autonegotiation"], Literal["manual"]]
        """choice getter

        TBD

        Returns: Union[Literal["autonegotiation"], Literal["manual"]]
        """
        return self._get_property('choice')

    @choice.setter
    def choice(self, value):
        """choice setter

        TBD

        value: Union[Literal["autonegotiation"], Literal["manual"]]
        """
        self._set_property('choice', value)

    @property
    def annotations(self):
        # type: () -> str
        """annotations getter

        TBD

        Returns: str
        """
        return self._get_property('annotations')

    @annotations.setter
    def annotations(self, value):
        """annotations setter

        TBD

        value: str
        """
        self._set_property('annotations', value)


class L1SettingsProfileAutonegotiation(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'advertise_fec': {'type': bool},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS = {
        'advertise_fec': True,
    } # type: Dict[str, Union(type)]

    def __init__(self, parent=None, advertise_fec=True):
        super(L1SettingsProfileAutonegotiation, self).__init__()
        self._parent = parent
        self._set_property('advertise_fec', advertise_fec)

    @property
    def advertise_fec(self):
        # type: () -> bool
        """advertise_fec getter

        TBD

        Returns: bool
        """
        return self._get_property('advertise_fec')

    @advertise_fec.setter
    def advertise_fec(self, value):
        """advertise_fec setter

        TBD

        value: bool
        """
        self._set_property('advertise_fec', value)


class L1SettingsProfileManual(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'fec_mode': {
            'type': str,
            'enum': [
                'firecode',
                'kp4',
                'reed_solomon',
            ],
        },
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS = {
        'fec_mode': 'reed_solomon',
    } # type: Dict[str, Union(type)]

    FIRECODE = 'firecode' # type: str
    KP4 = 'kp4' # type: str
    REED_SOLOMON = 'reed_solomon' # type: str

    def __init__(self, parent=None, fec_mode='reed_solomon'):
        super(L1SettingsProfileManual, self).__init__()
        self._parent = parent
        self._set_property('fec_mode', fec_mode)

    @property
    def fec_mode(self):
        # type: () -> Union[Literal["firecode"], Literal["kp4"], Literal["reed_solomon"]]
        """fec_mode getter

        TBD

        Returns: Union[Literal["firecode"], Literal["kp4"], Literal["reed_solomon"]]
        """
        return self._get_property('fec_mode')

    @fec_mode.setter
    def fec_mode(self, value):
        """fec_mode setter

        TBD

        value: Union[Literal["firecode"], Literal["kp4"], Literal["reed_solomon"]]
        """
        self._set_property('fec_mode', value)


class L1SettingsProfileIter(OpenApiIter):
    __slots__ = ('_parent', '_choice')

    _GETITEM_RETURNS_CHOICE_OBJECT = False

    def __init__(self, parent=None, choice=None):
        super(L1SettingsProfileIter, self).__init__()
        self._parent = parent
        self._choice = choice

    def __getitem__(self, key):
        # type: (str) -> Union[L1SettingsProfile, L1SettingsProfileAutonegotiation, L1SettingsProfileManual]
        return self._getitem(key)

    def __iter__(self):
        # type: () -> L1SettingsProfileIter
        return self._iter()

    def __next__(self):
        # type: () -> L1SettingsProfile
        return self._next()

    def next(self):
        # type: () -> L1SettingsProfile
        return self._next()

    def l1settingsprofile(self, name=None, link_speed='speed_100_gbps', annotations=None):
        # type: (str,Union[Literal["speed_100_gbps"], Literal["speed_200_gbps"], Literal["speed_25_gbps"], Literal["speed_50_gbps"]],str) -> L1SettingsProfileIter
        """Factory method that creates an instance of the L1SettingsProfile class

        TBD

        Returns: L1SettingsProfileIter
        """
        item = L1SettingsProfile(parent=self._parent, choice=self._choice, name=name, link_speed=link_speed, annotations=annotations)
        self._add(item)
        return self

    def add(self, name=None, link_speed='speed_100_gbps', annotations=None):
        # type: (str,Union[Literal["speed_100_gbps"], Literal["speed_200_gbps"], Literal["speed_25_gbps"], Literal["speed_50_gbps"]],str) -> L1SettingsProfile
        """Add method that creates and returns an instance of the L1SettingsProfile class

        TBD

        Returns: L1SettingsProfile
        """
        item = L1SettingsProfile(parent=self._parent, choice=self._choice, name=name, link_speed=link_speed, annotations=annotations)
        self._add(item)
        return item


class ErrorDetails(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'errors': {'type': 'ErrorItemIter'},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None):
        super(ErrorDetails, self).__init__()
        self._parent = parent

    @property
    def errors(self):
        # type: () -> ErrorItemIter
        """errors getter

        TBD

        Returns: ErrorItemIter
        """
        return self._get_property('errors', ErrorItemIter, self._parent, self._choice)


class ErrorItem(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'message': {'type': str},
        'code': {'type': int},
        'detail': {'type': str},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None, message=None, code=None, detail=None):
        super(ErrorItem, self).__init__()
        self._parent = parent
        self._set_property('message', message)
        self._set_property('code', code)
        self._set_property('detail', detail)

    @property
    def message(self):
        # type: () -> str
        """message getter

        TBD

        Returns: str
        """
        return self._get_property('message')

    @message.setter
    def message(self, value):
        """message setter

        TBD

        value: str
        """
        self._set_property('message', value)

    @property
    def code(self):
        # type: () -> int
        """code getter

        TBD

        Returns: int
        """
        return self._get_property('code')

    @code.setter
    def code(self, value):
        """code setter

        TBD

        value: int
        """
        self._set_property('code', value)

    @property
    def detail(self):
        # type: () -> str
        """detail getter

        TBD

        Returns: str
        """
        return self._get_property('detail')

    @detail.setter
    def detail(self, value):
        """detail setter

        TBD

        value: str
        """
        self._set_property('detail', value)


class ErrorItemIter(OpenApiIter):
    __slots__ = ('_parent', '_choice')

    _GETITEM_RETURNS_CHOICE_OBJECT = False

    def __init__(self, parent=None, choice=None):
        super(ErrorItemIter, self).__init__()
        self._parent = parent
        self._choice = choice

    def __getitem__(self, key):
        # type: (str) -> Union[ErrorItem]
        return self._getitem(key)

    def __iter__(self):
        # type: () -> ErrorItemIter
        return self._iter()

    def __next__(self):
        # type: () -> ErrorItem
        return self._next()

    def next(self):
        # type: () -> ErrorItem
        return self._next()

    def item(self, message=None, code=None, detail=None):
        # type: (str,int,str) -> ErrorItemIter
        """Factory method that creates an instance of the ErrorItem class

        TBD

        Returns: ErrorItemIter
        """
        item = ErrorItem(parent=self._parent, message=message, code=code, detail=detail)
        self._add(item)
        return self

    def add(self, message=None, code=None, detail=None):
        # type: (str,int,str) -> ErrorItem
        """Add method that creates and returns an instance of the ErrorItem class

        TBD

        Returns: ErrorItem
        """
        item = ErrorItem(parent=self._parent, message=message, code=code, detail=detail)
        self._add(item)
        return item


class State(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'chaos': {'type': 'StateChaos'},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None):
        super(State, self).__init__()
        self._parent = parent

    @property
    def chaos(self):
        # type: () -> StateChaos
        """chaos getter

        

        Returns: StateChaos
        """
        return self._get_property('chaos', StateChaos)


class StateChaos(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'drop_frames': {'type': 'StateChaosDropFramesIter'},
        'background_traffic': {'type': 'StateChaosBackgroundTrafficIter'},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None):
        super(StateChaos, self).__init__()
        self._parent = parent

    @property
    def drop_frames(self):
        # type: () -> StateChaosDropFramesIter
        """drop_frames getter

        TBD

        Returns: StateChaosDropFramesIter
        """
        return self._get_property('drop_frames', StateChaosDropFramesIter, self._parent, self._choice)

    @property
    def background_traffic(self):
        # type: () -> StateChaosBackgroundTrafficIter
        """background_traffic getter

        TBD

        Returns: StateChaosBackgroundTrafficIter
        """
        return self._get_property('background_traffic', StateChaosBackgroundTrafficIter, self._parent, self._choice)


class StateChaosDropFrames(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'config_names': {
            'type': list,
            'itemtype': str,
        },
        'state': {
            'type': str,
            'enum': [
                'started',
                'stopped',
            ],
        },
    } # type: Dict[str, str]

    _REQUIRED = ('state', 'config_names') # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    STARTED = 'started' # type: str
    STOPPED = 'stopped' # type: str

    def __init__(self, parent=None, config_names=None, state=None):
        super(StateChaosDropFrames, self).__init__()
        self._parent = parent
        self._set_property('config_names', config_names)
        self._set_property('state', state)

    @property
    def config_names(self):
        # type: () -> List[str]
        """config_names getter

        The names of the drop frams configs to which the transmit state will be applied to.. . x-constraint:. - ../chaos/chaos.yaml/components/schemas/DropFrames/properties/name. 

        Returns: List[str]
        """
        return self._get_property('config_names')

    @config_names.setter
    def config_names(self, value):
        """config_names setter

        The names of the drop frams configs to which the transmit state will be applied to.. . x-constraint:. - ../chaos/chaos.yaml/components/schemas/DropFrames/properties/name. 

        value: List[str]
        """
        self._set_property('config_names', value)

    @property
    def state(self):
        # type: () -> Union[Literal["started"], Literal["stopped"]]
        """state getter

        TBD

        Returns: Union[Literal["started"], Literal["stopped"]]
        """
        return self._get_property('state')

    @state.setter
    def state(self, value):
        """state setter

        TBD

        value: Union[Literal["started"], Literal["stopped"]]
        """
        self._set_property('state', value)


class StateChaosDropFramesIter(OpenApiIter):
    __slots__ = ('_parent', '_choice')

    _GETITEM_RETURNS_CHOICE_OBJECT = False

    def __init__(self, parent=None, choice=None):
        super(StateChaosDropFramesIter, self).__init__()
        self._parent = parent
        self._choice = choice

    def __getitem__(self, key):
        # type: (str) -> Union[StateChaosDropFrames]
        return self._getitem(key)

    def __iter__(self):
        # type: () -> StateChaosDropFramesIter
        return self._iter()

    def __next__(self):
        # type: () -> StateChaosDropFrames
        return self._next()

    def next(self):
        # type: () -> StateChaosDropFrames
        return self._next()

    def dropframes(self, config_names=None, state=None):
        # type: (List[str],Union[Literal["started"], Literal["stopped"]]) -> StateChaosDropFramesIter
        """Factory method that creates an instance of the StateChaosDropFrames class

        TBD

        Returns: StateChaosDropFramesIter
        """
        item = StateChaosDropFrames(parent=self._parent, config_names=config_names, state=state)
        self._add(item)
        return self

    def add(self, config_names=None, state=None):
        # type: (List[str],Union[Literal["started"], Literal["stopped"]]) -> StateChaosDropFrames
        """Add method that creates and returns an instance of the StateChaosDropFrames class

        TBD

        Returns: StateChaosDropFrames
        """
        item = StateChaosDropFrames(parent=self._parent, config_names=config_names, state=state)
        self._add(item)
        return item


class StateChaosBackgroundTraffic(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'flow_names': {
            'type': list,
            'itemtype': str,
        },
        'state': {
            'type': str,
            'enum': [
                'started',
                'stopped',
            ],
        },
    } # type: Dict[str, str]

    _REQUIRED = ('state', 'flow_names') # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    STARTED = 'started' # type: str
    STOPPED = 'stopped' # type: str

    def __init__(self, parent=None, flow_names=None, state=None):
        super(StateChaosBackgroundTraffic, self).__init__()
        self._parent = parent
        self._set_property('flow_names', flow_names)
        self._set_property('state', state)

    @property
    def flow_names(self):
        # type: () -> List[str]
        """flow_names getter

        The names of flows to which the transmit state will be applied to.. . x-constraint:. - ../chaos/background_traffic.yaml/components/schemas/Flow/properties/name. 

        Returns: List[str]
        """
        return self._get_property('flow_names')

    @flow_names.setter
    def flow_names(self, value):
        """flow_names setter

        The names of flows to which the transmit state will be applied to.. . x-constraint:. - ../chaos/background_traffic.yaml/components/schemas/Flow/properties/name. 

        value: List[str]
        """
        self._set_property('flow_names', value)

    @property
    def state(self):
        # type: () -> Union[Literal["started"], Literal["stopped"]]
        """state getter

        TBD

        Returns: Union[Literal["started"], Literal["stopped"]]
        """
        return self._get_property('state')

    @state.setter
    def state(self, value):
        """state setter

        TBD

        value: Union[Literal["started"], Literal["stopped"]]
        """
        self._set_property('state', value)


class StateChaosBackgroundTrafficIter(OpenApiIter):
    __slots__ = ('_parent', '_choice')

    _GETITEM_RETURNS_CHOICE_OBJECT = False

    def __init__(self, parent=None, choice=None):
        super(StateChaosBackgroundTrafficIter, self).__init__()
        self._parent = parent
        self._choice = choice

    def __getitem__(self, key):
        # type: (str) -> Union[StateChaosBackgroundTraffic]
        return self._getitem(key)

    def __iter__(self):
        # type: () -> StateChaosBackgroundTrafficIter
        return self._iter()

    def __next__(self):
        # type: () -> StateChaosBackgroundTraffic
        return self._next()

    def next(self):
        # type: () -> StateChaosBackgroundTraffic
        return self._next()

    def backgroundtraffic(self, flow_names=None, state=None):
        # type: (List[str],Union[Literal["started"], Literal["stopped"]]) -> StateChaosBackgroundTrafficIter
        """Factory method that creates an instance of the StateChaosBackgroundTraffic class

        TBD

        Returns: StateChaosBackgroundTrafficIter
        """
        item = StateChaosBackgroundTraffic(parent=self._parent, flow_names=flow_names, state=state)
        self._add(item)
        return self

    def add(self, flow_names=None, state=None):
        # type: (List[str],Union[Literal["started"], Literal["stopped"]]) -> StateChaosBackgroundTraffic
        """Add method that creates and returns an instance of the StateChaosBackgroundTraffic class

        TBD

        Returns: StateChaosBackgroundTraffic
        """
        item = StateChaosBackgroundTraffic(parent=self._parent, flow_names=flow_names, state=state)
        self._add(item)
        return item


class MetricsRequest(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'port_metrics': {'type': 'PortMetricsRequest'},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None):
        super(MetricsRequest, self).__init__()
        self._parent = parent

    @property
    def port_metrics(self):
        # type: () -> PortMetricsRequest
        """port_metrics getter

        

        Returns: PortMetricsRequest
        """
        return self._get_property('port_metrics', PortMetricsRequest)


class PortMetricsRequest(OpenApiObject):
    __slots__ = ('_parent','_choice')

    _TYPES = {
        'choice': {
            'type': str,
            'enum': [
                'port_names',
                'front_panel_ports',
            ],
        },
        'port_names': {
            'type': list,
            'itemtype': str,
        },
        'front_panel_ports': {
            'type': list,
            'itemtype': int,
        },
        'select_metrics': {
            'type': list,
            'itemtype': str,
        },
        'from_cache': {'type': bool},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS = {
        'from_cache': False,
    } # type: Dict[str, Union(type)]

    PORT_NAMES = 'port_names' # type: str
    FRONT_PANEL_PORTS = 'front_panel_ports' # type: str

    LINK_STATUS = 'link_status' # type: str
    FRAMES_TRANSMITTED_ALL = 'frames_transmitted_all' # type: str
    FRAMES_TRANSMITTED_MULTICAST = 'frames_transmitted_multicast' # type: str
    FRAMES_TRANSMITTED_UNICAST = 'frames_transmitted_unicast' # type: str
    FRAMES_TRANSMITTED_BROADCAST = 'frames_transmitted_broadcast' # type: str
    FRAMES_TRANSMITTED_LENGTH_64 = 'frames_transmitted_length_64' # type: str
    FRAMES_TRANSMITTED_LENGTH_65_127 = 'frames_transmitted_length_65_127' # type: str
    FRAMES_TRANSMITTED_LENGTH_128_255 = 'frames_transmitted_length_128_255' # type: str
    FRAMES_TRANSMITTED_LENGTH_256_511 = 'frames_transmitted_length_256_511' # type: str
    FRAMES_TRANSMITTED_LENGTH_512_1023 = 'frames_transmitted_length_512_1023' # type: str
    FRAMES_TRANSMITTED_LENGTH_1024_1518 = 'frames_transmitted_length_1024_1518' # type: str
    FRAMES_TRANSMITTED_LENGTH_1519_2047 = 'frames_transmitted_length_1519_2047' # type: str
    FRAMES_TRANSMITTED_LENGTH_2048_4095 = 'frames_transmitted_length_2048_4095' # type: str
    BYTES_TRANSMITTED_ALL = 'bytes_transmitted_all' # type: str
    FRAMES_TRANSMITTED_ECN_MARKED = 'frames_transmitted_ecn_marked' # type: str
    FRAMES_TRANSMITTED_PRIORITY_PAUSE = 'frames_transmitted_priority_pause' # type: str
    FRAMES_TRANSMITTED_PAUSE = 'frames_transmitted_pause' # type: str
    FRAMES_RECEIVED_ALL = 'frames_received_all' # type: str
    FRAMES_RECEIVED_MULTICAST = 'frames_received_multicast' # type: str
    FRAMES_RECEIVED_UNICAST = 'frames_received_unicast' # type: str
    FRAMES_RECEIVED_BROADCAST = 'frames_received_broadcast' # type: str
    FRAMES_RECEIVED_LENGTH_64 = 'frames_received_length_64' # type: str
    FRAMES_RECEIVED_LENGTH_65_127 = 'frames_received_length_65_127' # type: str
    FRAMES_RECEIVED_LENGTH_128_255 = 'frames_received_length_128_255' # type: str
    FRAMES_RECEIVED_LENGTH_256_511 = 'frames_received_length_256_511' # type: str
    FRAMES_RECEIVED_LENGTH_512_1023 = 'frames_received_length_512_1023' # type: str
    FRAMES_RECEIVED_LENGTH_1024_1518 = 'frames_received_length_1024_1518' # type: str
    FRAMES_RECEIVED_LENGTH_1519_2047 = 'frames_received_length_1519_2047' # type: str
    FRAMES_RECEIVED_LENGTH_2048_4095 = 'frames_received_length_2048_4095' # type: str
    BYTES_RECEIVED_ALL = 'bytes_received_all' # type: str
    FRAMES_RECEIVED_ERRORS = 'frames_received_errors' # type: str
    FRAMES_RECEIVED_PAUSE = 'frames_received_pause' # type: str
    FRAMES_RECEIVED_PRIORITY_PAUSE = 'frames_received_priority_pause' # type: str
    FRAMES_DROPPED_EGRESS = 'frames_dropped_egress' # type: str
    FRAMES_DROPPED_INGRESS = 'frames_dropped_ingress' # type: str
    PER_EGRESS_QUEUE_METRICS = 'per_egress_queue_metrics' # type: str
    PER_PRIORITY_GROUP_METRICS = 'per_priority_group_metrics' # type: str
    FLOW_COUNTER_METRICS = 'flow_counter_metrics' # type: str

    def __init__(self, parent=None, choice=None, port_names=None, front_panel_ports=None, select_metrics=None, from_cache=False):
        super(PortMetricsRequest, self).__init__()
        self._parent = parent
        self._set_property('port_names', port_names)
        self._set_property('front_panel_ports', front_panel_ports)
        self._set_property('select_metrics', select_metrics)
        self._set_property('from_cache', from_cache)
        if 'choice' in self._DEFAULTS and choice is None:
            getattr(self, self._DEFAULTS['choice'])
        else:
            self.choice = choice

    @property
    def choice(self):
        # type: () -> Union[Literal["front_panel_ports"], Literal["port_names"]]
        """choice getter

        TBD

        Returns: Union[Literal["front_panel_ports"], Literal["port_names"]]
        """
        return self._get_property('choice')

    @choice.setter
    def choice(self, value):
        """choice setter

        TBD

        value: Union[Literal["front_panel_ports"], Literal["port_names"]]
        """
        self._set_property('choice', value)

    @property
    def port_names(self):
        # type: () -> List[str]
        """port_names getter

        Emulated ports names for which metrics are being requested. If empty metrics for all ports will be returned.

        Returns: List[str]
        """
        return self._get_property('port_names')

    @port_names.setter
    def port_names(self, value):
        """port_names setter

        Emulated ports names for which metrics are being requested. If empty metrics for all ports will be returned.

        value: List[str]
        """
        self._set_property('port_names', value, 'port_names')

    @property
    def front_panel_ports(self):
        # type: () -> List[int]
        """front_panel_ports getter

        Front panel ports for which metrics are being requested. If empty metrics for all ports will be returned.

        Returns: List[int]
        """
        return self._get_property('front_panel_ports')

    @front_panel_ports.setter
    def front_panel_ports(self, value):
        """front_panel_ports setter

        Front panel ports for which metrics are being requested. If empty metrics for all ports will be returned.

        value: List[int]
        """
        self._set_property('front_panel_ports', value, 'front_panel_ports')

    @property
    def select_metrics(self):
        # type: () -> List[Union[Literal["bytes_received_all"], Literal["bytes_transmitted_all"], Literal["flow_counter_metrics"], Literal["frames_dropped_egress"], Literal["frames_dropped_ingress"], Literal["frames_received_all"], Literal["frames_received_broadcast"], Literal["frames_received_errors"], Literal["frames_received_length_1024_1518"], Literal["frames_received_length_128_255"], Literal["frames_received_length_1519_2047"], Literal["frames_received_length_2048_4095"], Literal["frames_received_length_256_511"], Literal["frames_received_length_512_1023"], Literal["frames_received_length_64"], Literal["frames_received_length_65_127"], Literal["frames_received_multicast"], Literal["frames_received_pause"], Literal["frames_received_priority_pause"], Literal["frames_received_unicast"], Literal["frames_transmitted_all"], Literal["frames_transmitted_broadcast"], Literal["frames_transmitted_ecn_marked"], Literal["frames_transmitted_length_1024_1518"], Literal["frames_transmitted_length_128_255"], Literal["frames_transmitted_length_1519_2047"], Literal["frames_transmitted_length_2048_4095"], Literal["frames_transmitted_length_256_511"], Literal["frames_transmitted_length_512_1023"], Literal["frames_transmitted_length_64"], Literal["frames_transmitted_length_65_127"], Literal["frames_transmitted_multicast"], Literal["frames_transmitted_pause"], Literal["frames_transmitted_priority_pause"], Literal["frames_transmitted_unicast"], Literal["link_status"], Literal["per_egress_queue_metrics"], Literal["per_priority_group_metrics"]]]
        """select_metrics getter

        Filters port metrics to be returned

        Returns: List[Union[Literal["bytes_received_all"], Literal["bytes_transmitted_all"], Literal["flow_counter_metrics"], Literal["frames_dropped_egress"], Literal["frames_dropped_ingress"], Literal["frames_received_all"], Literal["frames_received_broadcast"], Literal["frames_received_errors"], Literal["frames_received_length_1024_1518"], Literal["frames_received_length_128_255"], Literal["frames_received_length_1519_2047"], Literal["frames_received_length_2048_4095"], Literal["frames_received_length_256_511"], Literal["frames_received_length_512_1023"], Literal["frames_received_length_64"], Literal["frames_received_length_65_127"], Literal["frames_received_multicast"], Literal["frames_received_pause"], Literal["frames_received_priority_pause"], Literal["frames_received_unicast"], Literal["frames_transmitted_all"], Literal["frames_transmitted_broadcast"], Literal["frames_transmitted_ecn_marked"], Literal["frames_transmitted_length_1024_1518"], Literal["frames_transmitted_length_128_255"], Literal["frames_transmitted_length_1519_2047"], Literal["frames_transmitted_length_2048_4095"], Literal["frames_transmitted_length_256_511"], Literal["frames_transmitted_length_512_1023"], Literal["frames_transmitted_length_64"], Literal["frames_transmitted_length_65_127"], Literal["frames_transmitted_multicast"], Literal["frames_transmitted_pause"], Literal["frames_transmitted_priority_pause"], Literal["frames_transmitted_unicast"], Literal["link_status"], Literal["per_egress_queue_metrics"], Literal["per_priority_group_metrics"]]]
        """
        return self._get_property('select_metrics')

    @select_metrics.setter
    def select_metrics(self, value):
        """select_metrics setter

        Filters port metrics to be returned

        value: List[Union[Literal["bytes_received_all"], Literal["bytes_transmitted_all"], Literal["flow_counter_metrics"], Literal["frames_dropped_egress"], Literal["frames_dropped_ingress"], Literal["frames_received_all"], Literal["frames_received_broadcast"], Literal["frames_received_errors"], Literal["frames_received_length_1024_1518"], Literal["frames_received_length_128_255"], Literal["frames_received_length_1519_2047"], Literal["frames_received_length_2048_4095"], Literal["frames_received_length_256_511"], Literal["frames_received_length_512_1023"], Literal["frames_received_length_64"], Literal["frames_received_length_65_127"], Literal["frames_received_multicast"], Literal["frames_received_pause"], Literal["frames_received_priority_pause"], Literal["frames_received_unicast"], Literal["frames_transmitted_all"], Literal["frames_transmitted_broadcast"], Literal["frames_transmitted_ecn_marked"], Literal["frames_transmitted_length_1024_1518"], Literal["frames_transmitted_length_128_255"], Literal["frames_transmitted_length_1519_2047"], Literal["frames_transmitted_length_2048_4095"], Literal["frames_transmitted_length_256_511"], Literal["frames_transmitted_length_512_1023"], Literal["frames_transmitted_length_64"], Literal["frames_transmitted_length_65_127"], Literal["frames_transmitted_multicast"], Literal["frames_transmitted_pause"], Literal["frames_transmitted_priority_pause"], Literal["frames_transmitted_unicast"], Literal["link_status"], Literal["per_egress_queue_metrics"], Literal["per_priority_group_metrics"]]]
        """
        self._set_property('select_metrics', value)

    @property
    def from_cache(self):
        # type: () -> bool
        """from_cache getter

        Determines whether to retrieve metrics from cache or not

        Returns: bool
        """
        return self._get_property('from_cache')

    @from_cache.setter
    def from_cache(self, value):
        """from_cache setter

        Determines whether to retrieve metrics from cache or not

        value: bool
        """
        self._set_property('from_cache', value)


class MetricsResponse(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'port_metrics': {'type': 'PortMetricsResponse'},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None):
        super(MetricsResponse, self).__init__()
        self._parent = parent

    @property
    def port_metrics(self):
        # type: () -> PortMetricsResponse
        """port_metrics getter

        

        Returns: PortMetricsResponse
        """
        return self._get_property('port_metrics', PortMetricsResponse)


class PortMetricsResponse(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'timestamp': {'type': float},
        'metrics': {'type': 'PortMetricsPortEntryIter'},
    } # type: Dict[str, str]

    _REQUIRED = ('timestamp', 'metrics') # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None, timestamp=None):
        super(PortMetricsResponse, self).__init__()
        self._parent = parent
        self._set_property('timestamp', timestamp)

    @property
    def timestamp(self):
        # type: () -> float
        """timestamp getter

        Unix epoch time when metrics were sampled expressed in miliseconds

        Returns: float
        """
        return self._get_property('timestamp')

    @timestamp.setter
    def timestamp(self, value):
        """timestamp setter

        Unix epoch time when metrics were sampled expressed in miliseconds

        value: float
        """
        self._set_property('timestamp', value)

    @property
    def metrics(self):
        # type: () -> PortMetricsPortEntryIter
        """metrics getter

        TBD

        Returns: PortMetricsPortEntryIter
        """
        return self._get_property('metrics', PortMetricsPortEntryIter, self._parent, self._choice)


class PortMetricsPortEntry(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'port_name': {'type': str},
        'meta': {'type': 'PortMeta'},
        'metrics': {'type': 'PortMetrics'},
    } # type: Dict[str, str]

    _REQUIRED = ('port_name', 'metrics') # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None, port_name=None):
        super(PortMetricsPortEntry, self).__init__()
        self._parent = parent
        self._set_property('port_name', port_name)

    @property
    def port_name(self):
        # type: () -> str
        """port_name getter

        Emulated port name

        Returns: str
        """
        return self._get_property('port_name')

    @port_name.setter
    def port_name(self, value):
        """port_name setter

        Emulated port name

        value: str
        """
        self._set_property('port_name', value)

    @property
    def meta(self):
        # type: () -> PortMeta
        """meta getter

        Port metadata.Port metadata.

        Returns: PortMeta
        """
        return self._get_property('meta', PortMeta)

    @property
    def metrics(self):
        # type: () -> PortMetrics
        """metrics getter

        Port metricsPort metrics

        Returns: PortMetrics
        """
        return self._get_property('metrics', PortMetrics)


class PortMeta(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'front_panel_port': {'type': int},
        'tx_switch': {'type': str},
        'rx_switch': {'type': str},
        'connected_to': {'type': str},
        'link_name': {'type': str},
        'annotations': {'type': str},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None, front_panel_port=None, tx_switch=None, rx_switch=None, connected_to=None, link_name=None, annotations=None):
        super(PortMeta, self).__init__()
        self._parent = parent
        self._set_property('front_panel_port', front_panel_port)
        self._set_property('tx_switch', tx_switch)
        self._set_property('rx_switch', rx_switch)
        self._set_property('connected_to', connected_to)
        self._set_property('link_name', link_name)
        self._set_property('annotations', annotations)

    @property
    def front_panel_port(self):
        # type: () -> int
        """front_panel_port getter

        The corresponding front panel port, if any.

        Returns: int
        """
        return self._get_property('front_panel_port')

    @front_panel_port.setter
    def front_panel_port(self, value):
        """front_panel_port setter

        The corresponding front panel port, if any.

        value: int
        """
        self._set_property('front_panel_port', value)

    @property
    def tx_switch(self):
        # type: () -> str
        """tx_switch getter

        The emulated device to which the port belongs to

        Returns: str
        """
        return self._get_property('tx_switch')

    @tx_switch.setter
    def tx_switch(self, value):
        """tx_switch setter

        The emulated device to which the port belongs to

        value: str
        """
        self._set_property('tx_switch', value)

    @property
    def rx_switch(self):
        # type: () -> str
        """rx_switch getter

        The emulated device to which the port is connected to

        Returns: str
        """
        return self._get_property('rx_switch')

    @rx_switch.setter
    def rx_switch(self, value):
        """rx_switch setter

        The emulated device to which the port is connected to

        value: str
        """
        self._set_property('rx_switch', value)

    @property
    def connected_to(self):
        # type: () -> str
        """connected_to getter

        The host to which a front-panel port is connected to

        Returns: str
        """
        return self._get_property('connected_to')

    @connected_to.setter
    def connected_to(self, value):
        """connected_to setter

        The host to which a front-panel port is connected to

        value: str
        """
        self._set_property('connected_to', value)

    @property
    def link_name(self):
        # type: () -> str
        """link_name getter

        Name of the emulated port link

        Returns: str
        """
        return self._get_property('link_name')

    @link_name.setter
    def link_name(self, value):
        """link_name setter

        Name of the emulated port link

        value: str
        """
        self._set_property('link_name', value)

    @property
    def annotations(self):
        # type: () -> str
        """annotations getter

        Other metadata

        Returns: str
        """
        return self._get_property('annotations')

    @annotations.setter
    def annotations(self, value):
        """annotations setter

        Other metadata

        value: str
        """
        self._set_property('annotations', value)


class PortMetrics(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'link_status': {
            'type': str,
            'enum': [
                'link_up',
                'link_down',
                'unknown',
            ],
        },
        'frames_transmitted_all': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_transmitted_multicast': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_transmitted_unicast': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_transmitted_broadcast': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_transmitted_length_64': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_transmitted_length_65_127': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_transmitted_length_128_255': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_transmitted_length_256_511': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_transmitted_length_512_1023': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_transmitted_length_1024_1518': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_transmitted_length_1519_2047': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_transmitted_length_2048_4095': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'bytes_transmitted_all': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_transmitted_ecn_marked': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_transmitted_priority_pause': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_transmitted_pause': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_received_all': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_received_multicast': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_received_unicast': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_received_broadcast': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_received_length_64': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_received_length_65_127': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_received_length_128_255': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_received_length_256_511': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_received_length_512_1023': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_received_length_1024_1518': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_received_length_1519_2047': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_received_length_2048_4095': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'bytes_received_all': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_received_errors': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_received_pause': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_received_priority_pause': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_dropped_egress': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'frames_dropped_ingress': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'per_egress_queue_metrics': {'type': 'PerEgressQueueMetricsIter'},
        'per_priority_group_metrics': {'type': 'PerPriorityGroupMetricsIter'},
        'flow_counter_metrics': {'type': 'FlowCounterMetrics'},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    LINK_UP = 'link_up' # type: str
    LINK_DOWN = 'link_down' # type: str
    UNKNOWN = 'unknown' # type: str

    def __init__(self, parent=None, link_status=None, frames_transmitted_all=None, frames_transmitted_multicast=None, frames_transmitted_unicast=None, frames_transmitted_broadcast=None, frames_transmitted_length_64=None, frames_transmitted_length_65_127=None, frames_transmitted_length_128_255=None, frames_transmitted_length_256_511=None, frames_transmitted_length_512_1023=None, frames_transmitted_length_1024_1518=None, frames_transmitted_length_1519_2047=None, frames_transmitted_length_2048_4095=None, bytes_transmitted_all=None, frames_transmitted_ecn_marked=None, frames_transmitted_priority_pause=None, frames_transmitted_pause=None, frames_received_all=None, frames_received_multicast=None, frames_received_unicast=None, frames_received_broadcast=None, frames_received_length_64=None, frames_received_length_65_127=None, frames_received_length_128_255=None, frames_received_length_256_511=None, frames_received_length_512_1023=None, frames_received_length_1024_1518=None, frames_received_length_1519_2047=None, frames_received_length_2048_4095=None, bytes_received_all=None, frames_received_errors=None, frames_received_pause=None, frames_received_priority_pause=None, frames_dropped_egress=None, frames_dropped_ingress=None):
        super(PortMetrics, self).__init__()
        self._parent = parent
        self._set_property('link_status', link_status)
        self._set_property('frames_transmitted_all', frames_transmitted_all)
        self._set_property('frames_transmitted_multicast', frames_transmitted_multicast)
        self._set_property('frames_transmitted_unicast', frames_transmitted_unicast)
        self._set_property('frames_transmitted_broadcast', frames_transmitted_broadcast)
        self._set_property('frames_transmitted_length_64', frames_transmitted_length_64)
        self._set_property('frames_transmitted_length_65_127', frames_transmitted_length_65_127)
        self._set_property('frames_transmitted_length_128_255', frames_transmitted_length_128_255)
        self._set_property('frames_transmitted_length_256_511', frames_transmitted_length_256_511)
        self._set_property('frames_transmitted_length_512_1023', frames_transmitted_length_512_1023)
        self._set_property('frames_transmitted_length_1024_1518', frames_transmitted_length_1024_1518)
        self._set_property('frames_transmitted_length_1519_2047', frames_transmitted_length_1519_2047)
        self._set_property('frames_transmitted_length_2048_4095', frames_transmitted_length_2048_4095)
        self._set_property('bytes_transmitted_all', bytes_transmitted_all)
        self._set_property('frames_transmitted_ecn_marked', frames_transmitted_ecn_marked)
        self._set_property('frames_transmitted_priority_pause', frames_transmitted_priority_pause)
        self._set_property('frames_transmitted_pause', frames_transmitted_pause)
        self._set_property('frames_received_all', frames_received_all)
        self._set_property('frames_received_multicast', frames_received_multicast)
        self._set_property('frames_received_unicast', frames_received_unicast)
        self._set_property('frames_received_broadcast', frames_received_broadcast)
        self._set_property('frames_received_length_64', frames_received_length_64)
        self._set_property('frames_received_length_65_127', frames_received_length_65_127)
        self._set_property('frames_received_length_128_255', frames_received_length_128_255)
        self._set_property('frames_received_length_256_511', frames_received_length_256_511)
        self._set_property('frames_received_length_512_1023', frames_received_length_512_1023)
        self._set_property('frames_received_length_1024_1518', frames_received_length_1024_1518)
        self._set_property('frames_received_length_1519_2047', frames_received_length_1519_2047)
        self._set_property('frames_received_length_2048_4095', frames_received_length_2048_4095)
        self._set_property('bytes_received_all', bytes_received_all)
        self._set_property('frames_received_errors', frames_received_errors)
        self._set_property('frames_received_pause', frames_received_pause)
        self._set_property('frames_received_priority_pause', frames_received_priority_pause)
        self._set_property('frames_dropped_egress', frames_dropped_egress)
        self._set_property('frames_dropped_ingress', frames_dropped_ingress)

    @property
    def link_status(self):
        # type: () -> Union[Literal["link_down"], Literal["link_up"], Literal["unknown"]]
        """link_status getter

        TBD

        Returns: Union[Literal["link_down"], Literal["link_up"], Literal["unknown"]]
        """
        return self._get_property('link_status')

    @link_status.setter
    def link_status(self, value):
        """link_status setter

        TBD

        value: Union[Literal["link_down"], Literal["link_up"], Literal["unknown"]]
        """
        self._set_property('link_status', value)

    @property
    def frames_transmitted_all(self):
        # type: () -> int
        """frames_transmitted_all getter

        TBD

        Returns: int
        """
        return self._get_property('frames_transmitted_all')

    @frames_transmitted_all.setter
    def frames_transmitted_all(self, value):
        """frames_transmitted_all setter

        TBD

        value: int
        """
        self._set_property('frames_transmitted_all', value)

    @property
    def frames_transmitted_multicast(self):
        # type: () -> int
        """frames_transmitted_multicast getter

        TBD

        Returns: int
        """
        return self._get_property('frames_transmitted_multicast')

    @frames_transmitted_multicast.setter
    def frames_transmitted_multicast(self, value):
        """frames_transmitted_multicast setter

        TBD

        value: int
        """
        self._set_property('frames_transmitted_multicast', value)

    @property
    def frames_transmitted_unicast(self):
        # type: () -> int
        """frames_transmitted_unicast getter

        TBD

        Returns: int
        """
        return self._get_property('frames_transmitted_unicast')

    @frames_transmitted_unicast.setter
    def frames_transmitted_unicast(self, value):
        """frames_transmitted_unicast setter

        TBD

        value: int
        """
        self._set_property('frames_transmitted_unicast', value)

    @property
    def frames_transmitted_broadcast(self):
        # type: () -> int
        """frames_transmitted_broadcast getter

        TBD

        Returns: int
        """
        return self._get_property('frames_transmitted_broadcast')

    @frames_transmitted_broadcast.setter
    def frames_transmitted_broadcast(self, value):
        """frames_transmitted_broadcast setter

        TBD

        value: int
        """
        self._set_property('frames_transmitted_broadcast', value)

    @property
    def frames_transmitted_length_64(self):
        # type: () -> int
        """frames_transmitted_length_64 getter

        TBD

        Returns: int
        """
        return self._get_property('frames_transmitted_length_64')

    @frames_transmitted_length_64.setter
    def frames_transmitted_length_64(self, value):
        """frames_transmitted_length_64 setter

        TBD

        value: int
        """
        self._set_property('frames_transmitted_length_64', value)

    @property
    def frames_transmitted_length_65_127(self):
        # type: () -> int
        """frames_transmitted_length_65_127 getter

        TBD

        Returns: int
        """
        return self._get_property('frames_transmitted_length_65_127')

    @frames_transmitted_length_65_127.setter
    def frames_transmitted_length_65_127(self, value):
        """frames_transmitted_length_65_127 setter

        TBD

        value: int
        """
        self._set_property('frames_transmitted_length_65_127', value)

    @property
    def frames_transmitted_length_128_255(self):
        # type: () -> int
        """frames_transmitted_length_128_255 getter

        TBD

        Returns: int
        """
        return self._get_property('frames_transmitted_length_128_255')

    @frames_transmitted_length_128_255.setter
    def frames_transmitted_length_128_255(self, value):
        """frames_transmitted_length_128_255 setter

        TBD

        value: int
        """
        self._set_property('frames_transmitted_length_128_255', value)

    @property
    def frames_transmitted_length_256_511(self):
        # type: () -> int
        """frames_transmitted_length_256_511 getter

        TBD

        Returns: int
        """
        return self._get_property('frames_transmitted_length_256_511')

    @frames_transmitted_length_256_511.setter
    def frames_transmitted_length_256_511(self, value):
        """frames_transmitted_length_256_511 setter

        TBD

        value: int
        """
        self._set_property('frames_transmitted_length_256_511', value)

    @property
    def frames_transmitted_length_512_1023(self):
        # type: () -> int
        """frames_transmitted_length_512_1023 getter

        TBD

        Returns: int
        """
        return self._get_property('frames_transmitted_length_512_1023')

    @frames_transmitted_length_512_1023.setter
    def frames_transmitted_length_512_1023(self, value):
        """frames_transmitted_length_512_1023 setter

        TBD

        value: int
        """
        self._set_property('frames_transmitted_length_512_1023', value)

    @property
    def frames_transmitted_length_1024_1518(self):
        # type: () -> int
        """frames_transmitted_length_1024_1518 getter

        TBD

        Returns: int
        """
        return self._get_property('frames_transmitted_length_1024_1518')

    @frames_transmitted_length_1024_1518.setter
    def frames_transmitted_length_1024_1518(self, value):
        """frames_transmitted_length_1024_1518 setter

        TBD

        value: int
        """
        self._set_property('frames_transmitted_length_1024_1518', value)

    @property
    def frames_transmitted_length_1519_2047(self):
        # type: () -> int
        """frames_transmitted_length_1519_2047 getter

        TBD

        Returns: int
        """
        return self._get_property('frames_transmitted_length_1519_2047')

    @frames_transmitted_length_1519_2047.setter
    def frames_transmitted_length_1519_2047(self, value):
        """frames_transmitted_length_1519_2047 setter

        TBD

        value: int
        """
        self._set_property('frames_transmitted_length_1519_2047', value)

    @property
    def frames_transmitted_length_2048_4095(self):
        # type: () -> int
        """frames_transmitted_length_2048_4095 getter

        TBD

        Returns: int
        """
        return self._get_property('frames_transmitted_length_2048_4095')

    @frames_transmitted_length_2048_4095.setter
    def frames_transmitted_length_2048_4095(self, value):
        """frames_transmitted_length_2048_4095 setter

        TBD

        value: int
        """
        self._set_property('frames_transmitted_length_2048_4095', value)

    @property
    def bytes_transmitted_all(self):
        # type: () -> int
        """bytes_transmitted_all getter

        TBD

        Returns: int
        """
        return self._get_property('bytes_transmitted_all')

    @bytes_transmitted_all.setter
    def bytes_transmitted_all(self, value):
        """bytes_transmitted_all setter

        TBD

        value: int
        """
        self._set_property('bytes_transmitted_all', value)

    @property
    def frames_transmitted_ecn_marked(self):
        # type: () -> int
        """frames_transmitted_ecn_marked getter

        TBD

        Returns: int
        """
        return self._get_property('frames_transmitted_ecn_marked')

    @frames_transmitted_ecn_marked.setter
    def frames_transmitted_ecn_marked(self, value):
        """frames_transmitted_ecn_marked setter

        TBD

        value: int
        """
        self._set_property('frames_transmitted_ecn_marked', value)

    @property
    def frames_transmitted_priority_pause(self):
        # type: () -> int
        """frames_transmitted_priority_pause getter

        TBD

        Returns: int
        """
        return self._get_property('frames_transmitted_priority_pause')

    @frames_transmitted_priority_pause.setter
    def frames_transmitted_priority_pause(self, value):
        """frames_transmitted_priority_pause setter

        TBD

        value: int
        """
        self._set_property('frames_transmitted_priority_pause', value)

    @property
    def frames_transmitted_pause(self):
        # type: () -> int
        """frames_transmitted_pause getter

        TBD

        Returns: int
        """
        return self._get_property('frames_transmitted_pause')

    @frames_transmitted_pause.setter
    def frames_transmitted_pause(self, value):
        """frames_transmitted_pause setter

        TBD

        value: int
        """
        self._set_property('frames_transmitted_pause', value)

    @property
    def frames_received_all(self):
        # type: () -> int
        """frames_received_all getter

        TBD

        Returns: int
        """
        return self._get_property('frames_received_all')

    @frames_received_all.setter
    def frames_received_all(self, value):
        """frames_received_all setter

        TBD

        value: int
        """
        self._set_property('frames_received_all', value)

    @property
    def frames_received_multicast(self):
        # type: () -> int
        """frames_received_multicast getter

        TBD

        Returns: int
        """
        return self._get_property('frames_received_multicast')

    @frames_received_multicast.setter
    def frames_received_multicast(self, value):
        """frames_received_multicast setter

        TBD

        value: int
        """
        self._set_property('frames_received_multicast', value)

    @property
    def frames_received_unicast(self):
        # type: () -> int
        """frames_received_unicast getter

        TBD

        Returns: int
        """
        return self._get_property('frames_received_unicast')

    @frames_received_unicast.setter
    def frames_received_unicast(self, value):
        """frames_received_unicast setter

        TBD

        value: int
        """
        self._set_property('frames_received_unicast', value)

    @property
    def frames_received_broadcast(self):
        # type: () -> int
        """frames_received_broadcast getter

        TBD

        Returns: int
        """
        return self._get_property('frames_received_broadcast')

    @frames_received_broadcast.setter
    def frames_received_broadcast(self, value):
        """frames_received_broadcast setter

        TBD

        value: int
        """
        self._set_property('frames_received_broadcast', value)

    @property
    def frames_received_length_64(self):
        # type: () -> int
        """frames_received_length_64 getter

        TBD

        Returns: int
        """
        return self._get_property('frames_received_length_64')

    @frames_received_length_64.setter
    def frames_received_length_64(self, value):
        """frames_received_length_64 setter

        TBD

        value: int
        """
        self._set_property('frames_received_length_64', value)

    @property
    def frames_received_length_65_127(self):
        # type: () -> int
        """frames_received_length_65_127 getter

        TBD

        Returns: int
        """
        return self._get_property('frames_received_length_65_127')

    @frames_received_length_65_127.setter
    def frames_received_length_65_127(self, value):
        """frames_received_length_65_127 setter

        TBD

        value: int
        """
        self._set_property('frames_received_length_65_127', value)

    @property
    def frames_received_length_128_255(self):
        # type: () -> int
        """frames_received_length_128_255 getter

        TBD

        Returns: int
        """
        return self._get_property('frames_received_length_128_255')

    @frames_received_length_128_255.setter
    def frames_received_length_128_255(self, value):
        """frames_received_length_128_255 setter

        TBD

        value: int
        """
        self._set_property('frames_received_length_128_255', value)

    @property
    def frames_received_length_256_511(self):
        # type: () -> int
        """frames_received_length_256_511 getter

        TBD

        Returns: int
        """
        return self._get_property('frames_received_length_256_511')

    @frames_received_length_256_511.setter
    def frames_received_length_256_511(self, value):
        """frames_received_length_256_511 setter

        TBD

        value: int
        """
        self._set_property('frames_received_length_256_511', value)

    @property
    def frames_received_length_512_1023(self):
        # type: () -> int
        """frames_received_length_512_1023 getter

        TBD

        Returns: int
        """
        return self._get_property('frames_received_length_512_1023')

    @frames_received_length_512_1023.setter
    def frames_received_length_512_1023(self, value):
        """frames_received_length_512_1023 setter

        TBD

        value: int
        """
        self._set_property('frames_received_length_512_1023', value)

    @property
    def frames_received_length_1024_1518(self):
        # type: () -> int
        """frames_received_length_1024_1518 getter

        TBD

        Returns: int
        """
        return self._get_property('frames_received_length_1024_1518')

    @frames_received_length_1024_1518.setter
    def frames_received_length_1024_1518(self, value):
        """frames_received_length_1024_1518 setter

        TBD

        value: int
        """
        self._set_property('frames_received_length_1024_1518', value)

    @property
    def frames_received_length_1519_2047(self):
        # type: () -> int
        """frames_received_length_1519_2047 getter

        TBD

        Returns: int
        """
        return self._get_property('frames_received_length_1519_2047')

    @frames_received_length_1519_2047.setter
    def frames_received_length_1519_2047(self, value):
        """frames_received_length_1519_2047 setter

        TBD

        value: int
        """
        self._set_property('frames_received_length_1519_2047', value)

    @property
    def frames_received_length_2048_4095(self):
        # type: () -> int
        """frames_received_length_2048_4095 getter

        TBD

        Returns: int
        """
        return self._get_property('frames_received_length_2048_4095')

    @frames_received_length_2048_4095.setter
    def frames_received_length_2048_4095(self, value):
        """frames_received_length_2048_4095 setter

        TBD

        value: int
        """
        self._set_property('frames_received_length_2048_4095', value)

    @property
    def bytes_received_all(self):
        # type: () -> int
        """bytes_received_all getter

        TBD

        Returns: int
        """
        return self._get_property('bytes_received_all')

    @bytes_received_all.setter
    def bytes_received_all(self, value):
        """bytes_received_all setter

        TBD

        value: int
        """
        self._set_property('bytes_received_all', value)

    @property
    def frames_received_errors(self):
        # type: () -> int
        """frames_received_errors getter

        TBD

        Returns: int
        """
        return self._get_property('frames_received_errors')

    @frames_received_errors.setter
    def frames_received_errors(self, value):
        """frames_received_errors setter

        TBD

        value: int
        """
        self._set_property('frames_received_errors', value)

    @property
    def frames_received_pause(self):
        # type: () -> int
        """frames_received_pause getter

        TBD

        Returns: int
        """
        return self._get_property('frames_received_pause')

    @frames_received_pause.setter
    def frames_received_pause(self, value):
        """frames_received_pause setter

        TBD

        value: int
        """
        self._set_property('frames_received_pause', value)

    @property
    def frames_received_priority_pause(self):
        # type: () -> int
        """frames_received_priority_pause getter

        TBD

        Returns: int
        """
        return self._get_property('frames_received_priority_pause')

    @frames_received_priority_pause.setter
    def frames_received_priority_pause(self, value):
        """frames_received_priority_pause setter

        TBD

        value: int
        """
        self._set_property('frames_received_priority_pause', value)

    @property
    def frames_dropped_egress(self):
        # type: () -> int
        """frames_dropped_egress getter

        TBD

        Returns: int
        """
        return self._get_property('frames_dropped_egress')

    @frames_dropped_egress.setter
    def frames_dropped_egress(self, value):
        """frames_dropped_egress setter

        TBD

        value: int
        """
        self._set_property('frames_dropped_egress', value)

    @property
    def frames_dropped_ingress(self):
        # type: () -> int
        """frames_dropped_ingress getter

        TBD

        Returns: int
        """
        return self._get_property('frames_dropped_ingress')

    @frames_dropped_ingress.setter
    def frames_dropped_ingress(self, value):
        """frames_dropped_ingress setter

        TBD

        value: int
        """
        self._set_property('frames_dropped_ingress', value)

    @property
    def per_egress_queue_metrics(self):
        # type: () -> PerEgressQueueMetricsIter
        """per_egress_queue_metrics getter

        TBD

        Returns: PerEgressQueueMetricsIter
        """
        return self._get_property('per_egress_queue_metrics', PerEgressQueueMetricsIter, self._parent, self._choice)

    @property
    def per_priority_group_metrics(self):
        # type: () -> PerPriorityGroupMetricsIter
        """per_priority_group_metrics getter

        TBD

        Returns: PerPriorityGroupMetricsIter
        """
        return self._get_property('per_priority_group_metrics', PerPriorityGroupMetricsIter, self._parent, self._choice)

    @property
    def flow_counter_metrics(self):
        # type: () -> FlowCounterMetrics
        """flow_counter_metrics getter

        

        Returns: FlowCounterMetrics
        """
        return self._get_property('flow_counter_metrics', FlowCounterMetrics)


class PerEgressQueueMetrics(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'queue_number': {
            'type': int,
            'minimum': 0,
        },
        'egress_buffer_reserved_usage_current': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'egress_buffer_total_usage_peak': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'multicast_buffer_total_usage_peak': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
    } # type: Dict[str, str]

    _REQUIRED = ('queue_number',) # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None, queue_number=None, egress_buffer_reserved_usage_current=None, egress_buffer_total_usage_peak=None, multicast_buffer_total_usage_peak=None):
        super(PerEgressQueueMetrics, self).__init__()
        self._parent = parent
        self._set_property('queue_number', queue_number)
        self._set_property('egress_buffer_reserved_usage_current', egress_buffer_reserved_usage_current)
        self._set_property('egress_buffer_total_usage_peak', egress_buffer_total_usage_peak)
        self._set_property('multicast_buffer_total_usage_peak', multicast_buffer_total_usage_peak)

    @property
    def queue_number(self):
        # type: () -> int
        """queue_number getter

        TBD

        Returns: int
        """
        return self._get_property('queue_number')

    @queue_number.setter
    def queue_number(self, value):
        """queue_number setter

        TBD

        value: int
        """
        self._set_property('queue_number', value)

    @property
    def egress_buffer_reserved_usage_current(self):
        # type: () -> int
        """egress_buffer_reserved_usage_current getter

        TBD

        Returns: int
        """
        return self._get_property('egress_buffer_reserved_usage_current')

    @egress_buffer_reserved_usage_current.setter
    def egress_buffer_reserved_usage_current(self, value):
        """egress_buffer_reserved_usage_current setter

        TBD

        value: int
        """
        self._set_property('egress_buffer_reserved_usage_current', value)

    @property
    def egress_buffer_total_usage_peak(self):
        # type: () -> int
        """egress_buffer_total_usage_peak getter

        TBD

        Returns: int
        """
        return self._get_property('egress_buffer_total_usage_peak')

    @egress_buffer_total_usage_peak.setter
    def egress_buffer_total_usage_peak(self, value):
        """egress_buffer_total_usage_peak setter

        TBD

        value: int
        """
        self._set_property('egress_buffer_total_usage_peak', value)

    @property
    def multicast_buffer_total_usage_peak(self):
        # type: () -> int
        """multicast_buffer_total_usage_peak getter

        TBD

        Returns: int
        """
        return self._get_property('multicast_buffer_total_usage_peak')

    @multicast_buffer_total_usage_peak.setter
    def multicast_buffer_total_usage_peak(self, value):
        """multicast_buffer_total_usage_peak setter

        TBD

        value: int
        """
        self._set_property('multicast_buffer_total_usage_peak', value)


class PerEgressQueueMetricsIter(OpenApiIter):
    __slots__ = ('_parent', '_choice')

    _GETITEM_RETURNS_CHOICE_OBJECT = False

    def __init__(self, parent=None, choice=None):
        super(PerEgressQueueMetricsIter, self).__init__()
        self._parent = parent
        self._choice = choice

    def __getitem__(self, key):
        # type: (str) -> Union[PerEgressQueueMetrics]
        return self._getitem(key)

    def __iter__(self):
        # type: () -> PerEgressQueueMetricsIter
        return self._iter()

    def __next__(self):
        # type: () -> PerEgressQueueMetrics
        return self._next()

    def next(self):
        # type: () -> PerEgressQueueMetrics
        return self._next()

    def peregressqueuemetrics(self, queue_number=None, egress_buffer_reserved_usage_current=None, egress_buffer_total_usage_peak=None, multicast_buffer_total_usage_peak=None):
        # type: (int,int,int,int) -> PerEgressQueueMetricsIter
        """Factory method that creates an instance of the PerEgressQueueMetrics class

        TBD

        Returns: PerEgressQueueMetricsIter
        """
        item = PerEgressQueueMetrics(parent=self._parent, queue_number=queue_number, egress_buffer_reserved_usage_current=egress_buffer_reserved_usage_current, egress_buffer_total_usage_peak=egress_buffer_total_usage_peak, multicast_buffer_total_usage_peak=multicast_buffer_total_usage_peak)
        self._add(item)
        return self

    def add(self, queue_number=None, egress_buffer_reserved_usage_current=None, egress_buffer_total_usage_peak=None, multicast_buffer_total_usage_peak=None):
        # type: (int,int,int,int) -> PerEgressQueueMetrics
        """Add method that creates and returns an instance of the PerEgressQueueMetrics class

        TBD

        Returns: PerEgressQueueMetrics
        """
        item = PerEgressQueueMetrics(parent=self._parent, queue_number=queue_number, egress_buffer_reserved_usage_current=egress_buffer_reserved_usage_current, egress_buffer_total_usage_peak=egress_buffer_total_usage_peak, multicast_buffer_total_usage_peak=multicast_buffer_total_usage_peak)
        self._add(item)
        return item


class PerPriorityGroupMetrics(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'priority_group': {
            'type': int,
            'minimum': 0,
        },
        'ingress_buffer_reserved_usage_current': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
        'ingress_buffer_shared_usage_peak': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
    } # type: Dict[str, str]

    _REQUIRED = ('priority_group',) # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None, priority_group=None, ingress_buffer_reserved_usage_current=None, ingress_buffer_shared_usage_peak=None):
        super(PerPriorityGroupMetrics, self).__init__()
        self._parent = parent
        self._set_property('priority_group', priority_group)
        self._set_property('ingress_buffer_reserved_usage_current', ingress_buffer_reserved_usage_current)
        self._set_property('ingress_buffer_shared_usage_peak', ingress_buffer_shared_usage_peak)

    @property
    def priority_group(self):
        # type: () -> int
        """priority_group getter

        TBD

        Returns: int
        """
        return self._get_property('priority_group')

    @priority_group.setter
    def priority_group(self, value):
        """priority_group setter

        TBD

        value: int
        """
        self._set_property('priority_group', value)

    @property
    def ingress_buffer_reserved_usage_current(self):
        # type: () -> int
        """ingress_buffer_reserved_usage_current getter

        TBD

        Returns: int
        """
        return self._get_property('ingress_buffer_reserved_usage_current')

    @ingress_buffer_reserved_usage_current.setter
    def ingress_buffer_reserved_usage_current(self, value):
        """ingress_buffer_reserved_usage_current setter

        TBD

        value: int
        """
        self._set_property('ingress_buffer_reserved_usage_current', value)

    @property
    def ingress_buffer_shared_usage_peak(self):
        # type: () -> int
        """ingress_buffer_shared_usage_peak getter

        TBD

        Returns: int
        """
        return self._get_property('ingress_buffer_shared_usage_peak')

    @ingress_buffer_shared_usage_peak.setter
    def ingress_buffer_shared_usage_peak(self, value):
        """ingress_buffer_shared_usage_peak setter

        TBD

        value: int
        """
        self._set_property('ingress_buffer_shared_usage_peak', value)


class PerPriorityGroupMetricsIter(OpenApiIter):
    __slots__ = ('_parent', '_choice')

    _GETITEM_RETURNS_CHOICE_OBJECT = False

    def __init__(self, parent=None, choice=None):
        super(PerPriorityGroupMetricsIter, self).__init__()
        self._parent = parent
        self._choice = choice

    def __getitem__(self, key):
        # type: (str) -> Union[PerPriorityGroupMetrics]
        return self._getitem(key)

    def __iter__(self):
        # type: () -> PerPriorityGroupMetricsIter
        return self._iter()

    def __next__(self):
        # type: () -> PerPriorityGroupMetrics
        return self._next()

    def next(self):
        # type: () -> PerPriorityGroupMetrics
        return self._next()

    def perprioritygroupmetrics(self, priority_group=None, ingress_buffer_reserved_usage_current=None, ingress_buffer_shared_usage_peak=None):
        # type: (int,int,int) -> PerPriorityGroupMetricsIter
        """Factory method that creates an instance of the PerPriorityGroupMetrics class

        TBD

        Returns: PerPriorityGroupMetricsIter
        """
        item = PerPriorityGroupMetrics(parent=self._parent, priority_group=priority_group, ingress_buffer_reserved_usage_current=ingress_buffer_reserved_usage_current, ingress_buffer_shared_usage_peak=ingress_buffer_shared_usage_peak)
        self._add(item)
        return self

    def add(self, priority_group=None, ingress_buffer_reserved_usage_current=None, ingress_buffer_shared_usage_peak=None):
        # type: (int,int,int) -> PerPriorityGroupMetrics
        """Add method that creates and returns an instance of the PerPriorityGroupMetrics class

        TBD

        Returns: PerPriorityGroupMetrics
        """
        item = PerPriorityGroupMetrics(parent=self._parent, priority_group=priority_group, ingress_buffer_reserved_usage_current=ingress_buffer_reserved_usage_current, ingress_buffer_shared_usage_peak=ingress_buffer_shared_usage_peak)
        self._add(item)
        return item


class FlowCounterMetrics(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'per_background_traffic_flow': {'type': 'FlowCounterMetricsPerBackgroundTrafficFlowIter'},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None):
        super(FlowCounterMetrics, self).__init__()
        self._parent = parent

    @property
    def per_background_traffic_flow(self):
        # type: () -> FlowCounterMetricsPerBackgroundTrafficFlowIter
        """per_background_traffic_flow getter

        TBD

        Returns: FlowCounterMetricsPerBackgroundTrafficFlowIter
        """
        return self._get_property('per_background_traffic_flow', FlowCounterMetricsPerBackgroundTrafficFlowIter, self._parent, self._choice)


class FlowCounterMetricsPerBackgroundTrafficFlow(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'flow_name': {'type': str},
        'frames_transmitted': {
            'type': int,
            'format': 'int64',
            'minimum': 0,
        },
    } # type: Dict[str, str]

    _REQUIRED = ('flow_name',) # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None, flow_name=None, frames_transmitted=None):
        super(FlowCounterMetricsPerBackgroundTrafficFlow, self).__init__()
        self._parent = parent
        self._set_property('flow_name', flow_name)
        self._set_property('frames_transmitted', frames_transmitted)

    @property
    def flow_name(self):
        # type: () -> str
        """flow_name getter

        TBD

        Returns: str
        """
        return self._get_property('flow_name')

    @flow_name.setter
    def flow_name(self, value):
        """flow_name setter

        TBD

        value: str
        """
        self._set_property('flow_name', value)

    @property
    def frames_transmitted(self):
        # type: () -> int
        """frames_transmitted getter

        TBD

        Returns: int
        """
        return self._get_property('frames_transmitted')

    @frames_transmitted.setter
    def frames_transmitted(self, value):
        """frames_transmitted setter

        TBD

        value: int
        """
        self._set_property('frames_transmitted', value)


class FlowCounterMetricsPerBackgroundTrafficFlowIter(OpenApiIter):
    __slots__ = ('_parent', '_choice')

    _GETITEM_RETURNS_CHOICE_OBJECT = False

    def __init__(self, parent=None, choice=None):
        super(FlowCounterMetricsPerBackgroundTrafficFlowIter, self).__init__()
        self._parent = parent
        self._choice = choice

    def __getitem__(self, key):
        # type: (str) -> Union[FlowCounterMetricsPerBackgroundTrafficFlow]
        return self._getitem(key)

    def __iter__(self):
        # type: () -> FlowCounterMetricsPerBackgroundTrafficFlowIter
        return self._iter()

    def __next__(self):
        # type: () -> FlowCounterMetricsPerBackgroundTrafficFlow
        return self._next()

    def next(self):
        # type: () -> FlowCounterMetricsPerBackgroundTrafficFlow
        return self._next()

    def perbackgroundtrafficflow(self, flow_name=None, frames_transmitted=None):
        # type: (str,int) -> FlowCounterMetricsPerBackgroundTrafficFlowIter
        """Factory method that creates an instance of the FlowCounterMetricsPerBackgroundTrafficFlow class

        TBD

        Returns: FlowCounterMetricsPerBackgroundTrafficFlowIter
        """
        item = FlowCounterMetricsPerBackgroundTrafficFlow(parent=self._parent, flow_name=flow_name, frames_transmitted=frames_transmitted)
        self._add(item)
        return self

    def add(self, flow_name=None, frames_transmitted=None):
        # type: (str,int) -> FlowCounterMetricsPerBackgroundTrafficFlow
        """Add method that creates and returns an instance of the FlowCounterMetricsPerBackgroundTrafficFlow class

        TBD

        Returns: FlowCounterMetricsPerBackgroundTrafficFlow
        """
        item = FlowCounterMetricsPerBackgroundTrafficFlow(parent=self._parent, flow_name=flow_name, frames_transmitted=frames_transmitted)
        self._add(item)
        return item


class PortMetricsPortEntryIter(OpenApiIter):
    __slots__ = ('_parent', '_choice')

    _GETITEM_RETURNS_CHOICE_OBJECT = False

    def __init__(self, parent=None, choice=None):
        super(PortMetricsPortEntryIter, self).__init__()
        self._parent = parent
        self._choice = choice

    def __getitem__(self, key):
        # type: (str) -> Union[PortMetricsPortEntry]
        return self._getitem(key)

    def __iter__(self):
        # type: () -> PortMetricsPortEntryIter
        return self._iter()

    def __next__(self):
        # type: () -> PortMetricsPortEntry
        return self._next()

    def next(self):
        # type: () -> PortMetricsPortEntry
        return self._next()

    def portentry(self, port_name=None):
        # type: (str) -> PortMetricsPortEntryIter
        """Factory method that creates an instance of the PortMetricsPortEntry class

        TBD

        Returns: PortMetricsPortEntryIter
        """
        item = PortMetricsPortEntry(parent=self._parent, port_name=port_name)
        self._add(item)
        return self

    def add(self, port_name=None):
        # type: (str) -> PortMetricsPortEntry
        """Add method that creates and returns an instance of the PortMetricsPortEntry class

        TBD

        Returns: PortMetricsPortEntry
        """
        item = PortMetricsPortEntry(parent=self._parent, port_name=port_name)
        self._add(item)
        return item


class Api(object):
    """OpenApi Abstract API
    """

    def __init__(self, **kwargs):
        pass

    def set_config(self, payload):
        """PUT /onex/api/v1/config

        Sets the ONEx configuration.

        Return: error_details
        """
        raise NotImplementedError("set_config")

    def get_config(self):
        """GET /onex/api/v1/config

        Gets the ONEx configuration.

        Return: config
        """
        raise NotImplementedError("get_config")

    def set_state(self, payload):
        """PUT /onex/api/v1/state

        Updates the state of ONEx configured experiment(s).

        Return: error_details
        """
        raise NotImplementedError("set_state")

    def get_state(self):
        """GET /onex/api/v1/state

        Gets the state of ONEx configured experiments.

        Return: state
        """
        raise NotImplementedError("get_state")

    def get_metrics(self, payload):
        """POST /onex/api/v1/fabric/metrics/operations/query

        Gets the requested fabric metrics.

        Return: metrics_response
        """
        raise NotImplementedError("get_metrics")

    def clear_metrics(self):
        """POST /onex/api/v1/fabric/metrics/operations/clear

        Clear the metrics.

        Return: error_details
        """
        raise NotImplementedError("clear_metrics")

    def config(self):
        """Factory method that creates an instance of Config

        Return: Config
        """
        return Config()

    def error_details(self):
        """Factory method that creates an instance of ErrorDetails

        Return: ErrorDetails
        """
        return ErrorDetails()

    def state(self):
        """Factory method that creates an instance of State

        Return: State
        """
        return State()

    def metrics_request(self):
        """Factory method that creates an instance of MetricsRequest

        Return: MetricsRequest
        """
        return MetricsRequest()

    def metrics_response(self):
        """Factory method that creates an instance of MetricsResponse

        Return: MetricsResponse
        """
        return MetricsResponse()


class HttpApi(Api):
    """OpenAPI HTTP Api
    """
    def __init__(self, **kwargs):
        super(HttpApi, self).__init__(**kwargs)
        self._transport = HttpTransport(**kwargs)

    def set_config(self, payload):
        """PUT /onex/api/v1/config

        Sets the ONEx configuration.

        Return: error_details
        """
        return self._transport.send_recv(
            "put",
            "/onex/api/v1/config",
            payload=payload,
            return_object=self.error_details(),
        )

    def get_config(self):
        """GET /onex/api/v1/config

        Gets the ONEx configuration.

        Return: config
        """
        return self._transport.send_recv(
            "get",
            "/onex/api/v1/config",
            payload=None,
            return_object=self.config(),
        )

    def set_state(self, payload):
        """PUT /onex/api/v1/state

        Updates the state of ONEx configured experiment(s).

        Return: error_details
        """
        return self._transport.send_recv(
            "put",
            "/onex/api/v1/state",
            payload=payload,
            return_object=self.error_details(),
        )

    def get_state(self):
        """GET /onex/api/v1/state

        Gets the state of ONEx configured experiments.

        Return: state
        """
        return self._transport.send_recv(
            "get",
            "/onex/api/v1/state",
            payload=None,
            return_object=self.state(),
        )

    def get_metrics(self, payload):
        """POST /onex/api/v1/fabric/metrics/operations/query

        Gets the requested fabric metrics.

        Return: metrics_response
        """
        return self._transport.send_recv(
            "post",
            "/onex/api/v1/fabric/metrics/operations/query",
            payload=payload,
            return_object=self.metrics_response(),
        )

    def clear_metrics(self):
        """POST /onex/api/v1/fabric/metrics/operations/clear

        Clear the metrics.

        Return: error_details
        """
        return self._transport.send_recv(
            "post",
            "/onex/api/v1/fabric/metrics/operations/clear",
            payload=None,
            return_object=self.error_details(),
        )
