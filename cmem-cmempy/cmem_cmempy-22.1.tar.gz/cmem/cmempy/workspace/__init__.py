"""Workspace API."""
from cmem.cmempy import config
from cmem.cmempy.api import (
    get_json,
    send_request
)


def get_reload_uri():
    """Get URL for workspace reload."""
    return config.get_di_api_endpoint() + "/workspace/reload"


def get_reload_prefixes_uri():
    """Get URL for prefix reload."""
    return config.get_di_api_endpoint() + "/workspace/reloadPrefixes"


def get_update_global_vocabulary_cache_uri():
    """Get URL for prefix reload."""
    di_base = config.get_di_api_endpoint()
    return di_base + "/workspace/updateGlobalVocabularyCache"


def reload_workspace():
    """Reload the workspace from the backend."""
    return send_request(
        get_reload_uri(),
        method="POST"
    )


def get_task_plugins():
    """
    Get a list of plugins that can be created as workspace tasks.

    A list of plugins that can be created as workspace tasks, e.g. datasets,
    transform tasks etc. The result of this endpoint only contains meta data
    of the plugin, i.e. title, description and categories.
    To fetch the schema details of a specific plugin use the /plugin endpoint.
    """
    return get_json(
        config.get_di_api_endpoint() + "/api/core/taskPlugins",
        method="GET"
    )


def get_task_plugin_description(plugin_id):
    """Get The plugin description of a specific plugin."""
    path = "/api/core/plugins/{}".format(plugin_id)
    return get_json(
        config.get_di_api_endpoint() + path,
        method="GET"
    )


def reload_prefixes():
    """Reload the workspace from the backend."""
    return send_request(
        get_reload_prefixes_uri(),
        method="POST"
    )


def update_global_vocabulary_cache(iri):
    """Update the global vocabulary cache."""
    data = '{"iri":"' + iri + '"}'
    headers = {"Content-Type": "text/json"}
    return send_request(
        get_update_global_vocabulary_cache_uri(),
        method="POST",
        data=data,
        headers=headers
    )
