""" Schema Viewer models
"""
from django.db import models

from core_main_app.permissions.utils import get_formatted_name
from core_schema_viewer_app.permissions import rights


class SchemaViewer(models.Model):
    class Meta(object):
        verbose_name = "core_schema_viewer_app"
        default_permissions = ()
        permissions = (
            (
                rights.schema_viewer_access,
                get_formatted_name(rights.schema_viewer_access),
            ),
            (
                rights.schema_viewer_sandbox_data_structure_access,
                get_formatted_name(rights.schema_viewer_sandbox_data_structure_access),
            ),
        )
