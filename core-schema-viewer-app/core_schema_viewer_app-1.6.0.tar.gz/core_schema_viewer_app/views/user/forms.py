""" Form needed for the user part
"""
import logging

from django import forms

from core_main_app.commons.exceptions import DoesNotExist
from core_schema_viewer_app.components.template_schema_viewer import (
    api as template_schema_viewer_api,
)

logger = logging.getLogger(__name__)


class FormDefaultTemplate(forms.Form):
    """Form to get all the visible templates, with as first choice, the default template if it exists."""

    # Schema showed in the form,
    schema = forms.ChoiceField(
        label="Schema",
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super(FormDefaultTemplate, self).__init__(*args, **kwargs)
        self.set_default()

    def set_default(self, widget="select", empty_label=True):
        """Populate the form with the visible template, and set the default one if it exists.

        Args:
            widget: name of the widget used to represent the form (default: select):
                _"select": Select
                _"radio": RadioSelect
            empty_label: True is an empty label has to be created, False else. (default: True)

        Returns:

        """
        # Set the widget
        if widget == "radio":
            self.fields["schema"].widget = forms.RadioSelect()
        else:
            self.fields["schema"].widget = forms.Select()

        # Populate the form with all the visible templates
        visible_template_schema_viewer_list = (
            template_schema_viewer_api.get_all_by_visibility(True)
        )
        self.fields["schema"].choices = [
            (element.template.id, element.template.display_name)
            for element in visible_template_schema_viewer_list
        ]

        # Create an empty label is needed
        if not empty_label:
            self.fields["schema"].empty_label = None
        else:
            self.fields["schema"].empty_label = "Select a schema..."

        # Set the default template if it exists
        try:
            self.initial[
                "schema"
            ] = template_schema_viewer_api.get_default().template.id
        except DoesNotExist as e:
            logger.warning("set_default threw an exception: %s" % str(e))
