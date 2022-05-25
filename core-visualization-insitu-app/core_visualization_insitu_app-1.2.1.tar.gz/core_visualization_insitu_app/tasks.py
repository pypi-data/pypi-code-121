""" Admin Tasks visualization
"""
import logging
from celery import shared_task
from django.core.cache import caches

from core_main_app.commons import exceptions
from core_explore_tree_app.components.navigation.api import (
    create_navigation_tree_from_owl_file,
)
from core_visualization_insitu_app.components.projects import api as projects_api
from core_visualization_insitu_app.components.builds import api as builds_api
from core_visualization_insitu_app.components.parts import api as parts_api
from core_visualization_insitu_app.components.insitu_data import api as insitu_data_api
from core_visualization_insitu_app.components.insitu_data import (
    operations as insitu_data_operations,
)
from core_visualization_insitu_app.utils import parser as utils_parser

import core_explore_tree_app.components.query_ontology.api as query_ontology_api


logger = logging.getLogger(__name__)
navigation_cache = caches["navigation"]


@shared_task
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
                navigation = navigation_cache.get(nav_key)
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

            logger.info("FINISH load visualization data")

        except Exception as e:
            logger.error("ERROR in load visualization data")
    else:
        logger.info("ERROR no active Ontology")


@shared_task
def build_display_data(request):
    """

    Args:
        request:

    Returns:

    """
    build_visualization_data()

    data_table = insitu_data_api.get_all_table()
    data_table_csv = utils_parser.get_data_table_csv(data_table)

    data_lines = str(int((len(data_table) - 1) / 7))
    data = {"data_table_csv": data_table_csv, "data_lines": data_lines}

    return data
