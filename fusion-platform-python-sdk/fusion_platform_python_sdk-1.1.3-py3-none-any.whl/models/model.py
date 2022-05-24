"""
Model base class file.

author: Matthew Casey

&copy; [Digital Content Analysis Technology Ltd](https://www.d-cat.co.uk)
"""

import copy
import i18n

from fusion_platform.base import Base
from fusion_platform.common.utilities import string_camel_to_underscore, value_to_read_only, value_to_string
from fusion_platform.session import Session


class ModelError(Exception):
    """
    Exception raised on model errors.
    """
    pass


class Model(Base):
    """
    Model base class providing attributes and methods to manipulate models.
    """

    # Define the schema. Override this with the correct schema object.
    _SCHEMA = None

    # Define the base model class name. Override this with the correct class name.
    _BASE_MODEL_CLASS_NAME = None

    # Define the standard template model paths. Override these with the correct paths.
    _PATH_CREATE = None
    _PATH_DELETE = None
    _PATH_GET = None
    _PATH_NEW = None
    _PATH_PATCH = None

    # Useful fields and templates.
    _FIELD_CONSTRAINED_NAMES = 'constrained_names'
    _FIELD_CONSTRAINED_VALUES = 'constrained_values'
    _FIELD_DATA_TYPE = 'data_type'
    _FIELD_ERROR = 'error'
    _FIELD_FILE_TYPE = 'file_type'
    _FIELD_GROUP_ID = 'group_id'
    _FIELD_ID = 'id'
    _FIELD_INPUT = 'input'
    _FIELD_INPUTS = 'inputs'
    _FIELD_KEYWORDS = 'keywords'
    _FIELD_NAME = 'name'
    _FIELD_OPTIONS = 'options'
    _FIELD_OUTPUTS = 'outputs'
    _FIELD_PROCESS_STATUS = 'process_status'
    _FIELD_SSD_ID = 'ssd_id'
    _FIELD_PUBLISHABLE = 'publishable'
    _FIELD_SIZE = 'size'
    _FIELD_VALIDATION = 'validation'
    _FIELD_VALUE = 'value'

    _FIELD_ID_NAME = '{name}_id'

    # Filter templates.
    _FILTER_MODIFIER_EQ = 'eq'
    _FILTER_MODIFIER_NE = 'ne'
    _FILTER_MODIFIER_LE = 'le'
    _FILTER_MODIFIER_LT = 'lt'
    _FILTER_MODIFIER_GE = 'ge'
    _FILTER_MODIFIER_GT = 'gt'
    _FILTER_MODIFIER_BEGINS_WITH = 'begins_with'
    _FILTER_MODIFIER_CONTAINS = 'contains'
    _FILTER_MODIFIER_NOT_CONTAINS = 'not_contains'
    _FILTER_MODIFIER_NULL = 'null'
    _FILTER_MODIFIER_NOT_NULL = 'not_null'
    _FILTER_MODIFIER_IN = 'in'
    _FILTER_MODIFIER_BETWEEN = 'between'

    _FILTER_TEMPLATE = '{name}__{modifier}'

    # Request keys.
    _REQUEST_KEY_FILTER = 'filter'
    _REQUEST_KEY_LAST = 'last'
    _REQUEST_KEY_LIMIT = 'limit'
    _REQUEST_KEY_NAME = '{model}[{key}]'
    _REQUEST_KEY_REVERSE = 'reverse'

    # Response keys.
    _RESPONSE_KEY_EXTRAS = 'extras'
    _RESPONSE_KEY_LAST = 'last'
    _RESPONSE_KEY_LIST = 'list'
    _RESPONSE_KEY_MODEL = 'model'
    _RESPONSE_KEY_URL = 'url'

    # Schema metadata keywords.
    _METADATA_HIDE = 'hide'
    _METADATA_READ_ONLY = 'read_only'

    # API job update frequency check.
    _API_UPDATE_WAIT_PERIOD = 5  # Time in seconds to wait between checking jobs on the API.

    def __init__(self, session, schema=None):
        """
        Initialises the object.

        Args:
            session: The linked session object for interfacing with the Fusion Platform<sup>&reg;</sup>.
            schema: The optional schema to use instead of the schema defined by the class.
        """
        super(Model, self).__init__()

        # Save off the session.
        self._session = session

        # Save off the schema. We either use the inherited value, or the custom value passed in.
        self.__schema = schema if schema is not None else self.__class__._SCHEMA

        # Initialise the fields.
        self.__model = None
        self.__persisted = False

    @property
    def attributes(self):
        """
        Returns:
            The model attributes as a dictionary.
        """
        schema = self.__get_schema()
        attributes = {}

        for key in schema.fields:
            # Do not include attributes which are hidden.
            if (Model._METADATA_HIDE not in schema.fields[key].metadata) and hasattr(self, key):
                value = getattr(self, key)
                attributes[key] = value

        return attributes

    def __build_body(self, **kwargs):
        """
        Builds a request body suitable for sending to the API. All current model attributes are included, with the keywords arguments overridding their value.

        Args:
            kwargs: The model attributes which override those already in the template.

        Returns:
            The built body.
        """
        model_name = self.__class__.__name__
        schema = self.__get_schema()
        body = {}

        # Include the current attributes. This includes anything which is read-only or hidden.
        for key in schema.fields:
            if (self.__model is not None) and (key in self.__model):
                body[Model._REQUEST_KEY_NAME.format(model=model_name, key=key)] = self.__model.get(key)

        # Now override any of the passed in attributes, ignoring anything which is read-only or hidden.
        for key in kwargs:
            if (Model._METADATA_READ_ONLY not in schema.fields[key].metadata) and (Model._METADATA_HIDE not in schema.fields[key].metadata):
                body[Model._REQUEST_KEY_NAME.format(model=model_name, key=key)] = kwargs[key]

        return body

    @classmethod
    def _build_filter(cls, parameters):
        """
        Builds a filter parameter suitable for #_models_from_api_path. Each of the parameters is a tuple specifying the field name, modifier and value. If a value
        is None, the filter is ignored.

        Args:
            parameters: A list of tuples specifying the field name, modifier and value

        Returns:
            The resulting filter dictionary.
        """
        filter = {}

        for name, modifier, value in parameters:
            if value is not None:
                filter[Model._FILTER_TEMPLATE.format(name=name, modifier=modifier)] = value

        return filter

    def _create(self, **kwargs):
        """
        Attempts to create the model object with the given values. This assumes the model template has been loaded first using the _new method, and that the model
        is then created using a POST RESTful request. This assumes that the post body contains key names which include the name of the model class.

        Args:
            kwargs: The model attributes which override those already in the template.

        Raises:
            RequestError: if the create fails.
            ModelError: if the model could not be loaded or validated from the Fusion Platform<sup>&reg;</sup>.
        """
        # Make sure the model is not already persisted.
        if self.__persisted:
            raise ModelError(i18n.t('models.model.already_persisted'))

        # Form the post body dictionary from the current object and the keyword arguments.
        body = self.__build_body(**kwargs)

        # Make sure there is a create which can be performed. This requires a non-empty body.
        if len(body) <= 0:
            raise ModelError(i18n.t('models.model.create_empty_body'))

        # Send the request and load the resulting model.
        self._send_and_load(self._get_path(self.__class__._PATH_CREATE), method=Session.METHOD_POST, body=body)

        # The model must have been persisted.
        self.__persisted = True

    def delete(self):
        """
        Attempts to delete the model object. This assumes the model is deleted using a DELETE RESTful request.

        Raises:
            RequestError: if the delete fails.
        """
        # Make sure the model is already persisted.
        if not self.__persisted:
            raise ModelError(i18n.t('models.model.not_persisted'))

        # Attempt to delete the model.
        self._session.request(path=self._get_path(self.__class__._PATH_DELETE), method=Session.METHOD_DELETE)

        # The model is no longer persisted.
        self.__persisted = False

    def __eq__(self, other):
        """
        Determines whether the other object is equal to self. Compares the object's attributes.

        Note that since a model object is mutable, there is no corresponding hash method.

        Args:
            other: The other object to compare against.

        Returns:
            True if the object's attributes are equal.
        """
        if isinstance(other, Model):
            return self.attributes == other.attributes

        return False

    @classmethod
    def _first_and_generator(cls, partial_generator):
        """
        Executes the partial generator to return the first returned model and a generator through all models (including the first). The partial generator is
        assumed to take an extra keyword argument used to limit the results.

        Args:
            partial_generator: The partial generator used to obtain the results.

        Returns:
            The first found model, or None if not found, and an iterator through all the models.

        Raises:
            RequestError: if any get fails.
            ModelError: if a model could not be loaded or validated from the Fusion Platform<sup>&reg;</sup>.
        """
        # We want to return the first model if available, plus the iterator through the rest. We therefore issue the query first with an items per request of 1 to
        # obtain the first model in a single request. The partial is then used to return a generator for them all.
        models = partial_generator(items_per_request=1)
        model = next(models, None)

        return model, partial_generator()

    def get(self, **kwargs):
        """
        Gets the model object by loading it from the Fusion Platform<sup>&reg;</sup>. Uses the model's current id and base model id for the get unless explicit values are
        provided via keyword arguments. This assumes the model is obtained using a GET RESTful request, and that the model data is held with the expected dictionary
        key within the response. The model is then loaded using the supplied schema to obtain the corresponding Python representation of it, before loading it into
        the model as a set of read-only attributes.

        Args:
            kwargs: Any explicit ids to be used.

        Raises:
            RequestError: if the get fails.
            ModelError: if the model could not be loaded or validated from the Fusion Platform<sup>&reg;</sup>.
        """
        # Send the request and load the resulting model.
        self._send_and_load(self._get_path(self.__class__._PATH_GET, **kwargs))

        # The model must have been persisted.
        self.__persisted = True

    @staticmethod
    def _get_id_name(class_name):
        """
        Generates the key name for the specified class' id attribute.

        Args:
            The class name to generate the key for.

        Returns:
            The key name for the class id attribute.
        """
        return Model._FIELD_ID_NAME.format(name=string_camel_to_underscore(class_name))

    def _get_ids(self, **kwargs):
        """
        Creates a dictionary containing all the relevant ids used by the model. This base class returns the id for the model which is taken from the id attribute,
        and any corresponding base model id. Each id is named using the associated class name and suffix (in underscore format). Each id may be overridden by a
        keyword argument.

        Args:
            kwargs: Any explicit ids to be used.

        Returns:
            A dictionary of the relevant model ids.
        """
        model_id_name = Model._get_id_name(self.__class__.__name__)
        result = {model_id_name: self.id if hasattr(self, Model._FIELD_ID) else None}

        if self.__class__._BASE_MODEL_CLASS_NAME is not None:
            base_model_id_name = Model._get_id_name(self.__class__._BASE_MODEL_CLASS_NAME)
            result[base_model_id_name] = getattr(self, base_model_id_name) if hasattr(self, base_model_id_name) else None

        # Override with any keywords. We explicitly replace 'id' with the correct key using a prefix.
        for key, value in kwargs.items():
            if (key == Model._FIELD_ID) and (model_id_name in result):
                result[model_id_name] = value
            else:
                result[key] = value

        return result

    @classmethod
    def _get_ids_from_list(cls, id_list, **kwargs):
        """
        Converts a list of ids into a list of dictionaries containing the correct id parameters. Additional id parameters cna be added to each element via the
        keyword arguments.

        Args:
            id_list: The list of ids to convert.
            kwargs: The additional ids as keyword arguments.

        Returns:
            The list of dictionary ids.
        """
        ids = []

        for item in id_list:
            ids.append({**{Model._get_id_name(cls.__name__): item}, **kwargs})

        return ids

    def _get_path(self, template, **kwargs):
        """
        Gets the RESTful path for the model using the template. The model's current ids are used, unless any explicit values are provided via keyword arguments.

        Args:
            template: The template path.
            kwargs: Any explicit ids to be used.

        Returns:
            The constructed path.

        Raises:
            NotImplementedError: if the template does not exist.
        """
        if template is None:
            raise NotImplementedError

        return template.format(**self._get_ids(**kwargs))

    def __get_schema(self):
        """
        Returns:
            The model schema object.

        Raises:
            NotImplementedError: if the schema does not exist.
        """
        if self.__schema is None:
            raise NotImplementedError

        return self.__schema

    @property
    def _model(self):
        """
        Protected getter for the model so that subclasses can access the model fields directly, but without the ability to change any value.

        Returns:
            The protected model object.
        """
        return value_to_read_only(self.__model)

    @classmethod
    def _model_from_api_id(cls, session, **kwargs):
        """
        Loads a model object with the given ids as keyword arguments from the Fusion Platform<sup>&reg;</sup>.

        Args:
            session: The linked session object for interfacing with the Fusion Platform<sup>&reg;</sup>.
            kwargs: Any explicit ids to be used.

        Returns:
            The created user model.

        Raises:
            RequestError: if the get fails.
            ModelError: if the model could not be loaded or validated from the Fusion Platform<sup>&reg;</sup>.
        """
        # Initialise a new object.
        model = cls(session)

        # Now get the model with an explicit user id.
        model.get(**kwargs)

        return model

    @classmethod
    def _models_from_api_ids(cls, session, ids):
        """
        Generates an iterator through a series of models using their ids. Each model is loaded using an id.

        Args:
            session: The linked session object for interfacing with the Fusion Platform<sup>&reg;</sup>.
            ids: A list of dictionaries containing the ids to iterate through.

        Returns:
            A generator to iterate through the models retrieved via the model GET.

        Raises:
            RequestError: if the get fails.
            ModelError: if the model could not be loaded or validated from the Fusion Platform<sup>&reg;</sup>.
        """
        return (cls._model_from_api_id(session, **id) for id in ids)

    @classmethod
    def _models_from_api_path(cls, session, path, items_per_request=24, reverse=False, filter=None, **kwargs):
        """
        Generates an iterator through a series of models using a path which returns a list of objects. Each model is loaded from the list. Since API lists are
        paged, the generator takes into account having to get subsequent pages of results.

        Use the items per request, reverse and filter parameters to modify the set of results returned. The items per request parameter determines how many results
        are returned by each request to the API for a page of results, up to the maximum number of results available. The reverse parameter can be used to return
        the results in reverse order (according to their natural order returned from the API). The filter parameter is a dictionary of filter values which should be
        applied. Each key represents a particular model field name which is used for filtering, while the value represents the value which should be used as the
        filter. With just the name of the field and a value, only those models with an exact (case-sensitive) match for the value will be returned. The following
        modifiers can be used to change the criteria by adding the modified to the end of the field name:

        __eq: filter the field by those which are equal to the filter value.
        __ne: filter the field by those which are not equal to the filter value. *
        __le: filter the field by those which are less than or equal to the filter value.
        __lt: filter the field by those which are less than the filter value.
        __ge: filter the field by those which are greater than or equal to the filter value.
        __gt: filter the field by those which are greater than the filter value.
        __begins_with: filter the field by those which begin with the filter value.
        __contains: filter the field by those which contain the filter value. *
        __not_contains: filter the field by those which do not contain the filter value. *
        __null: filter the field by those which are null. *
        __not_null: filter the field by those which are not null. *
        __in: filter the field by those which are equal to one of the values in the list. *
        __between: filter the field by those which are between (inclusive) the two lower and upper values supplied in the list. *

        * these modifiers are only available for certain fields. Using these on key fields will raise an exception.

        All string filtering is case-sensitive.

        Args:
            session: The linked session object for interfacing with the Fusion Platform<sup>&reg;</sup>.
            path: The path used to retrieve the list of objects.
            items_per_request: The optional maximum number of items to retrieve at each request. Default 24.
            reverse: Whether the list should be reversed or not. Default False.
            filter: The optional filter to be applied to the results. Default is no filter.
            kwargs: Any additional attributes which are to be set on each model which are not provided in each item from the path.

        Returns:
            A generator to iterate through the models retrieved via the path.

        Raises:
            RequestError: if the get fails.
            ModelError: if the model could not be loaded or validated from the Fusion Platform<sup>&reg;</sup>.
        """
        # Modify the filter keys so that they match the API requirement.
        filter = {} if filter is None else filter
        filter = {f"{Model._REQUEST_KEY_FILTER}[{key}]": value for key, value in filter.items()}

        # Loop through all required pages.
        finished = False
        last = {}

        while not finished:
            # Build the query parameters, including the last index, if available.
            query_parameters = {Model._REQUEST_KEY_LIMIT: items_per_request, Model._REQUEST_KEY_REVERSE: reverse, **filter, **last}

            # Send the request.
            response = session.request(path=path, query_parameters=query_parameters)

            # Extract the last index so that we know if we need to continue getting pages.
            last = {f"{Model._REQUEST_KEY_LAST}[{key}]": value for key, value in response.get(Model._RESPONSE_KEY_LAST).items()} if response.get(
                Model._RESPONSE_KEY_LAST) is not None else {}
            finished = len(last) <= 0

            # Build the generator around all of the returned items, which must all have been persisted.
            for item in response.get(Model._RESPONSE_KEY_LIST, []):
                model = cls(session)
                model.__set_model_from_response(item, **kwargs)
                model.__persisted = True

                yield model

    def _new(self, query_parameters=None, **kwargs):
        """
        Gets a new template model object by loading it from the Fusion Platform<sup>&reg;</sup>. The explicit base model id value should be provided via a keyword argument. This
        assumes the model is obtained using a GET RESTful request from the corresponding path, and that the model data is held with the expected dictionary key
        within the response. The template model is then loaded using the supplied schema to obtain the corresponding Python representation of it, before loading
        it into the model as a set of read-only attributes.

        Args:
            query_parameters: The optional query parameters as a dictionary.
            kwargs: Should include the base model id, if needed.

        Raises:
            RequestError: if the new fails.
            ModelError: if the model could not be loaded or validated from the Fusion Platform<sup>&reg;</sup>.
        """
        # Get the data.
        response = self._session.request(path=self._get_path(self.__class__._PATH_NEW, **kwargs), query_parameters=query_parameters)

        # Assume that the resulting model is held within the expected key within the resulting dictionary.
        if Model._RESPONSE_KEY_MODEL not in response:
            raise ModelError(i18n.t('models.model.failed_model_new'))

        # Add in the keyword arguments to the response so that they are set in the model as well.
        modified_response = response.get(Model._RESPONSE_KEY_MODEL, {})

        for key, value in kwargs.items():
            modified_response[key] = value

        # Load the response into the model. We ignore missing required fields and those which are None.
        self.__set_model_from_response(modified_response, partial=True)

        # The model is not persisted.
        self.__persisted = False

    @property
    def _persisted(self):
        """
        Protected getter for the persisted flag so that subclasses can find out if the model has already been persisted.

        Returns:
            The persisted flag.
        """
        return self.__persisted

    def _send_and_load(self, path, method=Session.METHOD_GET, body=None, key=_RESPONSE_KEY_MODEL):
        """
        Sends the body to the path using the method and then loads the resulting model.

        Args:
            path: The path to send the request to.
            method: The optional RESTful method for sending. Default is GET.
            body: The optional body to send. Default is None.
            key: The optional key to load the model from the response. Default is RESPONSE_KEY_MODEL.
        """
        # Send the request.
        response = self._session.request(path=path, method=method, body=body)

        # Assume that the resulting model is held within the expected key within the resulting dictionary.
        if key not in response:
            raise ModelError(i18n.t('models.model.failed_model_send_and_load'))

        # Load the response into the model.
        self.__set_model_from_response(response.get(key, {}))

    def __setattr__(self, key, value):
        """
        Prevents any model properties from being changed directly.

        Args:
            key: The property key.
            value: The property value.

        Raises:
            ModelError: to prevent modification.
        """
        # Prevent properties which are not protected or private from being set.
        if not key.startswith('_'):
            raise ModelError(i18n.t('models.model.readonly_property', property=key))

        # Make sure everything else can be set.
        super(Model, self).__setattr__(key, value)

    def _set_field(self, keys, value):
        """
        Sets the hierarchical field value. This modifies the underlying model.

        Args:
            keys: The hierarchical list of keys from top to bottom.
            value: The value to set.
        """
        # Step through the hierarchy to find the bottom key.
        top_key = keys[0]
        bottom_key = keys[-1]
        field = self.__model if len(keys) <= 1 else None

        for key in keys[:-1]:  # Does not include bottom key
            field = self.__model if field is None else field

            if (isinstance(field, dict) and (key not in field)) or (isinstance(field, list) and (key >= len(field))):
                raise ModelError(i18n.t('models.model.no_such_keys', keys=keys))
            else:
                field = field[key]

        if field is None:
            raise ModelError(i18n.t('models.model.no_such_keys', keys=keys))

        # Set the bottom key value.
        field[bottom_key] = value

        # Now update the object dictionary to reflect the change.
        schema = self.__get_schema()

        # Do not include attributes which are hidden.
        if Model._METADATA_HIDE not in schema.fields[top_key].metadata:
            self.__dict__[top_key] = value_to_read_only(self.__model[top_key])

    def _set_model(self, model):
        """
        Sets the underlying model for the object.

        Args:
            model: The model dictionary which this model object will represent.
        """
        # Convert the model dictionary into read-only properties. We use a deep copy of the dictionary to prevent later external changes.
        self.__model = copy.deepcopy(model)

        # Remove all existing field values.
        schema = self.__get_schema()

        for key in schema.fields:
            if key in self.__dict__:
                self.__dict__.pop(key)

        # Now add in all the values from the model.
        for key in self.__model:
            # Do not include attributes which are hidden.
            if Model._METADATA_HIDE not in schema.fields[key].metadata:
                self.__dict__[key] = value_to_read_only(self.__model[key])

    def __set_model_from_response(self, response, partial=False, **kwargs):
        """
        Obtains the model from the response using the supplied schema to obtain the corresponding Python representation of it, before
        loading it into the model as a set of read-only attributes.

        Args:
            response: The response containing the model attributes.
            schema: The schema used to load and validate the model.
            partial: Skip validation of required fields which are missing? Default False.
            kwargs: Any additional attributes which are to be set on the model which are not provided in the response.

        Raises:
            ModelError: if the model could not be loaded or validated from the Fusion Platform<sup>&reg;</sup>.
        """
        # Load the model in using the schema, and then use it to set the attributes of the model.
        try:
            # If we are loading a partial model, then remove any keys which have None values.
            if partial:
                response = {key: value for key, value in response.items() if value is not None}

            model = self.__get_schema().load(response, partial=partial)
            self._set_model({**model, **kwargs})

        except ModelError:
            raise

        except Exception as e:
            message = str(e)
            raise ModelError(i18n.t('models.model.failed_model_validation', message=message)) from e

    def __str__(self):
        """
        Returns:
            A string representation of the object.
        """
        return f"{self.__class__.__name__}{self.attributes}"

    def to_csv(self, exclude=None):
        """
        Converts the model attributes into a CSV string.

        Args:
            exclude: A list of attribute names which should be excluded from the CSV.

        Returns:
            The attribute names as a CSV header string and the model attributes as a CSV string.
        """
        exclude = exclude if exclude is not None else []
        header = []
        line = []

        for key, value in self.attributes.items():
            if key not in exclude:
                header.append(key)
                line.append(value_to_string(value))  # Handles things better than base object representations.

        return ','.join(header), ','.join(line)

    def update(self, **kwargs):
        """
        Attempts to update the model object with the given values. For models which have not been persisted, the relevant fields are updated without validation,
        which will occur when the model is persisted. For models which have been persisted, the update is made via the Fusion Platform<sup>&reg;</sup>. All current model
        attributes are sent to the Fusion Platform<sup>&reg;</sup> which will automatically ignore any which are not allowed or are read-only.

        Args:
            kwargs: The model attributes which are to be patched.

        Raises:
            RequestError: if the update fails.
            ModelError: if the model could not be loaded or validated from the Fusion Platform<sup>&reg;</sup>.
        """
        if self.__persisted:
            # Form the patch body dictionary from the keyword arguments.
            body = self.__build_body(**kwargs)

            # Make sure there is an update which can be performed. This requires a non-empty body.
            if len(body) <= 0:
                raise ModelError(i18n.t('models.model.update_empty_body'))

            # Send the request and load the resulting model.
            self._send_and_load(self._get_path(self.__class__._PATH_PATCH), method=Session.METHOD_PATCH, body=body)
        else:
            # Attempt to update the internal model. We do not allow updates to read-only or hidden fields.
            schema = self.__get_schema()

            for key in kwargs:
                if (Model._METADATA_READ_ONLY not in schema.fields[key].metadata) and (Model._METADATA_HIDE not in schema.fields[key].metadata):
                    self._set_field([key], kwargs[key])
