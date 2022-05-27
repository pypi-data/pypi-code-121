""" Forms for Cache options
"""
from django import forms


class FormSelectDatabaseObject(forms.Form):
    """Form to select which element from the database to cache"""

    nodes = forms.ChoiceField(
        label="nodes",
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super(FormSelectDatabaseObject, self).__init__(*args, **kwargs)

    def set_objects(self, nodes_list, widget="select", empty_label=True):
        """Populate the form with the existing Nodes from the tree.

        Args:
            widget: name of the widget used to represent the form (default: select):
                _"select": Select
                _"radio": RadioSelect
            empty_label: True is an empty label has to be created, False else. (default: True)
            nodes_list: list of nodes name
        Returns:

        """
        # Set the widget
        if widget == "radio":
            self.fields["nodes"].widget = forms.RadioSelect()
        else:
            self.fields["nodes"].widget = forms.Select()

        # Populate the form with all the name of the direct nodes
        elements_list = []
        for element in nodes_list:
            # Get the name of the nodes
            element_name_index = (element.name).index("#")
            element_name = (element.name)[element_name_index + 1 :]
            elements_list.append((element.id, element_name))

        self.fields["nodes"].choices = elements_list

        # Create an empty label is needed
        if not empty_label:
            self.fields["nodes"].empty_label = None
        else:
            self.fields["nodes"].empty_label = "Select a database object..."
