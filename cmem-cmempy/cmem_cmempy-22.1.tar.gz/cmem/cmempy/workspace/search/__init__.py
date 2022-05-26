"""API for searching items in the data integration workspace."""

import json

from cmem.cmempy import config
from cmem.cmempy.api import send_request


def get_search_items_uri():
    """Get endpoint URL for the search items API."""
    path = "/api/workspace/searchItems"
    return config.get_di_api_endpoint() + path


# pylint: disable-msg=too-many-arguments
def list_items(
        limit=1000000,
        offset=0,
        project=None,
        text_query="",
        item_type="",
        facets=None,
        add_task_parameter=True
):
    """GET retrieve custom task for the project."""
    data = json.dumps({
        "limit": limit,
        "offset": offset,
        "itemType": item_type,
        "project": project,
        "textQuery": text_query,
        "facets": facets,
        "addTaskParameters": add_task_parameter
    })
    response = send_request(
        get_search_items_uri(),
        method="POST",
        headers={'Content-Type': 'application/json'},
        data=data
    )
    return json.loads(response.decode("utf-8"))
