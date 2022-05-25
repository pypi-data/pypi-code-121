import base64
import json
import re
import requests
from requests.structures import CaseInsensitiveDict
from typing import Union

from ssb_altinn3_util.models.basic_file import BasicFile


def get_instance(
    token: str, instance_owner_id: int, instance_guid: str, platform_base_url: str
) -> str:
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{platform_base_url}storage/api/v1/instances/{instance_owner_id}/{instance_guid}"
    response = requests.get(url, headers=headers)

    content = response.content.decode("UTF-8")

    return json.dumps(json.loads(content))


def get_data_for_instance(
    token: str,
    instance_owner_id: int,
    instance_guid: str,
    data_guid: str,
    platform_base_url: str,
) -> BasicFile:
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{platform_base_url}storage/api/v1/instances/{instance_owner_id}/{instance_guid}/data/{data_guid}"
    response = requests.get(url, headers=headers)

    b64_content = str(base64.b64encode(response.content), "utf-8")

    filename = _get_filename_from_headers(response.headers)

    content_type = response.headers["Content-Type"]

    file = BasicFile(
        filename=filename, content_type=content_type, base64_content=b64_content
    )
    return file


def _get_filename_from_headers(headers: CaseInsensitiveDict) -> Union[str, None]:
    if "Content-Disposition" not in headers:
        return None

    content_disposition = headers["Content-Disposition"]

    matches = re.findall("filename=(.+?);", content_disposition)

    if not matches:
        return None

    filename: str = matches[0]

    if filename[0] == '"':
        filename = filename[1:-1]

    return filename
