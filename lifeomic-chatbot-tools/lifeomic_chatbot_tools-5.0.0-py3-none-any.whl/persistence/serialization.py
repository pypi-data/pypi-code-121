import os
import pickle
import shutil
import typing as t


class ITypeSerializer(t.Protocol):
    """
    Interface for serializing instances of some type or group of types, for use with the :class:`Serializer` class.
    """

    type_name: str
    """
    A name identifying the type this serializer serializers. Should be unique among all the other
    :class:`TypeSerializer` serializers used. Should also contain only letters, numbers, and dashes.
    """

    ext: t.Optional[str]
    """The filename extension, if the serializer serializes its data to a single file. Should be ``None`` otherwise."""

    def serialize(self, obj: object, path: str):
        """Should serialize ``obj`` and save it to ``path``."""
        ...

    def deserialize(self, path: str) -> object:
        """
        Should load the persisted object at ``path``, and return the deserialized version. The object living at ``path``
        is guaranteed to have the type associated with this serializer.
        """
        ...

    def is_serializable(self, obj: object) -> bool:
        """Should return ``True`` if this serializer should be used to serialze ``obj``."""
        ...


class _CustomPickler(pickle.Pickler):
    def __init__(self, pkl_file, assets_path: str, type_serializers: t.Sequence[ITypeSerializer]):
        super().__init__(pkl_file)
        self._assets_path = assets_path
        self._ser_map = {ser.type_name: ser for ser in type_serializers}
        self._unique_id = 0

    def persistent_id(self, obj: object) -> t.Optional[tuple]:
        for ser in self._ser_map.values():
            if ser.is_serializable(obj):
                # Treat `obj` as an external object and serialize it using our own
                # methods. Our serializer's type name and the relative path it was serialized
                # to is returned and pickled, so the pickler will know how to find
                # the object again and deserialize it.
                obj_id = f"{ser.type_name}-{self._get_unique_id()}"
                obj_path = self._resolve_path(ser, obj_id)
                ser.serialize(obj, os.path.join(self._assets_path, obj_path))
                return ser.type_name, obj_path

        # No custom serializer for `obj`; pickle it using the normal way.
        return None

    def _get_unique_id(self) -> int:
        """A primary key generator."""
        id_ = self._unique_id
        self._unique_id += 1
        return id_

    @staticmethod
    def _resolve_path(ser: ITypeSerializer, obj_id: str):
        return f"{obj_id}.{ser.ext}" if ser.ext else obj_id


class _CustomUnpickler(pickle.Unpickler):
    def __init__(self, pkl_file, assets_path: str, type_serializers: t.Sequence[ITypeSerializer]):
        super().__init__(pkl_file)
        self._assets_path = assets_path
        self._ser_map = {ser.type_name: ser for ser in type_serializers}

    def persistent_load(self, pid: tuple) -> object:
        """
        This method is invoked whenever a persistent ID is encountered.
        Here, pid is the tuple returned by `_CustomPickler.persistent_id`.
        """
        ser_type_name, obj_path = pid
        if ser_type_name not in self._ser_map:
            raise pickle.UnpicklingError(
                "cannot deserialize: an object was found which was serialized using the "
                f"{ser_type_name} serializer, and this unpickler does not have that serializer registered."
            )
        ser = self._ser_map[ser_type_name]
        return ser.deserialize(os.path.join(self._assets_path, obj_path))


class Serializer:
    """
    A replacement for the :func:`pickle.dump` and :func:`pickle.load` functions. Exposes a hook for custom serialization
    behavior of different data types (e.g. keras models, PyTorch models, numpy arrays, etc.). You can use your own type
    serializers. Just implement the :class:`TypeSerializer` class and pass an instance of your class to the constructor.
    """

    def __init__(self, *custom_type_serializers: ITypeSerializer):
        self._type_serializers = custom_type_serializers

        if len(self._type_serializers) != len({ser.type_name for ser in self._type_serializers}):
            raise ValueError(
                "The type_name of each type serializer must be unique."
                f" Currently registered names: {[ser.type_name for ser in self._type_serializers]}"
            )

    def serialize(self, obj: object, path: str, overwrite: bool = False):
        """Serialize ``obj`` to ``path``, a directory."""
        if os.path.isfile(path):
            raise ValueError(f"cannot serialize to directory {path}; it is a file")
        if not os.path.isdir(path):
            os.makedirs(path)
        elif len(os.listdir(path)) > 0 and not overwrite:
            raise ValueError(f"cannot serialize: {path} is already populated and overwrite is set to False")

        with open(self._get_pkl_path(path), "wb") as f:
            _CustomPickler(f, path, self._type_serializers).dump(obj)

    def deserialize(self, path: str, delete: bool = False):
        """
        Load the data that was serialized to the directory at
        ``path``. It should have been serialized using this class's
        :meth:`serialize` method. If ``delete==True``, ``path`` will be
        deleted once the deserialization is finished.
        """
        # Deserialize the data
        with open(self._get_pkl_path(path), "rb") as f:
            obj = _CustomUnpickler(f, path, self._type_serializers).load()

        if delete:
            shutil.rmtree(path)

        return obj

    @staticmethod
    def _get_pkl_path(path: str) -> str:
        return os.path.join(path, "data.pkl")


class Persistent:
    """
    Mixin class giving persistence behavior. Any inheriting subclass will automatically receive :meth:`to_dir` and
    :meth:`from_dir` methods, which allows a class instance to easily be serialized to and deserialized from a
    directory.
    """

    serializer = Serializer()
    """The serializer to use. Override this for custom serialization behavior."""

    def to_dir(self, path: str, overwrite: bool = False):
        """Serializes the full state of ``self`` to directory ``path``."""
        self.serializer.serialize(self, path, overwrite)

    @classmethod
    def from_dir(cls, path: str, delete: bool = False) -> "Persistent":
        """
        Deserializes a full instance of this class from directory ``path``. If ``delete==True``,
        the persisted instance will be deleted once loaded into memory.
        """
        obj = cls.serializer.deserialize(path, delete)
        assert isinstance(obj, cls)
        return obj
