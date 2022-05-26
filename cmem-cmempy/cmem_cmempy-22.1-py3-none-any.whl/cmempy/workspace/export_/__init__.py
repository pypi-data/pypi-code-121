"""Export workspace."""
from cmem.cmempy import config
from cmem.cmempy.api import send_request


def get_export_uri():
    """Get endpoint URI pattern for workspace export."""
    return config.get_di_api_endpoint() + "/workspace/export/{}"


def export_xml_zip():
    """Export DI Workspace to XML ZIP."""
    return export("xmlZip")


def export_rdf_turtle():
    """Export DI Workspace as RDF Turtle.

    This does not export the resources.
    """
    return export("rdfTurtle")


def export(plugin_name="xmlZip"):
    """Export DI workspace with a specific marshalling plugin.

    Default plugin is xmlZip.
    """
    export_uri = get_export_uri().format(plugin_name)
    export_data = send_request(export_uri)
    return export_data
