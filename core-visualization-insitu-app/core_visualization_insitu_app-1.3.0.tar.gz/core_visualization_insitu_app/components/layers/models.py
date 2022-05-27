"""
InSituLayers models
"""

from django_mongoengine import fields, Document
from mongoengine import errors as mongoengine_errors

from core_main_app.commons import exceptions


class InSituLayer(Document):
    """Data Structure to handle the selected InSituLayer"""

    name = fields.StringField(blank=True)
    is_selected = fields.BooleanField(default=False)

    @staticmethod
    def get_all_layers_names():
        """Return the list of all the layers names

        Returns:

        """
        return InSituLayer.objects.all().values_list("name")

    @staticmethod
    def create_layer(layer):
        """Create and return a layer object

        Args:
            layer:

        Returns:

        """
        return InSituLayer.objects.create(name=layer)

    @staticmethod
    def get_layer_by_name(layer_name):
        """Return the layer object with the given argument

        Args:
            layer_name:

        Returns:

        """
        return InSituLayer.objects.get(name=layer_name)

    @staticmethod
    def get_selected_layer_name():
        """Return the only one selected layer object name

        Returns:

        """
        selected_layer = InSituLayer.objects.get(is_selected=True)
        return selected_layer.name

    @staticmethod
    def toggle_layer_selection(layer_name):
        """Toggle the boolean that indicates if a layer is selected or not.
        Return the layer with the given layer name

        Args:
            layer_name:

        Returns:

        """
        for layer in InSituLayer.objects.all():
            if layer.name == layer_name:
                InSituLayer.objects.filter(name=layer.name).update(is_selected=True)
            else:
                InSituLayer.objects.filter(name=layer.name).update(is_selected=False)

        return InSituLayer.objects.get(name=layer_name)

    @staticmethod
    def delete_all_layers():
        """Delete all layer objects

        Returns:

        """
        InSituLayer.objects.all().delete()

    @staticmethod
    def get_selected_layer():
        """Return the selected layer

        Returns:

        """
        try:
            return InSituLayer.objects.get(is_selected=True)
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(str(e))
        except Exception as ex:
            raise exceptions.ModelError(str(ex))
