import collections.abc as collections

# Helper class that exposes all data objects of a given class stored in a DataCollection.
class DataObjectsDict(collections.MutableMapping):
    """
    A dictionary-like view of all :py:class:`DataObject` instances of a particular type in a :py:class:`DataCollection`.

    The class implements the ``collections.abc.MutableMapping`` interface. That means it can be used
    like a regular Python ``dict`` object to access data objects based on their unique identifiers.
    """

    def __init__(self, data_collection, data_object_class):
        self._data = data_collection
        self._data_object_class = data_object_class

    def __len__(self):
        # Count the number of data objects of the right type in the collection.
        return sum(isinstance(obj, self._data_object_class) for obj in self._data.objects)

    def __getitem__(self, key):
        # Returns the data object with the given identifier key.
        if key.endswith('_'):
            if not self._data.is_safe_to_modify:
                raise ValueError("Requesting a mutable version of a {} is not possible if the data collection itself is not mutable.".format(self._data_object_class.__name__))
            request_mutable = True
            key = key[:-1]
        else:
            request_mutable = False
        for obj in self._data.objects:
            if isinstance(obj, self._data_object_class):
                if obj.identifier == key:
                    if request_mutable:
                        return self._data.make_mutable(obj)
                    else:
                        return obj
        # Generate a helpful error message for the user listing all available keys.
        available_ids = []
        for obj in self._data.objects:
            if isinstance(obj, self._data_object_class):
                available_ids.append(obj.identifier)
        raise KeyError("{} with identifier '{}' does not exist. Available identifiers: {}".format(self._data_object_class.__name__, str(key), available_ids))

    def __iter__(self):
        for obj in self._data.objects:
            if isinstance(obj, self._data_object_class):
                yield obj.identifier

    def __repr__(self):
        return repr(dict(self))

    def __delitem__(self, key):
        for obj in self._data.objects:
            if isinstance(obj, self._data_object_class) and obj.identifier == key:
                self._data.objects.remove(obj)
                return
        # Generate a helpful error message for the user listing all available keys.
        available_ids = []
        for obj in self._data.objects:
            if isinstance(obj, self._data_object_class):
                available_ids.append(obj.identifier)
        raise KeyError("{} with identifier '{}' does not exist. Available identifiers: {}".format(self._data_object_class.__name__, str(key), available_ids))

    def __setitem__(self, key, value):
        if not isinstance(value, self._data_object_class):
            raise ValueError("{} object expected".format(self._data_object_class.__name__))
        if not key:
            raise ValueError("Non-empty dictionary key expected")
        if value.identifier:
            if value.identifier != key:
                raise ValueError("Cannot insert {} object with identifier '{}' under dictionary key '{}'".format(self._data_object_class.__name__, value.identifier, key))
        else:
            value.identifier = key
        for obj in self._data.objects:
            if isinstance(obj, self._data_object_class) and obj.identifier == key:
                if not obj is value:
                    self._data.objects.remove(obj)
                    self._data.objects.append(value)
                return
        self._data.objects.append(value)

    def insert(self, object):
        if not isinstance(object, self._data_object_class):
            raise ValueError("{} object expected but got a {}".format(self._data_object_class.__name__, type(object)))
        if not object.identifier:
            raise ValueError("{} object must have a non-empty identifier when inserting it into the dictionary.".format(self._data_object_class.__name__))
        if not object in self._data.objects:
            if object.identifier in self:
                raise KeyError("{} object with the same identifier '{}' already exists the dictionary.".format(self._data_object_class.__name__, object.identifier))
            self._data.objects.append(object)

    def create(self, identifier: str, vis_params = None, **params):
        if not identifier:
            raise ValueError("Non-empty identifier expected.")
        for obj in self._data.objects:
            if isinstance(obj, self._data_object_class) and obj.identifier == identifier:
                mutable_obj = self._data.make_mutable(obj)
                if params:
                    for name, value in params.items():
                        setattr(mutable_obj, name, value)
                return mutable_obj
        new_obj = self._data_object_class(identifier = identifier, **params)
        self._data.objects.append(new_obj)
        if vis_params:
            for name, value in vis_params.items():
                setattr(new_obj.vis, name, value)
        return new_obj