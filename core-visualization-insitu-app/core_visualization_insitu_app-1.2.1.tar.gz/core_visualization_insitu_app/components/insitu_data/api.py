"""
InsSituData api
"""

from core_visualization_insitu_app.components.builds import api as builds_api
from core_visualization_insitu_app.components.insitu_data.models import InSituData
from core_visualization_insitu_app.components.parts import api as parts_api
from core_visualization_insitu_app.components.projects import api as projects_api


def get_all_data():
    """Return the list of all the insitu_data

    Returns:

    """
    return InSituData.get_all_data()


def get_data(project, build, part):
    """Get all insitu_data objects having the same project, build and part.
    Should be 7 of them (3 tabs for data_name builds command and 2 tabs for data_name melt pool and layer wise)

    Args:
        project:
        build:
        part:

    Returns:

    """
    return InSituData.get_data(project, build, part)


def get_data_by_tab_name(data_name, tab):
    """Return a single insitu_data object

    Args:
        data_name:
        tab:

    Returns:

    """
    project = projects_api.get_selected_project_name()
    build = builds_api.get_selected_build_name()
    part = parts_api.get_selected_part_name()
    return InSituData.get_data_by_tab_name(project, build, part, data_name, tab)


def change_active_image(data_name, tab, active_image):
    """Change the active image from a single insitu_data object and return this image

    Args:
        data_name:
        tab:
        active_image:

    Returns:

    """
    project = projects_api.get_selected_project_name()
    build = builds_api.get_selected_build_name()
    part = parts_api.get_selected_part_name()
    return InSituData.change_active_image(
        project, build, part, data_name, tab, active_image
    )


def get_all_table():
    """Return list of list of all information in the table in the admin view for insitu data

    Returns:

    """
    insitu_data_objects = get_all_data()
    data_table = []
    for insitu_data_object in insitu_data_objects:
        total_layers = insitu_data_object.layer_numbers[-1]
        if total_layers > 0:
            data_name = insitu_data_object.data_name
            tab_number = insitu_data_object.tab
            data_line = [
                insitu_data_object.project,
                insitu_data_object.build,
                insitu_data_object.part,
                data_name,
                tab_number,
                total_layers,
            ]
            data_table.append(data_line)

    return data_table


def create_data(project, build, part, data_name, tab, images=None, layers=None):
    """Create an insitu object

    Args:
        project:
        build:
        part:
        data_name:
        tab:
        images:
        layers:

    Returns:

    """
    return InSituData.create_data(project, build, part, data_name, tab, images, layers)


def get_data_by_name_all_tabs(data_name):
    """Return 2 or 3 insitu objects (same project, build, part, data_name) and different tab

    Args:
        data_name:

    Returns:

    """
    project = projects_api.get_selected_project_name()
    build = builds_api.get_selected_build_name()
    part = parts_api.get_selected_part_name()
    return InSituData.get_data_by_name_all_tabs(project, build, part, data_name)


def delete_all_data():
    """Delete all insitu_data objects

    Returns:

    """
    InSituData.delete_all_data()


def update_data(data_name, tab, layer_number, active_image):
    """Update the the layer_number and active_image of an insitu data object

    Args:
        data_name:
        tab:
        layer_number:
        active_image:

    Returns:

    """
    project = projects_api.get_selected_project_name()
    build = builds_api.get_selected_build_name()
    part = parts_api.get_selected_part_name()
    return InSituData.update_data(
        project, build, part, data_name, tab, layer_number, active_image
    )


def get_title(images, layers, layer_number=None):
    """Get the title of an image displayed. The title format is "Project, Build, Part, Layer number"

    Args:
        images:
        layers:
        layer_number:

    Returns:

    """
    if (len(images) > 0) and (len(layers) > 0):
        if layer_number is None:
            layer_number = layers[0]

        title = (
            projects_api.get_selected_project_name()
            + ", "
            + builds_api.get_selected_build_name()
            + ", "
            + parts_api.get_selected_part_name()
            + ", "
            + " layer "
            + str(layer_number)
        )

    else:
        title = "No Data Available"

    return title


def reset_default_data(project, build, part):
    """Return the insitu_data objects with the according arguments,
    and put back the 1st layer as the one which is displayed

    Args:
        project:
        build:
        part:

    Returns:

    """

    return InSituData.reset_default_data(project, build, part)
