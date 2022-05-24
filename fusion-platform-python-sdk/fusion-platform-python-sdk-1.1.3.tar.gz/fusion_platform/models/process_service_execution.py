"""
Process service execution model class file.

author: Matthew Casey

&copy; [Digital Content Analysis Technology Ltd](https://www.d-cat.co.uk)
"""

from marshmallow import Schema, EXCLUDE
import os

from fusion_platform.models import fields
from fusion_platform.models.data import Data
from fusion_platform.models.model import Model
from fusion_platform.models.process_service_execution_log import ProcessServiceExecutionLog


# Define the model schema classes. These are maintained from the API definitions.

class ProcessServiceExecutionActionValueSchema(Schema):
    """
    Nested schema class for service action value.
    """
    name = fields.String(required=True)
    required = fields.Boolean(required=True)
    data_type = fields.String(required=True)
    default = fields.String(allow_none=True)
    validation = fields.String(allow_none=True)

    constant = fields.Boolean(allow_none=True)

    ssd_id = fields.UUID(allow_none=True)
    output = fields.Integer(allow_none=True)
    selector = fields.String(allow_none=True)
    data_id = fields.UUID(allow_none=True)

    expression = fields.String(allow_none=True)
    value = fields.String(allow_none=True)
    url = fields.Url(allow_none=True)
    advanced = fields.Boolean(allow_none=True)
    title = fields.String(allow_none=True)
    description = fields.String(allow_none=True)

    class Meta:
        """
        When loading an object, make sure we exclude any unknown fields, rather than raising an exception, and put fields in their definition order.
        """
        unknown = EXCLUDE
        ordered = True


class ProcessServiceExecutionActionSchema(Schema):
    """
    Nested schema class for service action.
    """
    name = fields.String(required=True)
    values = fields.List(fields.Nested(ProcessServiceExecutionActionValueSchema()), required=True)
    url = fields.Url(allow_none=True)
    title = fields.String(allow_none=True)
    description = fields.String(allow_none=True)

    class Meta:
        """
        When loading an object, make sure we exclude any unknown fields, rather than raising an exception, and put fields in their definition order.
        """
        unknown = EXCLUDE
        ordered = True


class ProcessServiceExecutionActionsSchema(Schema):
    """
    Schema class used to isolate actions for controller responses.
    """
    actions = fields.List(fields.Nested(ProcessServiceExecutionActionSchema()), allow_none=True)

    class Meta:
        """
        When loading an object, make sure we exclude any unknown fields, rather than raising an exception, and put fields in their definition order.
        """
        unknown = EXCLUDE
        ordered = True


class ProcessServiceExecutionMetricSchema(Schema):
    """
    Nested schema class for metrics which are recorded during execution.
    """
    date = fields.DateTime(allow_none=True)
    memory_total_bytes = fields.Integer(allow_none=True)
    memory_free_bytes = fields.Integer(allow_none=True)
    swap_total_bytes = fields.Integer(allow_none=True)
    swap_free_bytes = fields.Integer(allow_none=True)
    tmp_total_bytes = fields.Integer(allow_none=True)
    tmp_free_bytes = fields.Integer(allow_none=True)
    s3_transfer_bytes = fields.Integer(allow_none=True)
    external_transfer_bytes = fields.Integer(allow_none=True)
    comment = fields.String(allow_none=True)

    class Meta:
        """
        When loading an object, make sure we exclude any unknown fields, rather than raising an exception, and put fields in their definition order.
        """
        unknown = EXCLUDE
        ordered = True


class ProcessServiceExecutionOptionSchema(Schema):
    """
    Nested schema class for options which are used during execution.
    """
    name = fields.String(required=True)
    value = fields.String(allow_none=True)

    class Meta:
        """
        When loading an object, make sure we exclude any unknown fields, rather than raising an exception, and put fields in their definition order.
        """
        unknown = EXCLUDE
        ordered = True


