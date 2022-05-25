import re
import six
import requests
from lusid_drive.utilities.lusid_drive_retry import lusid_drive_retry


@lusid_drive_retry
def stream_file_upload(api_factory, x_lusid_drive_filename, x_lusid_drive_path, content_length, body):
    headers = {
        "Accept": "application/json, text/plain, text/json",
        "Content-type": "application/octet-stream",
        "X-LUSID-SDK-Language": "Python",
        # extracts a version from generated header
        "X-LUSID-SDK-Version": api_factory.api_client.default_headers.get("User-Agent")[18:-7],
        "X-LUSID-Application": api_factory.api_client.default_headers.get("X-LUSID-Application"),
        "Authorization": "Bearer " + api_factory.api_client.configuration.access_token,
        "x-lusid-drive-filename": x_lusid_drive_filename,
        "x-lusid-drive-path": x_lusid_drive_path,
        "Content-Length": str(content_length),
        "User-Agent": api_factory.api_client.default_headers.get("User-Agent")
    }

    response_types_map = {
        201: "StorageObject",
        400: "LusidValidationProblemDetails",
    }

    req_url = f"{api_factory.api_client.configuration.host}/api/files"

    response = requests.post(req_url, data=body, headers=headers)

    response_type = response_types_map.get(response.status_code, None)

    if six.PY3:
        match = None
        content_type = response.headers['content-type']
        if content_type is not None:
            match = re.search(r"charset=([a-zA-Z\-\d]+)[\s\;]?", content_type)
        encoding = match.group(1) if match else "utf-8"
        response.data = response.content.decode(encoding)

    # deserialize response data
    if response_type:
        return_data = api_factory.api_client.deserialize(response, response_type)
    else:
        return_data = None

    return return_data
