"""Export project."""
from cmem.cmempy import config
from cmem.cmempy.api import send_request


def get_export_uri():
    """Get endpoint URI pattern for project export."""
    path = "/workspace/projects/{}/export/{}"
    return config.get_di_api_endpoint() + path


def export_project_rdf_turtle(project_name):
    """Export DI Project as RDF Turtle.

    This does not export the resources.
    """
    return export_project(project_name, "rdfTurtle")


def export_project(project_name, plugin_name="xmlZip"):
    """Export DI Project with a specific marshalling plugin.

    Default plugin is xmlZip.
    """
    export_uri = get_export_uri().format(project_name, plugin_name)
    export_data = send_request(export_uri)
    return export_data
