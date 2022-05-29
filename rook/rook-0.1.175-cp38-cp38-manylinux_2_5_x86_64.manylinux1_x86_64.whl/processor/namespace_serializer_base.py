import datetime
import decimal
from types import FunctionType, MethodType, ModuleType

import six

if six.PY2:
    from types import TypeType

from google.protobuf.descriptor import Descriptor as google_descriptor

try:
    import numpy
except ImportError:
    numpy = None

try:
    import torch
except ImportError:
    torch = None

try:
    import multidict
except ImportError:
    multidict = None


class NamespaceSerializerBase(object):
    BUILTIN_ATTRIBUTES_IGNORE = {
        '__dict__',
        '__module__',
        '__weakref__',
        '__name__',
        '__doc__',
        '__qualname__',
        '__spec__',
        '__defaults__',
        '__code__',
        '__globals__',
        '__closure__',
        '__annotations__',
        '__kwdefaults__',
        '__bases__'}

    try:
        BINARY_TYPES = (buffer, bytearray)
        CODE_TYPES = (FunctionType, MethodType, TypeType, ModuleType, six.MovedModule)
        PRIMITIVE_TYPES = (type(None), int, long, float, str, unicode, complex, decimal.Decimal) + BINARY_TYPES + CODE_TYPES + (datetime.datetime,)

    except NameError:
        BINARY_TYPES = (bytearray, bytes)
        CODE_TYPES = (FunctionType, MethodType, type, ModuleType, six.MovedModule)
        PRIMITIVE_TYPES = (type(None), int, float, str, complex, decimal.Decimal) + BINARY_TYPES + CODE_TYPES + (datetime.datetime,)

    def __init__(self, use_string_cache=False):
        self.use_string_cache = use_string_cache
        self.string_cache = {}

        if use_string_cache:
            # Lock the 0 index since some variant will have no originalType (container for example)
            self.string_cache[""] = 0

        self.estimated_pending_bytes = 0

    def get_string_cache(self):
        return self.string_cache

    def get_estimated_pending_bytes(self):
        return self.estimated_pending_bytes

    def _get_string_index_in_cache(self, str):
        if str in self.string_cache:
            return self.string_cache[str]

        current_size = len(self.string_cache)
        # We estimate each character is one byte in utf-8 and overhead is 5 bytes
        self.estimated_pending_bytes += len(str) + 5
        self.string_cache[str] = current_size
        return current_size

    @staticmethod
    def _get_object_width(obj):
        object_width = 0
        if hasattr(obj, '__dict__') and obj.__dict__:
            object_width += len(obj.__dict__)
        if hasattr(obj, '__slots__') and obj.__slots__:
            object_width += len(obj.__slots__)
        return object_width


    @staticmethod
    def normalize_string(obj):
        if six.PY2:
            if isinstance(obj, str):
                return unicode(obj, errors="replace")
            else:
                return unicode(obj)
        else:
            return str(obj)

    @staticmethod
    def is_numpy_obj(obj):
        if not numpy:
            return False

        return not isinstance(obj, six.MovedModule) and isinstance(obj, numpy.generic)

    @staticmethod
    def is_torch_obj(obj):
        if not torch:
            return False

        module = getattr(type(obj), '__module__', None)
        if not module:
            return False

        return module.startswith('torch')

    @staticmethod
    def is_multidict_obj(obj):
        if not multidict or isinstance(obj, six.MovedModule) or not hasattr(multidict, '_multidict'):
            return False

        return isinstance(obj, (multidict._multidict.MultiDict, multidict._multidict.CIMultiDict, multidict._multidict.MultiDictProxy, multidict._multidict.CIMultiDictProxy))

    @staticmethod
    def is_protobuf_obj(obj):
        if not isinstance(obj, six.MovedModule) and hasattr(obj, "DESCRIPTOR"):
            return isinstance(obj.DESCRIPTOR, google_descriptor)

        return False
