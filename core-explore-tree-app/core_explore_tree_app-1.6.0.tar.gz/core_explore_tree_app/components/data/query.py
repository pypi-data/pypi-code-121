import json

from core_main_app.system import api as system_api
from core_explore_tree_app.utils.xml.projection import get_projection
from core_main_app.commons.exceptions import ApiError


def _is_advanced_filter(str_filter):
    """Helper able to determine if a filter is advanced or not

    Args:
         str_filter:

    Return:
    """
    try:
        json_filter = json.loads(str_filter)
        expected_keys = {"documents", "query"}

        return len(expected_keys.difference(list(json_filter.keys()))) == 0
    except ValueError:  # Only error that json.loads can raise
        return False


def execute_query(template_id, filters=None, projection=None):
    """Execute a query given a template, filters and the projection

    Args:
        template_id:
        filters:
        projection:

    Return:
    """
    # Set default value for filters
    if filters is None:
        filters = list()

    # Will be returned at the end
    data_list_result = []

    # Get all data from the given template
    data_id_list = {
        data.id for data in system_api.get_all_by_list_template([template_id])
    }

    # Parsing filters if present
    for _filter in filters:
        # Extracted correct documents
        filter_result = []

        try:
            # Loads filter and projection
            json_filter = json.loads(_filter)
            json_projection = json.loads(projection)
        except Exception as e:
            raise ApiError("Query parsing failed (%s)" % str(e))

        if _is_advanced_filter(_filter):
            # Get matching document
            #   list possible values of the right hand side
            #   match resulted documents
            documents_field = list(json_filter["documents"].values())[0]

            values = get_filter_values(documents_field)
            matching_documents = get_matching_document(
                template_id,
                list(json_filter["documents"].keys())[0],
                values,
                json_filter["query"],
            )

            for doc in matching_documents:
                doc_cross_query = {
                    list(json_filter["documents"].values())[0]: get_projection(doc)
                }
                filter_result += system_api.execute_query_with_projection(
                    doc_cross_query, list(json_projection.keys())[0]
                )
        else:
            filter_result = system_api.execute_query_with_projection(
                json_filter, list(json_projection.keys())[0]
            )

        filter_id = {document.id for document in filter_result}
        data_id_list = data_id_list.intersection(filter_id)

        data_list_result = [doc for doc in filter_result if doc.id in data_id_list]

    return data_list_result


def get_filter_values(field):
    """Get matching values for a given field

    Args:
        field:
    Return:
    """
    query = {field: {"$exists": True}}
    documents = system_api.execute_query_with_projection(query, field)
    return {get_projection(doc) for doc in documents}


def get_matching_document(template_id, field, values, query):
    """Get matching document

    Args:
        template_id:
        field:
        values:
        query:

    Return:
    """
    document_set = []
    document_projection = {field: 1}

    for value in values:
        tmp_query = [json.dumps(query), json.dumps({field: value})]

        document_set += execute_query(
            template_id, tmp_query, json.dumps(document_projection)
        )

    return document_set
