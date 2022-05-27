"""
InSituLayer api
"""

import json

import core_explore_tree_app.components.data.query as query_database_api
from core_visualization_insitu_app.components.builds import api as builds_api
from core_visualization_insitu_app.components.layers.models import InSituLayer


def get_all_layers_names():
    """Return the list of all the layers names

    Returns:

    """
    return InSituLayer.get_all_layers_names()


def toggle_layer_selection(layer_name):
    """Toggle the boolean that indicates if a layer is selected or not.
    Return the layer with the given layer name

    Args:
        layer_name:

    Returns:

    """
    return InSituLayer.toggle_layer_selection(layer_name)


def set_layers(template_id):
    """Return layer tuples, a list of tuples. Each tuple is a layer.

    Returns:

    """
    # Get selected build
    build = builds_api.get_selected_build_name()

    # Query the database
    build_filter = {"dict_content.amBuildDB.amBuild.generalInfo.buildID": build}
    projection = {"dict_content.amMonitoringDataSetDB.inSItuMonitoringItem.id": 1}
    layers = query_database_api.execute_query(
        template_id, [json.dumps(build_filter)], json.dumps(projection)
    )

    # set layers objects
    for layer_result in layers:
        layer = layer_result.dict_content[0]
        new_layer = InSituLayer(name=layer, is_selected=False)
        new_layer.save()

    return InSituLayer.objects.all()


def get_layer_by_name(layer_name):
    """Return the layer object with the given argument

    Args:
        layer_name:

    Returns:

    """
    return InSituLayer.get_layer_by_name(layer_name)


def get_selected_layer_name():
    """Return the only one selected layer object name

    Returns:

    """
    return InSituLayer.get_selected_layer_name()


def delete_all_layers():
    """Delete all the InSituLayer objects

    Returns:

    """
    return InSituLayer.delete_all_layers()
