"""Explore tree app user views
"""
import logging

from django.core.cache import caches

import core_explore_tree_app.components.query_ontology.api as query_ontology_api
from core_explore_tree_app.components.navigation.api import (
    create_navigation_tree_from_owl_file,
)
from core_explore_tree_app.parser.renderer import render_navigation_tree
from core_main_app.commons import exceptions
from core_main_app.utils.rendering import render

logger = logging.getLogger(__name__)

navigation_cache = caches["navigation"]
html_tree_cache = caches["html_tree"]


def core_explore_tree_index(request):
    """Page that allows to see the exploration tree.

    Args:
        request:

    Returns:

    """
    context = {}
    error = None

    try:
        # get the active ontology
        active_ontology = query_ontology_api.get_active()
        # get the navigation from the cache
        nav_key = str(active_ontology.id)
        if nav_key in navigation_cache:
            navigation = navigation_cache.get(nav_key)
        else:
            # create the navigation
            navigation = create_navigation_tree_from_owl_file(active_ontology.content)
            navigation_cache.set(nav_key, navigation)

        # get the tree from the cache
        tree_key = str(navigation.id)
        if tree_key in html_tree_cache:
            html_tree = html_tree_cache.get(tree_key)
        else:
            # create the html tree
            html_tree = render_navigation_tree(navigation, active_ontology.template.id)
            html_tree_cache.set(str(tree_key), html_tree)

        context = {"navigation_tree": html_tree, "navigation_id": navigation.id}
    except exceptions.DoesNotExist:
        error = {
            "error": "An Ontology should be active to explore. Please contact an admin."
        }
    except Exception as e:
        error = {
            "error": "An error occurred during the generation of the navigation tree."
        }
        logger.error("ERROR : {0}".format(str(e)))

    if error:
        context.update(error)

    assets = {
        "js": [
            {"path": "core_explore_tree_app/user/js/load_view.js", "is_raw": False},
            {"path": "core_explore_tree_app/user/js/tree.js", "is_raw": True},
            {
                "path": "core_explore_tree_app/user/js/resize_tree_panel.js",
                "is_raw": True,
            },
            {"path": "core_explore_tree_app/user/js/mock.js", "is_raw": True},
        ],
        "css": [
            "core_explore_tree_app/user/css/tree.css",
            "core_explore_tree_app/user/css/loading_background.css",
        ],
    }

    modals = ["core_explore_tree_app/user/navigation/download_options.html"]
    return render(
        request,
        "core_explore_tree_app/user/navigation/explore_tree_wrapper.html",
        assets=assets,
        modals=modals,
        context=context,
    )
