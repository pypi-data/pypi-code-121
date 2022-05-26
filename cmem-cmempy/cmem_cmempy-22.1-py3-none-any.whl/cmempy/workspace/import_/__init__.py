"""Import workspace."""
import os

from cmem.cmempy import config
from cmem.cmempy.api import send_request


def get_import_uri():
    """Get endpoint URI pattern for workspace import."""
    return config.get_di_api_endpoint() + "/workspace/import/{}"


def import_xml_zip(xml_zip_file_path):
    """Import DI Workspace from XML ZIP."""
    with open(xml_zip_file_path, 'rb') as file_handle:
        xml_zip_file = {
            'file': (
                os.path.basename(xml_zip_file_path),
                file_handle
            )
        }
        import_uri = get_import_uri().format("xmlZip")
        response = send_request(
            import_uri,
            method="POST",
            files=xml_zip_file
        )
        return response


# https://jira.brox.de/browse/CMEM-2144
def import_rdf_turtle(rdf_turtle_zip_file_path):
    """Import DI Workspace from RDF Turtle (without resource files)."""
    with open(rdf_turtle_zip_file_path, 'rb') as file_handle:
        rdf_turtle_zip_file = {
            'file': (
                os.path.basename(rdf_turtle_zip_file_path),
                file_handle
            )
        }
        import_uri = get_import_uri().format("rdfTurtle")
        response = send_request(
            import_uri,
            method="POST",
            files=rdf_turtle_zip_file
        )
        return response


def import_workspace(file_path, plugin_name="xmlZip"):
    """Import DI Workspace with a specific marshalling plugin."""
    with open(file_path, 'rb') as file_handle:
        file = {
            'file': (
                os.path.basename(file_path),
                file_handle
            )
        }
        import_uri = get_import_uri().format(plugin_name)
        response = send_request(
            import_uri,
            method="POST",
            files=file
        )
        return response
