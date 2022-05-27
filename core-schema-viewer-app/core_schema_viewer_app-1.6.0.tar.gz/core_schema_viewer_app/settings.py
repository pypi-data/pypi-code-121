""" core schema viewer app settings
"""
from django.conf import settings

if not settings.configured:
    settings.configure()

PARSER_DOWNLOAD_DEPENDENCIES = getattr(settings, "PARSER_DOWNLOAD_DEPENDENCIES", False)
SANDBOX_STRUCTURES_MAX_DAYS_IN_DATABASE = getattr(
    settings, "SANDBOX_STRUCTURES_MAX_DAYS_IN_DATABASE", 7
)
SCHEMA_VIEWER_MENU_NAME = getattr(settings, "SCHEMA_VIEWER_MENU_NAME", "Schema Viewer")