class ProcessServiceExecutionSchema(Schema):
    """
    Schema class for process service execution model.

    Each process service execution model has the following fields (and nested fields):

    .. include::process_service_execution.md
    """
    id = fields.UUID(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    created_at = fields.DateTime(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    updated_at = fields.DateTime(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    organisation_id = fields.UUID(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    process_execution_id = fields.UUID(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    process_id = fields.UUID(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    service_id = fields.UUID(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    image_id = fields.UUID(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    name = fields.String(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    started_at = fields.DateTime(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    ended_at = fields.DateTime(allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    runtime = fields.Integer(allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    # Removed input_size.
    cpu = fields.Decimal(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    memory = fields.Decimal(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    actions = fields.List(fields.Nested(ProcessServiceExecutionActionSchema()), allow_none=True)
    options = fields.List(fields.Nested(ProcessServiceExecutionOptionSchema()), allow_none=True,
                          metadata={'read_only': True})  # Changed to prevent this being updated.
    inputs = fields.List(fields.UUID(required=True), allow_none=True, metadata={'hide': True})  # Changed to hide as an attribute.
    outputs = fields.List(fields.UUID(required=True), allow_none=True, metadata={'hide': True})  # Changed to hide as an attribute.
    intermediate = fields.Boolean(allow_none=True)
    # Removed task_id.
    # Removed task_definition_id.
    # Removed access_point_ids.
    # Removed security_group_id.
    success = fields.Boolean(allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    metrics = fields.List(fields.Nested(ProcessServiceExecutionMetricSchema()), allow_none=True,
                          metadata={'read_only': True})  # Changed to prevent this being updated.

    class Meta:
        """
        When loading an object, make sure we exclude any unknown fields, rather than raising an exception, and put fields in their definition order.
        """
        unknown = EXCLUDE
        ordered = True


class ProcessServiceExecution(Model):
    """
    Process service execution model class providing attributes and methods to manipulate process execution item details.
    """

    # Override the schema.
    _SCHEMA = ProcessServiceExecutionSchema()

    # Override the base model class name.
    _BASE_MODEL_CLASS_NAME = 'Organisation'  # A string to prevent circular imports.

    # Base path.
    _PATH_BASE = '/organisations/{organisation_id}/process_service_executions/{process_service_execution_id}'

    # Override the standard model paths.
    _PATH_GET = _PATH_BASE

    # Add in the custom model paths.
    _PATH_LOGS = f"{_PATH_BASE}/logs"

    @property
    def inputs(self):
        """
        Provides an iterator through the process execution component's inputs.

        Returns:
            An iterator through the input data objects.

        Raises:
            RequestError: if any get fails.
            ModelError: if a model could not be loaded or validated from the Fusion Platform<sup>&reg;</sup>.
        """
        inputs = self._model.get(self.__class__._FIELD_INPUTS, []) if self._model.get(self.__class__._FIELD_INPUTS) is not None else []

        return Data._models_from_api_ids(self._session, Data._get_ids_from_list(inputs, organisation_id=self.organisation_id))

    def download_log_file(self, path):
        """
        Downloads the log output from the component's execution to the specified path as a CSV file.

        Args:
            path: The path to save the log records to.

        Raises:
            RequestError if any get fails.
        """
        logs = ProcessServiceExecutionLog._models_from_api_path(self._session, self._get_path(self.__class__._PATH_LOGS), reverse=True)
        first = True

        try:
            with open(path, 'w') as file:
                for log in logs:
                    header, line = log.to_csv(exclude=['id', 'created_at', 'updated_at', 'process_service_execution_id'])

                    if first:
                        file.write(header)
                        file.write('\n')

                        first = False

                    file.write(line)
                    file.write('\n')
        except:
            # If an error occurred, delete the file.
            os.remove(path)

            # Make sure the error is raised.
            raise

    @property
    def outputs(self):
        """
        Provides an iterator through the process execution component's outputs.

        Returns:
            An iterator through the output data objects.

        Raises:
            RequestError: if any get fails.
            ModelError: if a model could not be loaded or validated from the Fusion Platform<sup>&reg;</sup>.
        """
        outputs = self._model.get(self.__class__._FIELD_OUTPUTS, []) if self._model.get(self.__class__._FIELD_OUTPUTS) is not None else []

        return Data._models_from_api_ids(self._session, Data._get_ids_from_list(outputs, organisation_id=self.organisation_id))
