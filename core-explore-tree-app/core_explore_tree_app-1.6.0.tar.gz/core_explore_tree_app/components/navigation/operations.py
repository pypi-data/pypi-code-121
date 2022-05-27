""" Operations on navigation objects
"""
from core_explore_tree_app.components.data import query
from core_explore_tree_app.components.navigation import api as navigation_api
from core_explore_tree_app.utils.xml.projection import get_projection
from core_main_app.components.data.models import Data

CQL_NAMESPACE = "http://siam.nist.gov/Database-Navigation-Ontology#"


def retrieve_navigation_filters(navigation_node):
    """retrieve filters from a navigation node

    Parameters
        navigation_node:

    Returns:
    """
    filters = []
    node_has_parent = True

    # If no parent, stops the filter lookup
    while node_has_parent:
        # Add filter to the list of filters
        if (
            "filter" in navigation_node.options
            and navigation_node.options["filter"] is not None
        ):
            filters.append(navigation_node.options["filter"])

        # Update parameters
        node_has_parent = navigation_node.parent is not None

        if node_has_parent:
            navigation_node = navigation_api.get_by_id(navigation_node.parent)

    return filters


def get_navigation_node_by_name(root_id, node_name):
    """Get the navigation node from a given node name

    Args:
        root_id:
        node_name:

    Returns:

    """
    navigation_root_node = navigation_api.get_by_id(root_id)
    owl_node_name = CQL_NAMESPACE + node_name
    navigation_nodes = navigation_api.get_by_name(owl_node_name)

    if navigation_root_node in navigation_nodes:
        return navigation_root_node

    if len(navigation_root_node.children) == 0:
        return None

    children_nodes = [
        get_navigation_node_by_name(child, node_name)
        for child in navigation_root_node.children
    ]
    children_nodes = [
        child_node for child_node in children_nodes if child_node is not None
    ]

    if len(children_nodes) != 1:
        return None
    else:
        return children_nodes[0]


def get_navigation_node_for_document(node_id, document_id):
    """Get the navigation node from a given data id

    Args:
        node_id:
        document_id:

    Returns:

    """
    navigation_node = navigation_api.get_by_id(node_id)
    original_node = navigation_api.get_by_id(node_id)

    if (
        "projection" in navigation_node.options
        and navigation_node.options["projection"] is not None
    ):
        # **************
        # FIXME duplicate of parser code
        # Get projection

        filters = []
        while True:
            # add filter to the list of filters
            if (
                "filter" in navigation_node.options
                and navigation_node.options["filter"] is not None
            ):
                filters.append(navigation_node.options["filter"])

            # if no parent, stops the filter lookup
            if navigation_node.parent is None:
                break
            else:  # if parent, continue the filter lookup at the parent level
                navigation_node = navigation_api.get_by_id(navigation_node.parent)

        # get the documents matching the query
        doc = Data.get_by_id(document_id)
        template_id = doc.template.id

        documents_id = [
            str(get_projection(document))
            for document in query.execute_query(template_id, filters, '{"id": 1}')
        ]
        #  End fixme
        # **************

        # If the document is one of the document we return the navigation node, else return None
        if document_id in documents_id:
            return original_node
        else:
            return None
    else:
        navigation_children = navigation_node.children

        if len(navigation_children) == 0:
            return None
        else:
            navigation_nodes = [
                get_navigation_node_for_document(child_id, document_id)
                for child_id in navigation_children
            ]
            navigation_nodes = [
                nav_node for nav_node in navigation_nodes if nav_node is not None
            ]

            if len(navigation_nodes) != 1:
                return None
            else:
                return navigation_nodes[0]
