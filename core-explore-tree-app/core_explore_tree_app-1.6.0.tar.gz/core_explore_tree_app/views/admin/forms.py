""" Forms for admin views
"""
from builtins import object
from django import forms
from django_mongoengine.forms import DocumentForm

from core_explore_tree_app.components.query_ontology.models import QueryOntology
from core_main_app.components.template import api as template_api
from core_main_app.views.admin.commons.upload.forms import UploadForm


class UploadQueryOntologyForm(UploadForm):
    """Form to upload a new Query Ontology file"""

    templates_manager = forms.ChoiceField(
        label="Select the associated template",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request")
        super(UploadQueryOntologyForm, self).__init__(*args, **kwargs)
        self.fields["name"].label = "Enter OWL file name"
        self.fields["templates_manager"].label = "Select the associated template"
        self.fields["templates_manager"].choices = _get_templates_versions(
            request=request
        )


class EditOntologyForm(DocumentForm):
    title = forms.CharField(
        label="Enter OWL file name",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Type the new name"}
        ),
    )
    template = forms.ChoiceField(
        label="Select the associated template",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta(object):
        document = QueryOntology
        fields = ["title", "template"]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(EditOntologyForm, self).__init__(*args, **kwargs)
        self.fields["template"].choices = _get_templates_versions(request=self.request)

    def clean_template(self):
        data = self.cleaned_data["template"]
        return template_api.get(data, request=self.request)


def _get_templates_versions(request):
    """Get templates versions.

    Returns:
        List of templates versions.

    """
    templates = []
    # display all template, global and from users
    template_list = template_api.get_all(request=request)
    for template in template_list:
        templates.append((template.id, template.display_name))
    return templates
