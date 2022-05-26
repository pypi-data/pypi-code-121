"""API for retrieving marshalling plugins."""
import json

from cmem.cmempy import config
from cmem.cmempy.api import send_request

KNOWN_PLUGINS = {
    "xmlZip": "zip",
    "rdfTurtle": "ttl"
}


def get_marshalling_plugins_uri():
    """Get endpoint URI for the marshalling plugins list."""
    path = "/workspace/marshallingPlugins"
    return config.get_di_api_endpoint() + path


def get_marshalling_plugins():
    """GET retrieve marshalling plugins."""
    return json.loads(send_request(
        get_marshalling_plugins_uri(),
        method="GET"
    ).decode("utf-8"))


def get_marshalling_plugins_as_dict():
    """Retrieve marshalling plugins as extended dictionary."""
    plugins = {}
    for plugin in get_marshalling_plugins():
        plugins[plugin["id"]] = plugin
        if plugin["id"] in KNOWN_PLUGINS.keys()\
                and "fileExtension" not in plugin.keys():
            plugin["fileExtension"] = KNOWN_PLUGINS[plugin["id"]]
    return plugins


def get_extension_by_plugin(plugin_id):
    """Return a filename extension string of a marshalling plugin."""
    plugins = get_marshalling_plugins_as_dict()
    if plugin_id in plugins.keys():
        if "fileExtension" in plugins[plugin_id].keys():
            return plugins[plugin_id]["fileExtension"]
        if plugin_id in KNOWN_PLUGINS.keys():
            return KNOWN_PLUGINS[plugin_id]
        raise ValueError("Could not get file extension for plugin "
                         + plugin_id)
    raise ValueError(plugin_id + " is not a valid marshalling plugin. "
                     + "Try one of " + str(KNOWN_PLUGINS.keys()))


def get_plugin_by_extension(extension):
    """Return a marshalling plugin for a given file extension."""
    for plugin_id, plugin in get_marshalling_plugins_as_dict().items():
        # return the first match of the extension
        if plugin["fileExtension"] == extension:
            return plugin_id
    raise ValueError("Could not get marshalling plugin for file extension "
                     + extension)
