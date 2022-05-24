"""
Process service execution log model class file.

author: Matthew Casey

&copy; [Digital Content Analysis Technology Ltd](https://www.d-cat.co.uk)
"""

from marshmallow import Schema, EXCLUDE

from fusion_platform.models import fields
from fusion_platform.models.model import Model


# Define the model schema classes. These are maintained from the API definitions.

class ProcessServiceExecutionLogSchema(Schema):
    """
    Schema class for process service execution log model.

    Each process service execution log model has the following fields (and nested fields):

    .. include::process_service_execution_log.md
    """
    id = fields.UUID(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    created_at = fields.DateTime(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    updated_at = fields.DateTime(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    process_service_execution_id = fields.UUID(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    logged_at = fields.DateTime(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    message = fields.String(allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    class Meta:
        """
        When loading an object, make sure we exclude any unknown fields, rather than raising an exception, and put fields in their definition order.
        """
        unknown = EXCLUDE
        ordered = True


class ProcessServiceExecutionLog(Model):
    """
    Process service execution log model class providing attributes and methods to manipulate process execution item details.
    """

    # Override the schema.
    _SCHEMA = ProcessServiceExecutionLogSchema()
