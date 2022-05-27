""" Template schema viewer api
"""
import logging

from core_main_app.commons import exceptions
from core_schema_viewer_app.components.template_schema_viewer.models import (
    TemplateSchemaViewer,
)

logger = logging.getLogger(__name__)


def upsert(template_schema_viewer):
    """Save or update TemplateSchemaViewer

    Args:
        template_schema_viewer:

    Returns:
        TemplateSchemaViewer(obj): TemplateSchemaViewer

    """
    return template_schema_viewer.save()


def get_all():
    """List all TemplateSchemaViewer

    Returns:
        TemplateSchemaViewer(obj): list of TemplateSchemaViewer

    """
    return TemplateSchemaViewer.get_all()


def get_by_template_id(template_id):
    """Return the object with the given template id.

    Args:
        template_id:

    Returns:
        TemplateSchemaViewer(obj): TemplateSchemaViewer

    """
    return TemplateSchemaViewer.get_by_template_id(template_id)


def get_by_id(pk):
    """Return the object with the given id.

    Args:
        pk:

    Returns:
        TemplateSchemaViewer(obj): TemplateSchemaViewer

    """
    return TemplateSchemaViewer.get_by_id(pk)


def get_default():
    """Return the default default object

    Returns:
        TemplateSchemaViewer(obj): TemplateSchemaViewer

    """
    return TemplateSchemaViewer.get_default()


def get_all_by_visibility(is_visible=True):
    """Return all TemplateSchemaViewer with the visibility given

    Returns:
        TemplateSchemaViewer(obj): list of TemplateSchemaViewer

    """
    return TemplateSchemaViewer.get_all_by_visibility(is_visible)


def toggle_visibility(template_schema_viewer):
    """Toggle the visibility of an object

    Args:
        template_schema_viewer:

    Returns:

    """
    template_schema_viewer.toggle_visibility()
    return upsert(template_schema_viewer)


def set_default(template_schema_viewer):
    """Toggle the current
        Toggle the given one

    Args:
        template_schema_viewer:

    Returns:

    """
    try:
        # switch the current to False
        default_template_schema_viewer = get_default()
        default_template_schema_viewer.toggle_default()
        upsert(default_template_schema_viewer)
    except exceptions.DoesNotExist as e:
        # in case there is no default template schema viewer yet
        # nothing to do, we could log it
        logger.warning("set_default threw an exception: %s" % str(e))

    # set template_schema_viewer to default
    template_schema_viewer.toggle_default()
    return upsert(template_schema_viewer)
