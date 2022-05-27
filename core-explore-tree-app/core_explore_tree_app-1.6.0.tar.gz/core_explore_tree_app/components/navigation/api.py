""" Navigation  API
"""
from core_explore_tree_app.components.navigation.models import Navigation
from core_explore_tree_app.parser.parser import parse_ontology

from core_cache_manager_app.components.data_cached import api as data_cached_api
from core_explore_tree_app.components.leaf import api as leaf_api


def get_by_id(navigation_id):
    """Return Navigation object with the given id.

    Args:
        navigation_id:

    Returns: Navigation object

    """
    return Navigation.get_by_id(navigation_id)


def get_by_name(navigation_name):
    """Return Navigation object with the given name.

    Args:
        navigation_name:

    Returns: Navigation object

    """
    return Navigation.get_by_name(navigation_name)


def upsert(navigation):
    """Save or Updates the Navigation object.

    Args:
        Navigation object

    Returns:

    """
    return navigation.save_object()


def create_navigation_tree_from_owl_file(owl_content):
    """Create Navigation associated to the ontology

    Args:
        String object

    Returns: Navigation object

    """
    clean_navigation_objects()
    data_cached_api.clean_datacached_objects()
    leaf_api.clean_leaves_objects()
    parsed_ontology = parse_ontology(owl_content)
    return _create_navigation(parsed_ontology)


def _create_navigation(tree):
    """Create navigation from the root element

    Args:
        tree
    Returns:
        Navigation object
    """
    # create navigation
    navigation = Navigation()
    upsert(navigation)
    # generate children
    children = _create_navigation_branches(tree, str(navigation.id))

    # update children
    navigation.children = children
    upsert(navigation)

    return navigation


def _create_navigation_branches(tree, parent):
    """Create navigation branches

    Args:
        tree, parent
    Returns:
        list
    """
    children_ids = []

    for name, values in tree.items():
        # create navigation
        navigation = Navigation(name=name, parent=parent)
        upsert(navigation)

        # generate children
        children = _create_navigation_branches(values["children"], str(navigation.id))

        # update navigation
        navigation.options = values["annotations"]
        navigation.children = children
        upsert(navigation)

        # add the navigation to the list
        children_ids.append(str(navigation.id))

    return children_ids


def clean_navigation_objects():
    """Delete all Navigation objects from the Database

    Args:

    Returns:

    """
    return Navigation.delete_objects()
