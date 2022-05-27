""" Query Ontology  API
"""
from core_explore_tree_app.commons.enums import QueryOntologyStatus
from core_explore_tree_app.components.query_ontology.models import QueryOntology


def upsert(query_ontology):
    """Save or Updates the Query Ontology.

    Args:
        query_ontology:

    Returns:

    """
    return query_ontology.save_object()


def delete(ontology):
    """Delete an Ontology

    Args:
        ontology:

    """
    ontology.delete()


def get_by_id(query_ontology_id):
    """Return QueryOntology object with the given id.

    Args:
        query_ontology_id:

    Returns: QueryOntology object

    """
    return QueryOntology.get_by_id(query_ontology_id)


def get_by_status(status):
    """Return QueryOntology object list with the given status.

    Args:
        status:

    Returns: QueryOntology object

    """
    return QueryOntology.get_by_status(status)


def get_active():
    """Return the only active ontology

    Returns:

    """
    return QueryOntology.get_active()


def get_all():
    """Get all the QueryOntology.

    Returns: QueryOntology collection

    """
    return QueryOntology.get_all()


def edit_status(ontology, status):
    """Edit status of a given ontology with a given status

    Args:
        ontology:
        status:

    Returns:

    """
    # If we activate an ontology, we deactivate all the other ones
    if status == QueryOntologyStatus.active.value:
        active_ontology_list = get_by_status(status=QueryOntologyStatus.active.value)
        # deactivate all active ontology (count should be 1)
        for active_ontology in active_ontology_list:
            _set_status(active_ontology, QueryOntologyStatus.uploaded.value)
    # set the new status
    return _set_status(ontology, status)


def _set_status(ontology, status):
    """set the new status to an ontology and save it in DB

    Args:
        ontology:
        status:

    Returns:

    """
    ontology.status = status
    return upsert(ontology)
