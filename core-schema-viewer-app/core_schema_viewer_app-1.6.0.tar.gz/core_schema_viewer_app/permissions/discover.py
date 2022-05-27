""" Initialize permissions for core schema viewer app
"""
from django.contrib.auth.models import Group, Permission
import logging

import core_main_app.permissions.rights as main_rights
import core_schema_viewer_app.permissions.rights as schema_viewer_rights

logger = logging.getLogger(__name__)


def init_permissions():
    """Initialization of groups and permissions.

    Returns:

    """
    try:
        # Get or Create the default group
        default_group, created = Group.objects.get_or_create(
            name=main_rights.default_group
        )
        anonymous_group, created = Group.objects.get_or_create(
            name=main_rights.anonymous_group
        )
        # Get schema_viewer permissions
        schema_viewer_access_perm = Permission.objects.get(
            codename=schema_viewer_rights.schema_viewer_access
        )
        schema_viewer_sandbox_data_structure_access_perm = Permission.objects.get(
            codename=schema_viewer_rights.schema_viewer_sandbox_data_structure_access
        )

        # Add permissions to default group
        default_group.permissions.add(
            schema_viewer_access_perm,
            schema_viewer_sandbox_data_structure_access_perm,
        )
        anonymous_group.permissions.add(
            schema_viewer_access_perm,
            schema_viewer_sandbox_data_structure_access_perm,
        )
    except Exception as e:
        logger.error("ERROR : Impossible to init the permissions : " + str(e))
