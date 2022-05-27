"""
InsituBuild api
"""

import json

import core_explore_tree_app.components.data.query as query_database_api
import core_visualization_insitu_app.components.projects.api as projects_api
from core_visualization_insitu_app.components.builds.models import InSituBuild
from core_visualization_insitu_app.utils.dict import (
    get_dict_path_value as utils_get_value,
)


def get_all_builds_names_list():
    """Return the list of all the builds names in a list

    Returns:

    """
    builds = InSituBuild.get_all_builds_names()

    return builds


def get_all_builds_names():
    """Return the list of all the builds names in a list of tuples

    Returns:

    """
    builds = InSituBuild.get_all_builds_names()
    builds_tuples = []
    for build in builds:
        builds_tuples.append((build, build))

    return builds_tuples


def toggle_build_selection(build_name):
    """Toggle the boolean that indicates if a build is selected or not.
    Return the build with the given build name

    Args:
        build_name:

    Returns:

    """
    return InSituBuild.toggle_build_selection(build_name)


def set_builds(template_id):
    """Return build tuples, a list of tuples. Each tuple is a build.

    Returns:

    """
    # Get selected project
    project = projects_api.get_selected_project_name()

    # Query the database
    build_path = "dict_content.amBuildDB.amBuild.generalInfo.buildID"
    project_filter = {"dict_content.amBuildDB.amBuild.projectID": project}
    projection = {build_path: 1}
    builds = query_database_api.execute_query(
        template_id, [json.dumps(project_filter)], json.dumps(projection)
    )

    # set builds objects
    for build_result in builds:
        build_dict = build_result.dict_content
        build = utils_get_value(build_dict, build_path)
        new_build = InSituBuild.create_build(build)
        # We need one only default build selected
        if get_selected_build_name() is None:
            new_build.is_selected = True
        new_build.save()

    return InSituBuild.objects.all()


def get_build_by_name(build_name):
    """Return the build object with the given argument

    Args:
        build_name:

    Returns:

    """
    return InSituBuild.get_build_by_name(build_name)


def get_selected_build_name():
    """Return the only one selected build object name

    Returns:

    """
    build_name = InSituBuild.get_selected_build_name()
    if build_name is None:
        return None

    return build_name


def delete_all_builds():
    """Delete all the InSituBuild objects

    Returns:

    """
    return InSituBuild.delete_all_builds()
