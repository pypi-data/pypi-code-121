import six
import datetime

from .namespace import Namespace

from rook.exceptions import RookKeyNotFound, RookAttributeNotFound, RookInvalidMethodArguments


class PythonObjectNamespace(Namespace):
    try:
        BINARY_TYPES = (buffer, bytearray)
    except NameError:
        BINARY_TYPES = (bytearray, bytes)

    class ObjectDumpConfig(object):

        STRICT_MAX_DEPTH = 2
        STRICT_MAX_WIDTH = 10
        STRICT_MAX_COLLECTION_DEPTH = 2
        STRICT_MAX_STRING = 128

        DEFAULT_MAX_DEPTH = 4
        DEFAULT_MAX_WIDTH = 10
        DEFAULT_MAX_COLLECTION_DEPTH = 4
        DEFAULT_MAX_STRING = 512

        TOLERANT_MAX_DEPTH = 5
        TOLERANT_MAX_WIDTH = 20
        TOLERANT_MAX_COLLECTION_DEPTH = 5
        TOLERANT_MAX_STRING = 4 * 1024

        UNLIMITED_STRING = 64 * 1024
        UNLIMITED_COLLECTION_WIDTH = 100

        def __init__(self, max_depth=None, max_width=None, max_collection_dump=None, max_string=None):
            self.max_depth = max_depth or self.DEFAULT_MAX_DEPTH
            self.max_width = max_width or self.DEFAULT_MAX_WIDTH
            self.max_collection_dump = max_collection_dump or self.DEFAULT_MAX_COLLECTION_DEPTH
            self.max_string = max_string or self.DEFAULT_MAX_STRING

        def __eq__(self, other):
            return type(self) == type(other) and self.max_depth == other.max_depth and \
                   self.max_width == other.max_width and self.max_collection_dump == other.max_collection_dump and \
                   self.max_string == other.max_string

        @classmethod
        def strict_limits(cls, obj):
            return cls(
                cls.STRICT_MAX_DEPTH,
                cls.STRICT_MAX_WIDTH,
                cls.STRICT_MAX_COLLECTION_DEPTH,
                cls.STRICT_MAX_STRING)

        @classmethod
        def default_limits(cls, obj):
            return cls(
                cls.DEFAULT_MAX_DEPTH,
                cls.DEFAULT_MAX_WIDTH,
                cls.DEFAULT_MAX_COLLECTION_DEPTH,
                cls.DEFAULT_MAX_STRING)

        @classmethod
        def tolerant_limits(cls, obj):
            return cls(
                cls.TOLERANT_MAX_DEPTH,
                cls.TOLERANT_MAX_WIDTH,
                cls.TOLERANT_MAX_COLLECTION_DEPTH,
                cls.TOLERANT_MAX_STRING)

        @classmethod
        def tailor_limits(cls, obj):
            if isinstance(obj, six.string_types):
                return PythonObjectNamespace.ObjectDumpConfig(1, 0, 0, cls.UNLIMITED_STRING)
            if isinstance(obj, (list, dict, set, tuple)) and len(obj) > cls.TOLERANT_MAX_WIDTH:
                return PythonObjectNamespace.ObjectDumpConfig(max_width=cls.UNLIMITED_COLLECTION_WIDTH)
            else:
                return PythonObjectNamespace.ObjectDumpConfig.tolerant_limits(obj)

    def __init__(self, obj, dump_config=None, methods=()):
        super(PythonObjectNamespace, self).__init__(methods + self.METHODS)
        self.obj = obj
        self.dump_config = dump_config or self.ObjectDumpConfig()

    @classmethod
    def get_common_type(cls, obj):
        # NOTE: This list is partially duplicated with the list in NamespaceSerializer._load_variant
        if obj is None:
            return u'null'
        elif isinstance(obj, six.integer_types):
            return u'int'
        elif isinstance(obj, six.string_types):
            return u'string'
        elif isinstance(obj, float):
            return u'float'
        elif isinstance(obj, cls.BINARY_TYPES):
            return u'buffer'
        elif isinstance(obj, datetime.datetime):
            return u'datetime'
        elif isinstance(obj, (list, set, tuple)):
            from .collection_namespace import ListNamespace
            return ListNamespace.get_common_type(obj)
        elif isinstance(obj, (dict)):
            return u'dict'
        elif isinstance(obj, complex):
            return u'complex'
        else:
            raise ValueError("Unknown type- %s", str(type(obj)))

    def read_attribute(self, name):
        try:
            if hasattr(self.obj, '__dict__') and self.obj.__dict__ and name in self.obj.__dict__:
                return PythonObjectNamespace(self.obj.__dict__[name])
            if hasattr(self.obj, '__slots__') and self.obj.__slots__ and name in self.obj.__slots__:
                return PythonObjectNamespace(self.obj.__slots__[name])

            raise RookAttributeNotFound(name)
        except AttributeError:
            raise RookAttributeNotFound(name)

    def read_key(self, key):
        try:
            return PythonObjectNamespace(self.obj[key])
        except (KeyError, IndexError, TypeError):
            # If key is a string and object is a dictionary check if any key within the dictionary stringifies to key
            if isinstance(key, six.string_types) and isinstance(self.obj, dict):
                for iteratorKey in self.obj:
                    if str(iteratorKey) == key:  # The str() is the important part
                        return PythonObjectNamespace(self.obj[iteratorKey])

            raise RookKeyNotFound(key)

    def type(self, args=None):
        return PythonObjectNamespace(self.serialize_type())

    def serialize_type(self):
        return str(type(self.obj))

    def size(self, args=None):
        return PythonObjectNamespace(len(self.obj))

    def depth(self, args):
        try:
            self.dump_config.max_depth = int(args)
        except ValueError:
            raise RookInvalidMethodArguments('depth()', args)

        return self

    def width(self, args):
        try:
            self.dump_config.max_width = int(args)
        except ValueError:
            raise RookInvalidMethodArguments('width()', args)

        return self

    def collection_dump(self, args):
        try:
            self.dump_config.max_collection_dump = int(args)
        except ValueError:
            raise RookInvalidMethodArguments('collection_dump()', args)

        return self

    def string(self, args):
        try:
            self.dump_config.max_string = int(args)
        except ValueError:
            raise RookInvalidMethodArguments('string()', args)

        return self

    def limit(self, args):
        try:
            self.dump_config = PythonObjectNamespace.dump_configs[args.lower()]
        except KeyError:
            raise RookInvalidMethodArguments('limit()', args)

        return self

    def __hash__(self):
        return hash(self.obj)

    def __eq__(self, other):
        return type(self) == other and self.obj == other.obj

    def __nonzero__(self):
        return bool(self.obj)

    if six.PY3:
        __bool__ = __nonzero__

    dump_configs = {
        '': ObjectDumpConfig.default_limits(ObjectDumpConfig),
        'strict': ObjectDumpConfig.strict_limits(ObjectDumpConfig),
        'default': ObjectDumpConfig.default_limits(ObjectDumpConfig),
        'tolerant': ObjectDumpConfig.tolerant_limits(ObjectDumpConfig)}

    METHODS = (type, size, depth, width, collection_dump, string, limit)
