"""
Documentation generator file.

author: Matthew Casey

&copy; [Digital Content Analysis Technology Ltd](https://www.d-cat.co.uk)

Use this script to build the SDK HTML documentation.

Usage:
  python documentation.py <path_to_engine_translations>

where

- `path_to_engine_translations` is the path to the engine "translations.py" file.
"""

import i18n
import importlib.util
from marshmallow import fields
import os
import sys

from fusion_platform.common.utilities import string_camel_to_underscore
from fusion_platform.models.credit import CreditSchema
from fusion_platform.models.data import DataSchema
from fusion_platform.models.data_file import DataFileSchema
from fusion_platform.models.model import Model
from fusion_platform.models.organisation import OrganisationSchema
from fusion_platform.models.process import ProcessSchema
from fusion_platform.models.process_execution import ProcessExecutionSchema
from fusion_platform.models.process_service_execution import ProcessServiceExecutionSchema
from fusion_platform.models.process_service_execution_log import ProcessServiceExecutionLogSchema
from fusion_platform.models.service import ServiceSchema
from fusion_platform.models.user import UserSchema

# Check the usage.
if len(sys.argv) <= 1:
    print("Usage: python documentation.py <path_to_engine_translations>")
    exit(1)

# Load in the translations file from the engine so that we can extract the model field descriptions.
spec = importlib.util.spec_from_file_location("translations", sys.argv[1])
translations = importlib.util.module_from_spec(spec)
spec.loader.exec_module(translations)


def get_schema_name(schema):
    """
    Converts a schema object's name into a more friendly name.

    Args:
        schema: The schema object.

    Returns:
        The friendly name.
    """
    return schema.__class__.__name__.replace('Schema', '')


def output_schema_fields(schema, level=0, file=None):
    """
    Recursive method to output the documentation for a particular schema (or nested schema). This will write a Markdown file for a top-level schema.

    Args:
        schema: The schema to traverse.
        level: The nesting level. 0 indicates a top-level schema.
        file: The optional file used to write the documentation to.
    """
    schema_name = string_camel_to_underscore(get_schema_name(schema))

    # Create the documentation file for the top-level schema.
    if level == 0:
        filename = os.path.join('fusion_platform', 'models', f"{schema_name}.md")
        print(f"Creating {filename}")
        file = open(filename, 'w')

    # Step through every field in the schema and output its documentation to the file.
    for field in schema.fields:
        # Ignore any hidden fields.
        if Model._METADATA_HIDE not in schema.fields[field].metadata:
            # Get the description for the field. This comes from the engine translations which have been loaded, or the metadata for any pseudo-field.
            default = schema.fields[field].metadata.get('description', '')
            description = i18n.t(f"models.{schema_name.replace('_', '.', 1)}.{field}.description", default=default)

            # Output the field to the file.
            file.write(f"{'    ' * level}* **{field}**: {description}\n")

            # If the field has a nested schema, then recursively step through its fields.
            if hasattr(schema.fields[field], 'inner') and isinstance(schema.fields[field].inner, fields.Nested) and hasattr(schema.fields[field].inner, 'nested'):
                nested = schema.fields[field].inner.nested
                output_schema_fields(nested, level + 1, file)

    # Make sure we close the file at the end.
    if (level == 0) and (file is not None):
        file.close()


# Output the documentation for all schemas.
schemas = [CreditSchema(), DataSchema(), DataFileSchema(), OrganisationSchema(), ProcessSchema(), ProcessExecutionSchema(), ProcessServiceExecutionSchema(),
           ProcessServiceExecutionLogSchema(), ServiceSchema(), UserSchema()]

for schema in schemas:
    output_schema_fields(schema)
