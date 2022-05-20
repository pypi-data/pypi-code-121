from bson import ObjectId
from pymongo import MongoClient


class MethodHandler:
    """
    A method handler is a class whose instances are callable. They are instantiated
    per-request and have one __call__ method to serve the method's implementation.
    The logic is totally custom, as long as the result is Flask-compatible. The only
    difference is that some arguments are provided to this custom method: they are
    settings in the involved resource (and the name of the custom method). The only
    method, in this instance, that is needed to be implemented is `__call__`, but
    any support method or lifecycle (e.g. `__init__`, `__del__`) are allowed.
    """

    def __call__(self, client: MongoClient, resource: str, method: str, db: str, collection: str, filter: dict):
        """
        The implementation of this method is performed on the entire collection, instead
        of a particular item on it. This means: it is intended for top-level methods in
        the "list" or "simple" resources (use `.find` method for lists, and `.find_one`
        method for simple resources, in the related collection).

        Typically, this method should not perform any change in the system or collections
        in the MongoDB server if the method is read-only (served with GET), while it can
        perform any change in the system or collections in the MongoDB server for methods
        of type "operation" (served with POST).

        Access to the Flask's request method is not just allowed, but also encouraged when
        on need of body and / or query arguments.
        :param client: The PyMongo client to use.
        :param resource: The key of the resource, as defined in the settings.
        :param method: The name of the method to invoke.
        :param db: The involved db, in the MongoDB server, for this resource.
        :param collection: The involved collection, in the MongoDB server, for this resource.
        :param filter: The filter to use (by default, it will be {}).
        :return: Whatever is needed, but compatible which flask endpoints (e.g. a response,
          a tuple with content and status, ...).
        """

        raise NotImplementedError


class ItemMethodHandler:
    """
    An item method handler is a class whose instances are callable. They are instantiated
    per-request and have one __call__ method to serve the method's implementation. The
    logic is totally custom, as long as the result is Flask-compatible. The only difference
    is that some arguments are provided to this custom method: they are settings in the
    involved resource (and the name of the custom method). The only method, in this instance,
    that is needed to be implemented is `__call__`, but any support method or lifecycle
    (e.g. `__init__`, `__del__`) are allowed. The invocation will also receive the current
    object's id inside the collection, intended to serve logic for a single object rather
    than for the collection as a whole, or a singleton object.
    """

    def __call__(self, client: MongoClient, resource: str, method: str, db: str, collection: str, filter: dict,
                 object_id: ObjectId):
        """
        The implementation of this method is performed on a particular element of the
        collection, instead of the whole. This means: it is intended for item-level methods
        in the "list" resources (use `.find_one` method by combining the input filter
        with the {"_id": objectid} criterion on need in the related collection).

        Typically, this method should not perform any change in the system or collections
        in the MongoDB server if the method is read-only (served with GET), while it can
        perform any change in the system or collections in the MongoDB server for methods
        of type "operation" (served with POST).

        Access to the Flask's request method is not just allowed, but also encouraged when
        on need of body and / or query arguments.
        :param client: The PyMongo client to use.
        :param resource: The key of the resource, as defined in the settings.
        :param method: The name of the method to invoke.
        :param db: The involved db, in the MongoDB server, for this resource.
        :param collection: The involved collection, in the MongoDB server, for this resource.
        :param filter: The filter to use (by default, it will be {}).
        :param object_id: The id of the object for which this method was called.
        :return: Whatever is needed, but compatible which flask endpoints (e.g. a response,
          a tuple with content and status, ...).
        """

        raise NotImplementedError
