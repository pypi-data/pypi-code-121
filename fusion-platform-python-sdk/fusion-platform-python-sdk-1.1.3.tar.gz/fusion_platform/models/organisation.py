"""
Organisation model class file.

author: Matthew Casey

&copy; [Digital Content Analysis Technology Ltd](https://www.d-cat.co.uk)
"""

from functools import partial
from marshmallow import Schema, EXCLUDE

from fusion_platform.models import fields
from fusion_platform.models.credit import Credit
from fusion_platform.models.data import Data
from fusion_platform.models.model import Model
from fusion_platform.models.process import Process
from fusion_platform.models.service import Service


# Define the model schema classes. These are maintained from the API definitions.

class OrganisationUserSchema(Schema):
    """
    Nested schema class for users.
    """
    id = fields.UUID(allow_none=True)
    email = fields.Email(allow_none=True)
    roles = fields.List(fields.String(required=True))

    class Meta:
        """
        When loading an object, make sure we exclude any unknown fields, rather than raising an exception, and put fields in their definition order.
        """
        unknown = EXCLUDE
        ordered = True


class OrganisationSchema(Schema):
    """
    Schema class for organisation model.

    Each organisation model has the following fields (and nested fields):

    .. include::organisation.md
    """
    id = fields.UUID(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    created_at = fields.DateTime(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    updated_at = fields.DateTime(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    name = fields.String(required=True)
    address_line_1 = fields.String(required=True)
    address_line_2 = fields.String(allow_none=True)
    address_town_city = fields.String(required=True)
    address_post_zip_code = fields.String(required=True)
    address_country = fields.String(required=True)

    payment_customer = fields.String(allow_none=True)
    payment_valid = fields.Boolean(allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated and optional.
    # Removed payment_last_checked.

    income_customer = fields.String(allow_none=True)
    income_valid = fields.Boolean(allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated and optional.
    # Removed income_last_checked.

    income_tax_rate = fields.Decimal(allow_none=True)
    income_tax_reference = fields.String(allow_none=True)

    currency = fields.String(allow_none=True)  # Changed to optional.

    users = fields.List(fields.Nested(OrganisationUserSchema()), allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    agreed_licenses = fields.List(fields.UUID(required=True), allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    offers = fields.List(fields.UUID(required=True), allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    # Removed audit_services.

    maximum_output_storage_period = fields.Integer(allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    maximum_file_downloads = fields.Integer(allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    class Meta:
        """
        When loading an object, make sure we exclude any unknown fields, rather than raising an exception, and put fields in their definition order.
        """
        unknown = EXCLUDE
        ordered = True


class Organisation(Model):
    """
    Organisation model class providing attributes and methods to manipulate organisation details.
    """

    # Override the schema.
    _SCHEMA = OrganisationSchema()

    # Base path.
    _PATH_BASE = '/organisations/{organisation_id}'

    # Override the standard model paths.
    _PATH_DELETE = _PATH_BASE
    _PATH_GET = _PATH_BASE
    _PATH_PATCH = _PATH_BASE

    # Add in the custom model paths.
    _PATH_DATA = f"{_PATH_BASE}/data/uploaded"
    _PATH_OWN_SERVICES = f"{_PATH_BASE}/services"
    _PATH_PROCESSES = f"{_PATH_BASE}/processes"
    _PATH_SERVICES = f"{_PATH_BASE}/services/latest"

    def create_data(self, name, file_type, files, wait=False):
        """
        Creates a data object for the organisation and uploads the corresponding files. Optionally waits for the upload and analysis to complete.

        Args:
            name: The name of the data object.
            file_type: The type of files that the data object will hold.
            files: The list of file paths to be uploaded.
            wait: Optionally wait for the upload and analysis to complete? Default False.

        Returns:
            The created data object.

        Raises:
            RequestError: if the create fails.
            ModelError: if the model could not be created and validated by the Fusion Platform<sup>&reg;</sup>.
        """
        # Get a new template for the data model.
        data = Data(self._session)
        data._new(organisation_id=self.id)

        # Now attempt to create the data item.
        data._create(name, file_type, files, wait)

        return data

    @property
    def credit(self):
        """
        Returns:
            The credit model for the organisation.

        Raises:
            RequestError: if any get fails.
            ModelError: if a model could not be loaded or validated from the Fusion Platform<sup>&reg;</sup>.
        """
        return Credit._model_from_api_id(self._session, organisation_id=self.id, id=self.id)  # Credit model id is the same as the organisation's id.

    @property
    def data(self):
        """
        Provides an iterator through the organisation's uploaded data objects.

        Returns:
            An iterator through the data objects.

        Raises:
            RequestError: if any get fails.
            ModelError: if a model could not be loaded or validated from the Fusion Platform<sup>&reg;</sup>.
        """
        return Data._models_from_api_path(self._session, self._get_path(self.__class__._PATH_DATA))

    def find_data(self, id=None, name=None):
        """
        Searches for uploaded data objects with the specified id and/or (non-unique) name, returning the first object found and an iterator.

        Args:
            id: The data id to search for.
            name: The name to search for (case-sensitive).

        Returns:
            The first found data object, or None if not found, and an iterator through the found data objects.

        Raises:
            RequestError: if any get fails.
            ModelError: if a model could not be loaded or validated from the Fusion Platform<sup>&reg;</sup>.
        """
        # Note that name is a key field, and hence we can only search using begins with.
        filter = self.__class__._build_filter(
            [(self.__class__._FIELD_ID, self.__class__._FILTER_MODIFIER_EQ, id), (self.__class__._FIELD_NAME, self.__class__._FILTER_MODIFIER_BEGINS_WITH, name)])

        # Build the partial find generator and execute it.
        find = partial(Data._models_from_api_path, self._session, self._get_path(self.__class__._PATH_DATA), filter=filter)
        return self.__class__._first_and_generator(find)

    def find_processes(self, id=None, name=None):
        """
        Searches for the organisation's processes with the specified id and/or (non-unique) name, returning the first object found and an iterator.

        Args:
            id: The process id to search for.
            name: The name to search for (case-sensitive).

        Returns:
            The first found process object, or None if not found, and an iterator through the found process objects.

        Raises:
            RequestError: if any get fails.
            ModelError: if a model could not be loaded or validated from the Fusion Platform<sup>&reg;</sup>.
        """
        filter = self.__class__._build_filter(
            [(self.__class__._FIELD_ID, self.__class__._FILTER_MODIFIER_EQ, id), (self.__class__._FIELD_NAME, self.__class__._FILTER_MODIFIER_CONTAINS, name)])

        # Build the partial find generator and execute it.
        find = partial(Process._models_from_api_path, self._session, self._get_path(self.__class__._PATH_PROCESSES), filter=filter)
        return self.__class__._first_and_generator(find)

    def find_services(self, id=None, ssd_id=None, name=None, keyword=None):
        """
        Searches for services with the specified id, SSD id, (non-unique) name and/or keywords, returning the first object found and an iterator.

        Args:
            id: The service id to search for.
            ssd_id: The SSD id to search for.
            name: The name to search for (case-sensitive).
            keyword: The keyword to search for (case-sensitive).

        Returns:
            The first found service object, or None if not found, and an iterator through the found service objects.

        Raises:
            RequestError: if any get fails.
            ModelError: if a model could not be loaded or validated from the Fusion Platform<sup>&reg;</sup>.
        """
        # Note that name is a key field, and hence we can only search using begins with.
        filter = self.__class__._build_filter(
            [(self.__class__._FIELD_ID, self.__class__._FILTER_MODIFIER_EQ, id), (self.__class__._FIELD_SSD_ID, self.__class__._FILTER_MODIFIER_EQ, ssd_id),
             (self.__class__._FIELD_NAME, self.__class__._FILTER_MODIFIER_BEGINS_WITH, name),
             (self.__class__._FIELD_KEYWORDS, self.__class__._FILTER_MODIFIER_CONTAINS, keyword)])

        # Build the partial find generator and execute it.
        find = partial(Service._models_from_api_path, self._session, self._get_path(self.__class__._PATH_SERVICES), filter=filter)
        return self.__class__._first_and_generator(find)

    def new_process(self, name, service):
        """
        Creates a new template process from the service object. This process is not persisted to the Fusion Platform<sup>&reg;</sup>.

        Args:
            name: The name of the process.
            service: The service for which the process is to be created.

        Returns:
            The new template process object.

        Raises:
            RequestError: if the new fails.
            ModelError: if the model could not be created and validated by the Fusion Platform<sup>&reg;</sup>.
        """
        # Get a new template for the process model using the service.
        process = Process(self._session)
        process._new(query_parameters={Model._get_id_name(Service.__name__): service.id}, organisation_id=self.id, name=name)

        return process

    @property
    def own_services(self):
        """
        Provides an iterator through the services owned by the organisation. This includes services which may not yet be approved.

        Returns:
            An iterator through the service objects.

        Raises:
            RequestError: if any get fails.
            ModelError: if a model could not be loaded or validated from the Fusion Platform<sup>&reg;</sup>.
        """
        return Service._models_from_api_path(self._session, self._get_path(self.__class__._PATH_OWN_SERVICES))

    @property
    def processes(self):
        """
        Provides an iterator through the organisation's processes.

        Returns:
            An iterator through the process objects.

        Raises:
            RequestError if any get fails.
            ModelError if a model could not be loaded or validated from the Fusion Platform<sup>&reg;</sup>.
        """
        return Process._models_from_api_path(self._session, self._get_path(self.__class__._PATH_PROCESSES))

    @property
    def services(self):
        """
        Provides an iterator through the services available to the organisation for execution.

        Returns:
            An iterator through the service objects.

        Raises:
            RequestError: if any get fails.
            ModelError: if a model could not be loaded or validated from the Fusion Platform<sup>&reg;</sup>.
        """
        return Service._models_from_api_path(self._session, self._get_path(self.__class__._PATH_SERVICES))
