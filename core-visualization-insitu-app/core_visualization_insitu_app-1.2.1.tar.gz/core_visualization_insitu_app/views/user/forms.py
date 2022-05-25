""" Forms for user views
"""
from django import forms


class SelectProjectDropDown(forms.Form):
    """Form to select what project to visualize"""

    projects = forms.ChoiceField(
        label="Select a project", required=True, widget=forms.Select()
    )

    def __init__(self):
        super(SelectProjectDropDown, self).__init__()


class SelectBuildDropDown(forms.Form):
    """Form to select what build to visualize"""

    builds = forms.ChoiceField(
        label="Select a build", required=True, widget=forms.Select()
    )

    def __init__(self, builds=None, selected=None, *args):
        super(SelectBuildDropDown, self).__init__(*args)
        if builds:
            self.fields["builds"].choices = builds
        if selected:
            self.fields["builds"].initial = [selected]


class SelectPartDropDown(forms.Form):
    """Form to select what part to visualize"""

    parts = forms.ChoiceField(
        label="Select a part", required=True, widget=forms.Select()
    )

    def __init__(self, parts=None, selected=None, *args):
        super(SelectPartDropDown, self).__init__(*args)
        if parts:
            self.fields["parts"].choices = parts
        if selected:
            self.fields["parts"].initial = [selected]
