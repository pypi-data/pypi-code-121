""" Template schema viewer
"""
from django_mongoengine import Document, fields
from mongoengine import errors as mongoengine_errors
from mongoengine.queryset.base import CASCADE

from core_main_app.commons import exceptions
from core_main_app.components.template.models import Template


class TemplateSchemaViewer(Document):
    """Collection to represent, all the attributes related to a template used by the schema viewer.

    Template: The selected template.
    is_default: True if the template is the default one.
    is_visible: True if the template has to be shown in the different forms.

    """

    template = fields.ReferenceField(Template, blank=False, reverse_delete_rule=CASCADE)
    is_default = fields.BooleanField(default=False, blank=False)
    is_visible = fields.BooleanField(default=True, blank=False)

    @staticmethod
    def get_all():
        """Get all TemplateSchemaViewer.

        Returns: List of TemplateSchemaViewer

        """
        return TemplateSchemaViewer.objects.all()

    @staticmethod
    def get_all_template_id(is_visible=True):
        """Get all template IDs with the visibility given.

        Returns: List of visible template IDs.

        """
        not_visible_templates = list(
            TemplateSchemaViewer.objects.filter(is_visible=is_visible).values_list(
                "template"
            )
        )
        return [str(template.id) for template in not_visible_templates]

    @staticmethod
    def get_by_template_id(template_id):
        """Return the object with the given template id.

        Args:
            template_id:

        Returns:
            TemplateSchemaViewer(obj): TemplateSchemaViewer object

        """
        try:
            return TemplateSchemaViewer.objects.get(template=str(template_id))
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(str(e))
        except Exception as ex:
            raise exceptions.ModelError(str(ex))

    @staticmethod
    def get_by_id(pk):
        """Return the object with the given id.

        Args:
            pk:

        Returns:
            TemplateSchemaViewer(obj): TemplateSchemaViewer object

        """
        try:
            return TemplateSchemaViewer.objects.get(pk=str(pk))
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(str(e))
        except Exception as ex:
            raise exceptions.ModelError(str(ex))

    @staticmethod
    def get_default():
        """Return the default default object

        Args:

        Returns:
            TemplateSchemaViewer(obj): TemplateSchemaViewer object

        """
        try:
            return TemplateSchemaViewer.objects.get(is_default=True)
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(str(e))
        except Exception as ex:
            raise exceptions.ModelError(str(ex))

    @staticmethod
    def get_all_by_visibility(is_visible=True):
        """Return all TemplateSchemaViewer with the visibility given

        Returns:
            TemplateSchemaViewer(obj): list of TemplateSchemaViewer

        """
        return TemplateSchemaViewer.objects.filter(is_visible=is_visible).all()

    def toggle_visibility(self):
        """toggle the visibility of an object

        Args:

        Returns:

        """
        self.is_visible = not self.is_visible

    def toggle_default(self):
        """toggle the default of an object

        Args:

        Returns:

        """
        self.is_default = not self.is_default
        # the default is necessary visible
        if self.is_default is True:
            self.is_visible = True
