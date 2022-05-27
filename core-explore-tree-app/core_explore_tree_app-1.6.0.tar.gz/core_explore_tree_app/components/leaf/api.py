""" Leaf  API
"""
from core_explore_tree_app.components.leaf.models import Leaf


def update_docs_list(leaf, doc_id):
    """Save or Updates the list of docs under the leaf.

    Args:
        Leaf object

    Returns:

    """
    # update docs_list
    leaf.docs_list.append(doc_id)
    upsert(leaf)


def upsert(leaf):
    """Save or Updates the Leaf object.

    Args:
        Leaf object

    Returns:

    """
    return leaf.save_object()


def upsert_leaf_object(node_id, doc_id):
    """Create or Updates the Leaf object.

    Args:
        node_id: represents the id of the Leaf node
        doc_id: id of document under the current leaf in the tree

    Returns:

    """
    try:
        leaf = get_by_current_node_id(node_id)
        # if leaf already exists in the DB => add to the list of the docs under this leaf id of the current doc
        update_docs_list(leaf, doc_id)
        upsert(leaf)
    except:
        # Leaf does not exists => create a list that will contains the id of docs for this node
        leaf = Leaf(current_node_id=node_id, docs_list=[doc_id])
        upsert(leaf)


def get_by_current_node_id(leaf_id):
    """Return the object with the given id
    Args:
     leaf_id:
    Return:
        Leaf(obj): Leaf object
    """
    return Leaf.get_by_current_node_id(leaf_id)


def clean_leaves_objects():
    """Remove all Leaf objects from the database.

    Returns:

    """
    return Leaf.delete_objects()
