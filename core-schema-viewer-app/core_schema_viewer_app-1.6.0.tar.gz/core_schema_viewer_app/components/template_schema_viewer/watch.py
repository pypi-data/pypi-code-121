""" Handle signals.
"""
from core_main_app.commons import exceptions
from core_main_app.components.template.models import Template
from core_main_app.system import api as template_api
from core_schema_viewer_app.components.template_schema_viewer import (
    api as template_schema_viewer_api,
)
from core_schema_viewer_app.components.template_schema_viewer.models import (
    TemplateSchemaViewer,
)
from signals_utils.signals.mongo import connector, signals


def init():
    """Connect to Template object events and create template schema viewer for existing templates"""
    connector.connect(post_save_template, signals.post_save, Template)
    create_template_schema_viewer_from_templates_in_db()


def post_save_template(sender, document, **kwargs):
    """Method executed after a saving of a Template object.
    Args:
        sender: Class.
        document: Template document.
        **kwargs: Args.

    """
    try:
        template_schema_viewer_api.get_by_template_id(document.pk)
    except exceptions.DoesNotExist as e:
        # upsert if does not exist for this template
        template_schema_viewer = TemplateSchemaViewer(template=document)
        return template_schema_viewer_api.upsert(template_schema_viewer)


def create_template_schema_viewer_from_templates_in_db():
    """Get all template in DB and create a TemplateSchemaViewer for each"""
    # get all template in DB
    templates = template_api.get_all_templates()
    for template in templates:
        try:
            # check if the TemplateSchemaViewer does not exist already
            template_schema_viewer_api.get_by_template_id(template.pk)
        except exceptions.DoesNotExist:
            # create the TemplateSchemaViewer associated only if it does not exist already
            template_schema_viewer = TemplateSchemaViewer(template=template)
            template_schema_viewer_api.upsert(template_schema_viewer)
