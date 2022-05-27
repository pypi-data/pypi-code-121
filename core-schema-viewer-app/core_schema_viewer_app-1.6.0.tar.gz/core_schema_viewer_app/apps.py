""" Apps file for setting core package when app is ready
"""
from django.apps import AppConfig

import core_schema_viewer_app.components.template_schema_viewer.watch as template_schema_viewer_watch


class SchemaViewerAppConfig(AppConfig):
    """Schema viewer application settings."""

    name = "core_schema_viewer_app"

    def ready(self):
        """Run when the app is ready.

        Returns:

        """
        import core_schema_viewer_app.permissions.discover as discover

        discover.init_permissions()
        template_schema_viewer_watch.init()
