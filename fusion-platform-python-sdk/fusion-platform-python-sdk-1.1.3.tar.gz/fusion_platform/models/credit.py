"""
Credit model class file.

author: Matthew Casey

&copy; [Digital Content Analysis Technology Ltd](https://www.d-cat.co.uk)
"""

from marshmallow import Schema, EXCLUDE

from fusion_platform.models import fields
from fusion_platform.models.model import Model


# Define the model schema classes. These are maintained from the API definitions.

class CreditSsdsSchema(Schema):
    """
    Nested schema class for runtime SSDs.
    """
    ssds = fields.List(fields.UUID(required=True), required=True)
    credits = fields.Decimal(required=True)

    class Meta:
        """
        When loading an object, make sure we exclude any unknown fields, rather than raising an exception, and put fields in their definition order.
        """
        unknown = EXCLUDE
        ordered = True


class CreditSchema(Schema):
    """
    Schema class for credit model.

    Each credit model has the following fields (and nested fields):

    .. include::credit.md
    """
    id = fields.UUID(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    created_at = fields.DateTime(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    updated_at = fields.DateTime(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    organisation_id = fields.UUID(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    # Removed lock.

    any_credits = fields.Decimal(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    cloud_storage_credits = fields.Decimal(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    registry_storage_credits = fields.Decimal(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    runtime_any_credits = fields.Decimal(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    runtime_ssds = fields.List(fields.Nested(CreditSsdsSchema()), allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    class Meta:
        """
        When loading an object, make sure we exclude any unknown fields, rather than raising an exception, and put fields in their definition order.
        """
        unknown = EXCLUDE
        ordered = True


class Credit(Model):
    """
    Credit model class providing attributes and methods to manipulate credit item details.
    """

    # Override the schema.
    _SCHEMA = CreditSchema()

    # Override the base model class name.
    _BASE_MODEL_CLASS_NAME = 'Organisation'  # A string to prevent circular imports.

    # Base path.
    _PATH_BASE = '/organisations/{organisation_id}/credits/{credit_id}'

    # Override the standard model paths.
    _PATH_GET = _PATH_BASE
