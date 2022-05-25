""" Admin Ajax visualization Insitu
"""

import json
import logging

from django.core.cache import caches
from django.http import HttpResponse
from django.http import HttpResponseBadRequest

import core_explore_tree_app.components.query_ontology.api as query_ontology_api
from core_explore_tree_app.components.navigation.api import (
    create_navigation_tree_from_owl_file,
)
from core_main_app.commons import exceptions
from core_visualization_insitu_app.components.builds import api as builds_api
from core_visualization_insitu_app.components.insitu_data import api as insitu_data_api
from core_visualization_insitu_app.components.insitu_data import (
    operations as insitu_data_operations,
)
from core_visualization_insitu_app.components.parts import api as parts_api
from core_visualization_insitu_app.components.projects import api as projects_api
from core_visualization_insitu_app.utils import parser as utils_parser

logger = logging.getLogger(__name__)
navigation_cache = caches["navigation"]


def build_visualization_data(request):
    """Build data table object"""
    error = None
    active_ontology = None

    logger.info("START load visualization data")
    try:
        # Set up the needed explore tree related objects to get the queries
        # get the active ontology
        active_ontology = query_ontology_api.get_active()
    except exceptions.DoesNotExist:
        error = {
            "error": "An Ontology should be active to explore. Please contact an admin."
        }
    if error is None:
        try:
            # Get the active ontology's ID
            template_id = active_ontology.template.id
            nav_key = active_ontology.id
            # get the navigation from the cache
            if nav_key in navigation_cache:
                navigation = navigation_cache.get(str(nav_key))
            else:
                # create the navigation
                navigation = create_navigation_tree_from_owl_file(
                    active_ontology.content
                )
                navigation_cache.set(
                    nav_key, navigation
                )  # navigation_cache.set(template_id, navigation)

            # Clean previous instance objects
            projects_api.delete_all_projects()
            insitu_data_api.delete_all_data()

            # Get the existing projects from the navigation
            projects = projects_api.get_all_projects_list(navigation, template_id)

            data_table_list = []
            for project in projects:
                # Set builds depending on default active project
                projects_api.toggle_project_selection(project)
                builds_api.delete_all_builds()
                builds_api.set_builds(template_id)
                builds = builds_api.get_all_builds_names_list()

                for build in builds:
                    # Set parts depending on default active build
                    builds_api.toggle_build_selection(build)
                    parts_api.delete_all_parts()
                    parts_api.set_parts(template_id)
                    parts = parts_api.get_all_parts_names_list()

                    for part in parts:
                        insitu_data_operations.load_frames(project, build, part)
                        insitu_data_objects = insitu_data_api.get_data(
                            project, build, part
                        )
                        for insitu_data_object in insitu_data_objects:
                            total_layers = insitu_data_object.layer_numbers[-1]
                            if total_layers > 0:
                                data_name = insitu_data_object.data_name
                                tab_number = insitu_data_object.tab
                                insitu_data_line = [
                                    project,
                                    build,
                                    part,
                                    data_name,
                                    tab_number,
                                    total_layers,
                                ]
                                data_table_list.append(insitu_data_line)

            data_table_csv = utils_parser.get_data_table_csv(data_table_list)
            data_lines = str(int((len(data_table_list) - 1) / 7))

            data = {"data_table_csv": data_table_csv, "data_lines": data_lines}

            logger.info("FINISH load visualization data")
            return HttpResponse(json.dumps(data), content_type="application/json")

        except exceptions.DoesNotExist as e_does_not_exist:
            return HttpResponseBadRequest(
                str(e_does_not_exist), content_type="application/javascript"
            )
        except Exception as e:
            return HttpResponseBadRequest(str(e), content_type="application/javascript")


def get_visualization_data(request):
    """Get the CSV table of all insitu data and calculate the number of parts that have images

    Args:
        request:

    Returns:

    """
    data_table = insitu_data_api.get_all_table()

    data_table_csv = utils_parser.get_data_table_csv(data_table)

    # Calculate the number of parts that have images
    # data_lines are the number of parts that have images
    # If a part has images, it has images for all tabs
    part_list = {}
    for data_l in data_table[1:]:
        build_name = data_l[1]
        if build_name not in part_list.keys():
            part_list[build_name] = [data_l[2]]
        else:
            v = part_list[build_name]
            if data_l[2] not in v:
                v.append(data_l[2])
                part_list[build_name] = v
    data_lines = 0
    for key, values in part_list.items():
        parts = []
        for v in values:
            if v not in parts:
                parts.append(v)
                data_lines = data_lines + 1

    data = {"data_table_csv": data_table_csv, "data_lines": data_lines}

    return HttpResponse(json.dumps(data), content_type="application/json")
