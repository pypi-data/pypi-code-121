""" Datacached  API
"""
from core_cache_manager_app.components.data_cached.models import DataCached


def update_cached_docs_list(data_cached, key_doc_id, dataobject):
    """Save or Updates the DataCached object.

    Args:
        DataCached object

    Returns:

    """
    # update cached_documents
    if key_doc_id not in data_cached.cached_documents_dict:
        data_cached.cached_documents_dict.append(key_doc_id)
        data_cached.cached_documents_objects.append(dataobject)

        upsert(data_cached)


def upsert(data_cached):
    """Save or Updates the id the DataCached object.

    Args:
        DataCached object

    Returns:

    """
    return data_cached.save_object()


def upsert_data_cache_object(node_name, doc, key_doc_id):
    """Create or Updates the cached files of the DataCached object.

    Args:
        node_name: represents the name of the Node
        doc: Data to cache under the current Node
        key_doc_id: dict of key (for cache) and associated docid that will be used to retrieve the data from the cache

    Returns:

    """
    doc_in_cache = False
    all_data_cached = DataCached.get_all()
    for datacached in all_data_cached:
        if datacached.current_node == node_name:
            # Node already exist
            update_cached_docs_list(datacached, key_doc_id, doc)
            upsert(datacached)
            doc_in_cache = True
            break
    if doc_in_cache == False:
        # Node does not exist => create a list that will contains cached files for this node
        data = DataCached(
            cached_documents_dict=[key_doc_id],
            current_node=node_name,
            cached_documents_objects=[doc],
        )
        upsert(data)


def clean_datacached_objects():
    """Remove all DataCached objects from the database.

    Returns:

    """
    return DataCached.delete_objects()
