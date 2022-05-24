"""
Process execution model class file.

author: Matthew Casey

&copy; [Digital Content Analysis Technology Ltd](https://www.d-cat.co.uk)
"""

import i18n
from marshmallow import Schema, EXCLUDE
from time import sleep

from fusion_platform.models import fields
from fusion_platform.models.model import Model, ModelError
from fusion_platform.models.process_service_execution import ProcessServiceExecution


# Define the model schema classes. These are maintained from the API definitions.

class ProcessExecutionChainOptionSchema(Schema):
    """
    Nested schema class for SSD chain option.
    """
    name = fields.String(required=True)
    value = fields.String(allow_none=True)

    class Meta:
        """
        When loading an object, make sure we exclude any unknown fields, rather than raising an exception, and put fields in their definition order.
        """
        unknown = EXCLUDE
        ordered = True


class ProcessExecutionChainSchema(Schema):
    """
    Nested schema class for SSD chain.
    """
    ssd_id = fields.UUID(required=True)
    service_id = fields.UUID(required=True)
    inputs = fields.List(fields.UUID(allow_none=True), allow_none=True)
    outputs = fields.List(fields.UUID(required=True), allow_none=True)
    options = fields.List(fields.Nested(ProcessExecutionChainOptionSchema()), allow_none=True)
    intermediate = fields.Boolean(allow_none=True)

    class Meta:
        """
        When loading an object, make sure we exclude any unknown fields, rather than raising an exception, and put fields in their definition order.
        """
        unknown = EXCLUDE
        ordered = True


class ProcessExecutionOptionSchema(Schema):
    """
    Nested schema class for options which are provided to the SSD images when run.
    """
    ssd_id = fields.UUID(required=True)
    name = fields.String(required=True)
    value = fields.String(allow_none=True)
    required = fields.Boolean(required=True)
    data_type = fields.String(required=True)
    validation = fields.String(allow_none=True)
    mutually_exclusive = fields.String(allow_none=True)
    advanced = fields.Boolean(allow_none=True)
    title = fields.String(allow_none=True)
    description = fields.String(allow_none=True)

    class Meta:
        """
        When loading an object, make sure we exclude any unknown fields, rather than raising an exception, and put fields in their definition order.
        """
        unknown = EXCLUDE
        ordered = True


class ProcessExecutionSchema(Schema):
    """
    Schema class for process execution model.

    Each process execution model has the following fields (and nested fields):

    .. include::process_execution.md
    """
    id = fields.UUID(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    created_at = fields.DateTime(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    updated_at = fields.DateTime(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    organisation_id = fields.UUID(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    process_id = fields.UUID(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    group_id = fields.UUID(allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    group_index = fields.Integer(allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    group_count = fields.Integer(allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    options = fields.List(fields.Nested(ProcessExecutionOptionSchema()), allow_none=True)
    chains = fields.List(fields.Nested(ProcessExecutionChainSchema()), allow_none=True)
    # Removed creator.

    started_at = fields.DateTime(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    ended_at = fields.DateTime(allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    abort_reason = fields.String(allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    abort = fields.Boolean(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    success = fields.Boolean(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    progress = fields.Integer(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    delete_expiry = fields.DateTime(required=True)
    delete_warning_status = fields.String(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    deletable = fields.String(allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    class Meta:
        """
        When loading an object, make sure we exclude any unknown fields, rather than raising an exception, and put fields in their definition order.
        """
        unknown = EXCLUDE
        ordered = True


class ProcessExecution(Model):
    """
    Process execution model class providing attributes and methods to manipulate process execution item details.
    """

    # Override the schema.
    _SCHEMA = ProcessExecutionSchema()

    # Override the base model class name.
    _BASE_MODEL_CLASS_NAME = 'Organisation'  # A string to prevent circular imports.

    # Base path.
    _PATH_BASE = '/organisations/{organisation_id}/process_executions/{process_execution_id}'

    # Override the standard model paths.
    _PATH_DELETE = _PATH_BASE
    _PATH_GET = _PATH_BASE
    _PATH_PATCH = _PATH_BASE

    # Add in the custom model paths.
    _PATH_COMPONENTS = f"{_PATH_BASE}/process_service_executions"

    def check_complete(self, wait=False):
        """
        Checks whether the execution has completed. Optionally waits for the execution to complete.

        Args:
            wait: Optionally wait for the execution to complete? Default False.

        Returns:
            True if the execution is complete.

        Raises:
            RequestError: if any request fails.
            ModelError: if the execution failed.
            ModelError: if a model could not be loaded or validated from the Fusion Platform<sup>&reg;</sup>.
        """
        complete = False

        # Optionally wait for the execution to finish.
        while not complete:
            # Load in the most recent version of the model.
            self.get(organisation_id=self.organisation_id)

            # See if the execution has completed.
            self._logger.debug('checking for execution %s to complete: %f', self.id, self.progress)
            complete = self.progress >= 100

            # Raise an exception if the execution failed.
            if complete and not self.success:
                raise ModelError(i18n.t('models.process_execution.execution_failed'))

            if complete:
                self._logger.debug('execution %s is complete', self.id)

            if (not wait) or complete:
                break

            # We are waiting, so block for a short while.
            sleep(self.__class__._API_UPDATE_WAIT_PERIOD)

        return complete

    @property
    def components(self):
        """
        Provides an iterator through the process execution's components.

        Returns:
            An iterator through the component objects.

        Raises:
            RequestError: if any get fails.
            ModelError: if a model could not be loaded or validated from the Fusion Platform<sup>&reg;</sup>.
        """
        return ProcessServiceExecution._models_from_api_path(self._session, self._get_path(self.__class__._PATH_COMPONENTS))
