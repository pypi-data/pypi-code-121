import re
import json
import logging
import functools
from datetime import datetime
from typing import Callable
from bson import ObjectId
from urllib.parse import quote_plus
from flask import Flask, request
from pymongo import ASCENDING, DESCENDING, MongoClient, GEOSPHERE, TEXT, HASHED
from pymongo.errors import DuplicateKeyError
from pymongo.collection import Collection
from .core.converters import RegexConverter
from .core.json import MongoDBEnhancedEncoder
from .core.responses import *
from .core.validation import MongoDBEnhancedValidator
from .engine.schemas import *


_PROJECTION_RX = re.compile(r"^-?([a-zA-Z][a-zA-Z0-9_-]+)(,[a-zA-Z][a-zA-Z0-9_-]+)*$")


class ImproperlyConfiguredError(Exception):
    """
    Raised when the storage app is misconfigured.
    """


class StorageApp(Flask):
    """
    A Standard HTTP Storage app. Among other things, it provides
    a way to interact with MongoDB.
    """

    json_encoder: type = MongoDBEnhancedEncoder
    validator_class: type = MongoDBEnhancedValidator
    timestamp_with_splitseconds: bool = False

    def __init__(self, settings: dict, import_name: str = None, *args, validator_class: type = None, **kwargs):
        """
        Checks a validator_class is properly configured, as well as the auth_db / auth_table.

        :param settings: The schema being used for this app.
        :param args: The flask-expected positional arguments.
        :param kwargs: The flask-expected keyword arguments.
        """

        # First, set the non-None arguments, overriding the per-class setup.
        self._validator_class = validator_class or self.validator_class

        # Also, set everything up to keep schema decorators.
        self._schema_decorators = {}

        # Then, validate them (regardless being instance or class arguments).
        # Once the schema is validated, keep the normalized document for future
        # uses (e.g. extract the auth db/collection from it, and later extract
        # all the resources" metadata from it).
        if not (isinstance(self._validator_class, type) and issubclass(self._validator_class,
                                                                       MongoDBEnhancedValidator)):
            raise ImproperlyConfiguredError("Wrong or missing validator class")
        validator = self._validator_class("alephvault.http_storage.schemas.settings")
        if not validator.validate(settings):
            raise ImproperlyConfiguredError(f"Validation errors on resources DSL: {validator.errors}")
        self._settings = validator.document
        self._client = self._build_client(self._settings["connection"])
        self._resource_validators = {}
        for key, resource in self._settings["resources"].items():
            schema = resource["schema"]
            if not schema:
                raise ImproperlyConfiguredError(f"Validation errors on resource schema for key '{key}': it is empty")
            else:
                try:
                    self._resource_validators[key] = self._validator_class(schema)
                except:
                    raise ImproperlyConfiguredError(f"Validation errors on resource schema for key '{key}'")

        # Then, the base initialization must occur.
        super().__init__(import_name, *args, **kwargs)

        self._logger = logging.getLogger(self.import_name + ":logger")
        if settings["debug"]:
            self._logger.setLevel(logging.DEBUG)
        else:
            self._logger.setLevel(logging.INFO)

        # Adding the converter.
        self.url_map.converters['regex'] = RegexConverter

        # Prepare the indices.
        self._prepare_indexes()

        # After everything is initialized, the endpoints must be registered.
        # Those are standard resource endpoints.
        self._register_endpoints()

    def _build_client(self, connection):
        """
        Builds a client from the connection settings.
        :param connection: The connection settings.
        :return: The mongo client.
        """

        host = connection["host"].strip()
        port = connection["port"]
        user = connection["user"].strip()
        password = connection["password"]

        if not user or not password:
            raise ImproperlyConfiguredError("Missing MongoDB user or password")
        return MongoClient("mongodb://%s:%s@%s:%s" % (quote_plus(user), quote_plus(password), host, port))

    def _bearer_required(self, f: Callable):
        """
        Requires a valid "Authorization: Bearer xxxxx..." header.
        :param f: The function to invoke.
        :return: The decorated function.
        """

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            # Get the auth settings.
            auth_db = self._settings["auth"]["db"]
            auth_table = self._settings["auth"]["collection"]
            # Get the header. It must be "bearer {token}".
            authorization = request.headers.get("Authorization")
            if not authorization:
                return auth_missing()
            # Split it, and expect it to be "bearer".
            try:
                scheme, token = authorization.split(" ")
                if scheme.lower() != "bearer":
                    return auth_bad_schema()
            except ValueError:
                return auth_syntax_error()
            # Check the token.
            token = self._client[auth_db][auth_table].find_one({
                "api-key": token, "valid_until": {"$not": {"$lt": datetime.now()}}
            })
            if not token:
                return auth_not_found()
            # If the validation passed, then we invoke the decorated function.
            return f(*args, **kwargs)

        return wrapper

    def _capture_unexpected_errors(self, f: Callable):
        """
        Logs and wraps the unexpected errors.
        :param f: The handler function to invoke.
        :return: A new handler which captures and logs any error
          and returns a 500.
        """

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except:
                self._logger.exception("An exception was occurred (don't worry! it was wrapped into a 500 error)")
                return internal_error()

        return wrapper

    def _using_resource(self, f: Callable):
        """
        Wraps a handler to provide more data from the resource definition.
        Returns a 404 if the resource is not defined.
        :param f: The handler function to invoke.
        :return: A new handler which gets the resource and passes it
          to the wrapped handler.
        """

        @functools.wraps(f)
        def new_handler(resource: str, *args, **kwargs):
            resource_definition = self._settings["resources"].get(resource)
            if not resource_definition:
                return not_found()
            verbs = resource_definition["verbs"]
            db_name = resource_definition["db"]
            collection_name = resource_definition["collection"]
            collection = self._client[db_name][collection_name]
            filter = resource_definition["filter"]
            if resource_definition["soft_delete"]:
                filter = {**filter, "_deleted": {"$ne": True}}
            if verbs != "*" and request.method not in verbs:
                return method_not_allowed()
            return f(resource, resource_definition, db_name, collection_name, collection, filter, *args, **kwargs)

        return new_handler

    def _prepare_indexes(self):
        """
        Prepares the indices for each setup.
        """

        # Prepare the indices for the auth table.
        self._client[self._settings["auth"]["db"]][self._settings["auth"]["collection"]].create_index(
            [("api-key", ASCENDING)], name="api-key", unique=True, background=False, sparse=True
        )

        # Prepare the indices for the resources.
        for key, resource in self._settings["resources"].items():
            indices = resource["indexes"]
            for name, index in indices.items():
                unique = index["unique"]
                fields = index["fields"]
                if isinstance(fields, str):
                    fields = [fields]
                native_fields = []
                for field in fields:
                    type_ = ASCENDING
                    if field[0] == "-":
                        type_ = DESCENDING
                    elif field[0] == "@":
                        type_ = GEOSPHERE
                    elif field[0] == "~":
                        type_ = TEXT
                    elif field[0] == "#":
                        type_ = HASHED
                    if type_ != ASCENDING:
                        field = field[1:]
                    native_fields.append((field, type_))
                self._client[resource["db"]][resource["collection"]].create_index(native_fields, name=name,
                                                                                  unique=unique, background=False,
                                                                                  sparse=True)

    def _register_endpoints(self):
        """
        Registers all the needed endpoints for the resources.
        """

        # First, list-wise and simple-wise resource methods.

        def _to_uint(value, minv=0):
            try:
                return max(minv, int(value))
            except:
                return minv

        def _parse_order_by(value):
            if not value:
                value = []
            elif isinstance(value, str):
                value = value.split(",")

            result = []
            for element in value:
                element = element.strip()
                if not element:
                    raise ValueError("Invalid order_by field: empty name")
                direction = ASCENDING
                if element[0] == "-":
                    element = element[1:]
                    direction = DESCENDING
                result.append((element, direction))
            return result

        def _parse_projection(projection):
            if projection is None:
                return None
            elif isinstance(projection, (list, tuple, dict)):
                return projection
            elif isinstance(projection, str):
                try:
                    # 1. attempt json, and pass directly.
                    return json.loads(projection)
                except ValueError:
                    # 2. attempt a csv format.
                    if projection == "":
                        raise TypeError("Invalid projection value")
                    elif projection == "*":
                        # Use full object.
                        return None
                    elif not _PROJECTION_RX.match(projection):
                        raise TypeError("Invalid projection value")

                    # Parse as a dictionary.
                    include = True
                    if projection[0] == "-":
                        include = False
                        projection = projection[1:]
                    return {p: include for p in projection}
            else:
                raise TypeError("Invalid projection value")

        def _update_document(element, updates):
            tmp = self._client["~tmp"]["updates"]
            tmp.replace_one({"_id": element["_id"]}, element, upsert=True)
            tmp.update_one({"_id": element["_id"]}, updates)
            element = tmp.find_one({"_id": element["_id"]})
            tmp.delete_one({"_id": element["_id"]})
            element.pop("_id")
            return element

        @self.route("/<string:resource>", methods=["GET"])
        @self._capture_unexpected_errors
        @self._using_resource
        @self._bearer_required
        def resource_read(resource: str, resource_definition: dict, db_name: str, collection_name: str,
                          collection: Collection, filter: dict):
            """
            Intended for list-type resources and simple-type resources.
            List-type resources use a cursor and return a list.
            Simple-type resources return a single element, or nothing / 404.
            """

            # Its "type" will be "list" or "simple".
            if resource_definition["type"] == "list":
                # Process a "list" resource.
                projection = _parse_projection(request.args.get('projection') or
                                               resource_definition.get("list_projection"))
                offset = _to_uint(request.args.get("offset"))
                max_results = self._settings["global"].get("list_max_results") or \
                    resource_definition.get("list_max_results")
                limit = min(_to_uint(request.args.get("limit", 20), 1), max_results)
                order_by = _parse_order_by(request.args.get("order_by", resource_definition.get("order_by")))
                self._logger.debug(f"GET /{resource} (type=list), using filter={filter}")
                query = collection.find(filter=filter, projection=projection)
                if order_by:
                    query = query.sort(order_by)
                if offset:
                    query = query.skip(offset)
                if limit:
                    query = query.limit(limit)

                return ok(list(query))
            else:
                # Process a "simple" resource.
                self._logger.debug(f"GET /{resource} (type=single), using filter={filter}")
                projection = _parse_projection(request.args.get('projection') or resource_definition.get("projection"))
                element = collection.find_one(filter=filter, projection=projection)
                if element:
                    return ok(element)
                else:
                    return not_found()

        @self.route("/<string:resource>", methods=["POST"])
        @self._capture_unexpected_errors
        @self._using_resource
        @self._bearer_required
        def resource_create(resource: str, resource_definition: dict, db_name: str, collection_name: str,
                            collection: Collection, filter: dict):
            """
            Intended for list-type resources and simple-type resources.
            List-type resources gladly accept new content (a single
            new element from incoming body).
            Simple-type resources only accept new content (a single
            new element from incoming body as well) if no previous
            content exists. Otherwise, they return conflict / 409.
            :return: Flask-compatible responses.
            """

            # Require the body to be json, and validate it.
            if not request.is_json or not isinstance(request.json, dict):
                return format_unexpected()
            validator = self._resource_validators[resource]
            request.json.pop('_id', None)
            self._logger.debug(f"POST /{resource} (type={resource_definition['type']}) "
                               f"with body: {request.json}")
            if validator.validate(request.json):
                # Its "type" will be "list" or "simple".
                if resource_definition["type"] != "list" and collection.find_one(filter):
                    return conflict_already_exists()
                else:
                    self._logger.debug(f"POST /{resource} (type={resource_definition['type']}) "
                                       f"with curated body: {validator.document}")
                    try:
                        result = collection.insert_one(validator.document)
                    except DuplicateKeyError as e:
                        self._logger.debug(f"Duplicate key: {e.details}")
                        return conflict_duplicate_key(e.details["keyValue"])
                    return created(result.inserted_id)
            else:
                return format_invalid(validator.errors)

        @self.route("/<string:resource>/~<string:method>", methods=["GET", "POST"])
        @self._capture_unexpected_errors
        @self._using_resource
        @self._bearer_required
        def resource_method(resource: str, resource_definition: dict, db_name: str, collection_name: str,
                            collection: Collection, filter: dict, method: str):
            """
            Intended for list-type resources and simple-type resources.
            Implementations should operate over {collection}.find() for
            list resources, and over {collection}.find_one() for simple
            resources. The operation must be read-only for GET verb.
            :return: Flask-compatible responses.
            """

            try:
                method_entry = resource_definition["methods"][method]
                if request.method == "GET":
                    if method_entry["type"] != "view":
                        return not_found()
                else:
                    if method_entry["type"] != "operation":
                        return not_found()
            except KeyError:
                return not_found()

            # Getting the appropriate instance.
            instance = method_entry["handler"]

            # Invoke the method
            return instance(self._client, resource, method, db_name, collection_name, filter)

        @self.route("/<string:resource>", methods=["PUT"])
        @self._capture_unexpected_errors
        @self._using_resource
        @self._bearer_required
        def resource_replace(resource: str, resource_definition: dict, db_name: str, collection_name: str,
                             collection: Collection, filter: dict):
            """
            Intended for simple-type resources. Replaces the element, if
            it exists (otherwise, returns a 404 error) with a new one, from
            the incoming json body.
            :return: Flask-compatible responses.
            """

            if not request.is_json or not isinstance(request.json, dict):
                return format_unexpected()
            # Process a "simple" resource.
            element = collection.find_one(filter=filter)
            if element:
                validator = self._resource_validators[resource]
                request.json.pop('_id', None)
                self._logger.debug(f"PUT /{resource} (type=simple) "
                                   f"with body: {request.json}")
                if validator.validate(request.json):
                    try:
                        self._logger.debug(f"PUT /{resource} (type=simple) "
                                           f"with curated body: {validator.document}")
                        collection.replace_one({"_id": element["_id"], **filter}, validator.document, upsert=False)
                    except DuplicateKeyError as e:
                        return conflict_duplicate_key(e.details["keyValue"])
                    return ok()
                else:
                    return format_invalid(validator.errors)
            else:
                return not_found()

        @self.route("/<string:resource>", methods=["PATCH"])
        @self._capture_unexpected_errors
        @self._using_resource
        @self._bearer_required
        def resource_update(resource: str, resource_definition: dict, db_name: str, collection_name: str,
                            collection: Collection, filter: dict):
            """
            Intended for simple-type resources. Updates the element, if
            it exists (otherwise, returns a 404 error) with new data from
            the incoming json body.
            :return: Flask-compatible responses.
            """

            if not request.is_json or not isinstance(request.json, dict):
                return format_unexpected()
            element = collection.find_one(filter=filter)
            if element:
                self._logger.debug(f"PATCH /{resource} (type=simple) "
                                   f"with body: {request.json}")
                element = _update_document(element, request.json)
                validator = self._resource_validators[resource]
                if validator.validate(element):
                    try:
                        self._logger.debug(f"PATCH /{resource} (type=simple) "
                                           f"with updated body: {validator.document}")
                        collection.replace_one({"_id": element["_id"], **filter}, validator.document, upsert=False)
                    except DuplicateKeyError as e:
                        return conflict_duplicate_key(e.details["keyValue"])
                    return ok()
                else:
                    return format_invalid(validator.errors)
            else:
                return not_found()

        @self.route("/<string:resource>", methods=["DELETE"])
        @self._capture_unexpected_errors
        @self._using_resource
        @self._bearer_required
        def resource_delete(resource: str, resource_definition: dict, db_name: str, collection_name: str,
                            collection: Collection, filter: dict):
            """
            Intended for simple-type resources. Deletes the element, if
            it exists (otherwise, returns a 404 error).
            :return: Flask-compatible responses.
            """

            if resource_definition["soft_delete"]:
                result = collection.update_one(filter, {"$set": {"_deleted": True}}, upsert=False)
                if result.modified_count:
                    return ok()
                else:
                    return not_found()
            else:
                result = collection.delete_one(filter)
                if result.deleted_count:
                    return ok()
                else:
                    return not_found()

        # Second, element-wise resource methods.

        @self.route("/<string:resource>/<regex('[a-f0-9]{24}'):object_id>", methods=["GET"])
        @self._capture_unexpected_errors
        @self._using_resource
        @self._bearer_required
        def item_resource_read(resource: str, resource_definition: dict, db_name: str, collection_name: str,
                               collection: Collection, filter: dict, object_id: str):
            """
            Reads an element from a list, or returns nothing / 404.
            :return: Flask-compatible responses.
            """

            # Process a "simple" resource.
            projection = _parse_projection(request.args.get('projection') or resource_definition.get("projection"))
            element = collection.find_one(filter={**filter, "_id": ObjectId(object_id)}, projection=projection)
            if element:
                return ok(element)
            else:
                return not_found()

        @self.route("/<string:resource>/<regex('[a-f0-9]{24}'):object_id>", methods=["PUT"])
        @self._capture_unexpected_errors
        @self._using_resource
        @self._bearer_required
        def item_resource_replace(resource: str, resource_definition: dict, db_name: str, collection_name: str,
                                  collection: Collection, filter: dict, object_id: str):
            """
            Replaces an element from a list, if it exists (or
            returns nothing / 404) with a new one from the
            incoming json body.
            :return: Flask-compatible responses.
            """

            if not request.is_json or not isinstance(request.json, dict):
                return format_unexpected()
            filter = {**filter, "_id": ObjectId(object_id)}
            element = collection.find_one(filter=filter)
            if element:
                validator = self._resource_validators[resource]
                request.json.pop('_id', None)
                self._logger.debug(f"PUT /{resource} (type=list) "
                                   f"with body: {request.json}")
                if validator.validate(request.json):
                    try:
                        self._logger.debug(f"PUT /{resource} (type=list) "
                                           f"with curated body: {request.json}")
                        collection.replace_one(filter, validator.document, upsert=False)
                    except DuplicateKeyError as e:
                        return conflict_duplicate_key(e.details["keyValue"])
                    return ok()
                else:
                    return format_invalid(validator.errors)
            else:
                return not_found()

        @self.route("/<string:resource>/<regex('[a-f0-9]{24}'):object_id>", methods=["PATCH"])
        @self._capture_unexpected_errors
        @self._using_resource
        @self._bearer_required
        def item_resource_update(resource: str, resource_definition: dict, db_name: str, collection_name: str,
                                 collection: Collection, filter: dict, object_id: str):
            """
            Updates an element from a list, if it exists (or
            returns nothing / 404) with new data from the
            incoming json body.
            :return: Flask-compatible responses.
            """

            if not request.is_json or not isinstance(request.json, dict):
                return format_unexpected()
            filter = {**filter, "_id": ObjectId(object_id)}
            element = collection.find_one(filter=filter)
            if element:
                element = _update_document(element, request.json)
                validator = self._resource_validators[resource]
                self._logger.debug(f"PUT /{resource} (type=list) "
                                   f"with body: {request.json}")
                if validator.validate(element):
                    try:
                        self._logger.debug(f"PUT /{resource} (type=list) "
                                           f"with updated body: {validator.document}")
                        collection.replace_one(filter, validator.document, upsert=False)
                    except DuplicateKeyError as e:
                        return conflict_duplicate_key(e.details["keyValue"])
                    return ok()
                else:
                    return format_invalid(validator.errors)
            else:
                return not_found()

        @self.route("/<string:resource>/<regex('[a-f0-9]{24}'):object_id>", methods=["DELETE"])
        @self._capture_unexpected_errors
        @self._using_resource
        @self._bearer_required
        def item_resource_delete(resource: str, resource_definition: dict, db_name: str, collection_name: str,
                                 collection: Collection, filter: dict, object_id: str):
            """
            Deletes an element from a list, if it exists (or
            returns nothing / 404).
            :return: Flask-compatible responses.
            """

            filter = {**filter, "_id": ObjectId(object_id)}
            if resource_definition["soft_delete"]:
                result = collection.update_one(filter, {"$set": {"_deleted": True}}, upsert=False)
                if result.modified_count:
                    return ok()
                else:
                    return not_found()
            else:
                result = collection.delete_one(filter)
                if result.deleted_count:
                    return ok()
                else:
                    return not_found()

        @self.route("/<string:resource>/<regex('[a-f0-9]{24}'):object_id>/~<string:method>", methods=["GET", "POST"])
        @self._capture_unexpected_errors
        @self._using_resource
        @self._bearer_required
        def item_resource_view(resource: str, resource_definition: dict, db_name: str, collection_name: str,
                               collection: Collection, filter: dict, object_id: str, method: str):
            """
            Implementation should operate over {collection}.find_one(
                {"_id": ObjectId(object_id)}
            ). This operation must be read-only.
            :return: Flask-compatible responses.
            """

            try:
                method_entry = resource_definition["item_methods"][method]
                if request.method == "GET":
                    if method_entry["type"] != "view":
                        return not_found()
                else:
                    if method_entry["type"] != "operation":
                        return not_found()
            except KeyError:
                return not_found()

            # Getting the appropriate instance.
            instance = method_entry["handler"]

            # Invoke the method
            return instance(self._client, resource, method, db_name, collection_name, filter, ObjectId(object_id))
