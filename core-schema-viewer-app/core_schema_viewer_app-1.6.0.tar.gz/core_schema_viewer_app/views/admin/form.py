""" Admin forms
"""
from django import forms

from core_schema_viewer_app.views.user.forms import FormDefaultTemplate


class FormUnzip(FormDefaultTemplate):
    """Form to associate <oxygen> zip file with a template"""

    # Zip file to be associated with the schema
    zip_file = forms.FileField(
        label="Oxygen zip file", required=True, allow_empty_file=False
    )

    def set_default(self, widget="select", empty_label=True):
        super(FormUnzip, self).set_default(widget=widget, empty_label=empty_label)
