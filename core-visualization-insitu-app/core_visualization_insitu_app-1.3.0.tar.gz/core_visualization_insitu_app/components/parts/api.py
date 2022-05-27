"""
InSituPart api
"""

import json

import core_explore_tree_app.components.data.query as query_database_api
from core_visualization_insitu_app.components.builds import api as builds_api
from core_visualization_insitu_app.components.parts.models import InSituPart
from core_visualization_insitu_app.utils.dict import (
    get_list_inside_dict as utils_get_list,
)


def get_all_parts_names_list():
    """Return the list of all the parts names

    Returns:

    """
    parts = InSituPart.get_all_parts_names()

    return parts


def get_all_parts_names():
    """Return the list of all the parts names as tuples

    Returns:

    """
    parts = InSituPart.get_all_parts_names()
    parts_tuples = []
    for part in parts:
        parts_tuples.append((part, part))

    return parts_tuples


def toggle_part_selection(part_name):
    """Toggle the boolean that indicates if a part is selected or not.
    Return the part with the given part name

    Args:
        part_name:

    Returns:

    """
    return InSituPart.toggle_part_selection(part_name)


def set_parts(template_id):
    """Return part tuples, a list of tuples. Each tuple is a part.

    Returns:

    """
    # Get selected build
    build = builds_api.get_selected_build_name()
    # Query the database
    part_path = "dict_content.amBuildDB.amBuild.parts.part"
    part_name_path = "dict_content.amBuildDB.amBuild.parts.part.partName"
    part_id_path = "dict_content.amBuildDB.amBuild.parts.part.partID"
    build_filter = {"dict_content.amBuildDB.amBuild.generalInfo.buildID": build}
    projection = {part_path: 1}
    parts = query_database_api.execute_query(
        template_id, [json.dumps(build_filter)], json.dumps(projection)
    )
    # set parts objects
    for part_result in parts:
        part_dict = part_result.dict_content
        parts_list = utils_get_list(part_path, part_dict)
        # InSituParts_list is a list of dicts with 1 key/value
        for part_dict in parts_list:
            for elt in part_dict["part"]:
                elt = dict(elt)
                part_name = elt["partName"]
                part_id = elt["partID"]
                # part_dict value is the part number
                new_part = InSituPart.create_part(part_name, part_id)
                # We need one only default part selected
                if get_selected_part_name() is None:
                    new_part.is_selected = True
                new_part.save()
    return InSituPart.objects.all()


def get_part_by_name(part_name):
    """Return the part object with the given argument

    Args:
        part_name:

    Returns:

    """
    return InSituPart.get_part_by_name(part_name)


def get_selected_part_name():
    """Return the only one selected part object name

    Returns:

    """
    return InSituPart.get_selected_part_name()


def get_selected_part_id():
    """Return the only one selected part object id

    Returns:

    """
    return InSituPart.get_selected_part_id()


def delete_all_parts():
    """Delete all the InSituPart objects

    Returns:

    """
    return InSituPart.delete_all_parts()
