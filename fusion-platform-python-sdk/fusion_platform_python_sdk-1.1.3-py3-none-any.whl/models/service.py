"""
Service model class file.

author: Matthew Casey

&copy; [Digital Content Analysis Technology Ltd](https://www.d-cat.co.uk)
"""

from marshmallow import Schema, EXCLUDE

from fusion_platform.models import fields
from fusion_platform.models.model import Model


# Define the model schema classes. These are maintained from the API definitions.

class ServiceActionValueSchema(Schema):
    """
    Nested schema class for service action value.
    """
    name = fields.String(required=True)
    required = fields.Boolean(required=True)
    data_type = fields.String(required=True)
    default = fields.String(allow_none=True)
    validation = fields.String(allow_none=True)

    # Values can be:
    #  constant,
    #  calculated from an expression (using previously calculated values),
    #  taken from an SSD output,
    #  obtained from a URL, or
    #  user provided (with a default).

    constant = fields.Boolean(allow_none=True)

    ssd_id = fields.UUID(allow_none=True)
    output = fields.Integer(allow_none=True)
    selector = fields.String(allow_none=True)

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


class ServiceActionSchema(Schema):
    """
    Nested schema class for service action.
    """
    name = fields.String(required=True)
    values = fields.List(fields.Nested(ServiceActionValueSchema()), required=True)
    url = fields.Url(allow_none=True)
    title = fields.String(allow_none=True)
    description = fields.String(allow_none=True)

    class Meta:
        """
        When loading an object, make sure we exclude any unknown fields, rather than raising an exception, and put fields in their definition order.
        """
        unknown = EXCLUDE
        ordered = True


class ServiceDefinitionLinkageSchema(Schema):
    """
    Nested schema class for service definition linkage.
    """
    ssd_id = fields.UUID(required=True)
    input = fields.Integer(required=True)

    class Meta:
        """
        When loading an object, make sure we exclude any unknown fields, rather than raising an exception, and put fields in their definition order.
        """
        unknown = EXCLUDE
        ordered = True


class ServiceDefinitionSchema(Schema):
    """
    Nested schema class for service definition.
    """
    ssd_id = fields.UUID(required=True)
    output = fields.Integer(required=True)
    linkages = fields.List(fields.Nested(ServiceDefinitionLinkageSchema()), required=True)

    class Meta:
        """
        When loading an object, make sure we exclude any unknown fields, rather than raising an exception, and put fields in their definition order.
        """
        unknown = EXCLUDE
        ordered = True


class ServiceInputExpressionSchema(Schema):
    """
    Nested schema class for service input expression.
    """
    lhs_ssd_id = fields.UUID(required=True)
    lhs_input = fields.Integer(required=True)
    expression = fields.String(required=True)
    rhs_ssd_id = fields.UUID(required=True)
    rhs_input = fields.Integer(required=True)

    class Meta:
        """
        When loading an object, make sure we exclude any unknown fields, rather than raising an exception, and put fields in their definition order.
        """
        unknown = EXCLUDE
        ordered = True


class ServiceOptionExpressionSchema(Schema):
    """
    Nested schema class for service option expression.
    """
    lhs_ssd_id = fields.UUID(required=True)
    lhs_name = fields.String(required=True)
    expression = fields.String(required=True)
    rhs_ssd_id = fields.UUID(required=True)
    rhs_name = fields.String(required=True)

    class Meta:
        """
        When loading an object, make sure we exclude any unknown fields, rather than raising an exception, and put fields in their definition order.
        """
        unknown = EXCLUDE
        ordered = True


class ServiceValidationSchema(Schema):
    """
    Nested schema class for service validation.
    """
    expression = fields.String(required=True)
    message = fields.String(required=True)

    class Meta:
        """
        When loading an object, make sure we exclude any unknown fields, rather than raising an exception, and put fields in their definition order.
        """
        unknown = EXCLUDE
        ordered = True


class ServiceSchema(Schema):
    """
    Schema class for service model.

    Each service model has the following fields (and nested fields):

    .. include::service.md
    """
    id = fields.UUID(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    created_at = fields.DateTime(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    updated_at = fields.DateTime(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    organisation_id = fields.UUID(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    ssd_id = fields.UUID(required=True)

    version = fields.Integer(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    approval_status = fields.String(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    # Removed latest.
    featured = fields.String(allow_none=True)
    show_in_latest = fields.Boolean(allow_none=True)  # Changed to optional.
    name = fields.String(required=True)

    categories = fields.List(fields.String(required=True), required=True)
    keywords = fields.List(fields.String(required=True), required=True)

    image_id = fields.UUID(required=True)

    definition = fields.List(fields.Nested(ServiceDefinitionSchema()), allow_none=True)
    actions = fields.List(fields.Nested(ServiceActionSchema()), allow_none=True)
    urls = fields.List(fields.Url(required=True), allow_none=True)
    cidrs = fields.List(fields.String(required=True), allow_none=True)

    input_expressions = fields.List(fields.Nested(ServiceInputExpressionSchema()), allow_none=True)
    input_validations = fields.List(fields.Nested(ServiceValidationSchema()), allow_none=True)
    option_expressions = fields.List(fields.Nested(ServiceOptionExpressionSchema()), allow_none=True)
    option_validations = fields.List(fields.Nested(ServiceValidationSchema()), allow_none=True)

    license_id = fields.UUID(required=True)

    charge_expression_platform = fields.String(allow_none=True)  # Changed to optional.
    charge_expression_owner = fields.String(allow_none=True)  # Changed to optional.

    organisations = fields.List(fields.UUID(required=True), allow_none=True)
    geographic_regions = fields.List(fields.String(required=True), allow_none=True)

    # Removed creator.
    # Removed approver.

    documentation_summary = fields.String(required=True)
    documentation_description = fields.String(required=True)
    documentation_assumptions = fields.String(required=True)
    documentation_performance = fields.String(required=True)
    documentation_actions = fields.String(required=True)
    documentation_inputs = fields.List(fields.String(required=True), allow_none=True)  # Added pseudo-parameter.
    documentation_outputs = fields.List(fields.String(required=True), allow_none=True)  # Added pseudo-parameter.
    documentation_options = fields.List(fields.String(required=True), allow_none=True)  # Added pseudo-parameter.

    class Meta:
        """
        When loading an object, make sure we exclude any unknown fields, rather than raising an exception, and put fields in their definition order.
        """
        unknown = EXCLUDE
        ordered = True


class Service(Model):
    """
    Service model class providing attributes and methods to manipulate service item details.
    """

    # Override the schema.
    _SCHEMA = ServiceSchema()

    # Override the base model class name.
    _BASE_MODEL_CLASS_NAME = 'Organisation'  # A string to prevent circular imports.

    # Base path.
    _PATH_BASE = '/organisations/{organisation_id}/services/{service_id}'

    # Override the standard model paths.
    _PATH_DELETE = _PATH_BASE
    _PATH_GET = _PATH_BASE
    _PATH_PATCH = _PATH_BASE
