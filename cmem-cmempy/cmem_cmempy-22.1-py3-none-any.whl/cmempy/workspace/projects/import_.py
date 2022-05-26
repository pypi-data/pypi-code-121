"""Import project."""
import json

from cmem.cmempy import config
from cmem.cmempy.api import (
    get_json,
    request,
    send_request,
)


def get_import_uri():
    """Get endpoint URI pattern for project import."""
    path = "/workspace/projects/{}/import/{}"
    return config.get_di_api_endpoint() + path


def import_project_rdf_turtle(project_name, rdf_turtle_string):
    """Import DI Project from RDF Turtle (without resource files)."""
    import_uri = get_import_uri().format(project_name, "rdfTurtle")
    response = send_request(
        import_uri,
        method="POST",
        data=rdf_turtle_string.encode("utf-8")
    )
    return response


def import_project(project_name, file_path, plugin_name="xmlZip"):
    """Import DI Project from an exported file (deprecated)."""
    import_uri = get_import_uri().format(project_name, plugin_name)
    with open(file_path, 'rb') as data:
        response = send_request(
            import_uri,
            method="POST",
            data=data
        )
    return response


def upload_project(file_path):
    """Upload a project file of the project to be imported.

    Project import based on uploaded resources is a multi step procedure.

    This function implements step 1 and 2 of the following process:

    - (1.) the project file upload,
    - (2.) the validation of the uploaded file,
    - (3.) the asynchronous execution of the project import and
    - (4.) the status of the running project import execution.

    Args:
        file_path (str): path to the ZIP or turtle (depends on plugin)

    Returns
        dict of the validation response
    """
    api_base = config.get_di_api_endpoint()

    # 1. the project file upload
    upload_path = "/api/workspace/projectImport"
    upload_uri = api_base + upload_path
    with open(file_path, 'rb') as data:
        project_import_id = json.loads(
            request(upload_uri, method="POST", data=data)
            .content.decode("utf-8")
        )["projectImportId"]

    # 2. the validation of the uploaded file
    validation_path = "/api/workspace/projectImport/" + project_import_id
    validation_uri = api_base + validation_path
    # projectId, label, marshallerId, projectAlreadyExists
    validation_response = json.loads(
        request(validation_uri, method="GET")
        .content.decode("utf-8")
    )
    validation_response["projectImportId"] = project_import_id
    return validation_response


def import_from_upload_start(
        import_id,
        project_id=None,
        generate_id=False,
        overwrite_existing=False
):
    """Import/create a project from an uploaded file.

    Project import based on uploaded resources is a multi step procedure.

    This function implements step 3 of the following process:

    - (1.) the project file upload,
    - (2.) the validation of the uploaded file,
    - (3.) the asynchronous execution of the project import and
    - (4.) the status of the running project import execution.

    Args:
        import_id (str): The projectUploadID received by upload_project()
        project_id (str): If provided, this will adopt the given id for the
            imported project. Cannot be set together with 'generateNewId'.
        generate_id (bool): When enabled this will always generate a new ID
            for this project based on the project label. This is one strategy
            if a project with the original ID already exists.
        overwrite_existing (bool): When enabled this will overwrite an
            existing project with the same ID. Enabling this option will
            NOT override the generateNewId option.

    Returns
        response object of the request
    """
    api_base = config.get_di_api_endpoint()
    endpoint_path = "/api/workspace/projectImport/" + import_id
    endpoint_uri = api_base + endpoint_path
    params = {
        "overwriteExisting": "true" if overwrite_existing else "false",
        "generateNewId": "true" if generate_id else "false",
    }
    if project_id is not None:
        params["newProjectId"] = project_id
    # 3. the asynchronous execution of the project import
    response = request(endpoint_uri, method="POST", params=params)
    return response


def import_from_upload_status(import_id):
    """Get the status of the import project activity.

    Project import based on uploaded resources is a multi step procedure.

    This function implements step 4 of the following process:

    - (1.) the project file upload,
    - (2.) the validation of the uploaded file,
    - (3.) the asynchronous execution of the project import and
    - (4.) the status of the running project import execution.

    Args:
        import_id (str): The projectUploadID received by upload_project()

    Returns
        status object
    """
    api_base = config.get_di_api_endpoint()
    path = "/api/workspace/projectImport/{}/status".format(import_id)
    endpoint = api_base + path
    # 4. the status of the running project import execution.
    return get_json(endpoint, params={"timeout": "1000"})
