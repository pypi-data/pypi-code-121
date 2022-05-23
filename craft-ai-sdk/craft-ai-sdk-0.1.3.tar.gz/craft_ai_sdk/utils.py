import xml.etree.ElementTree as ET

from json import JSONDecodeError

from .exceptions import SdkException
from requests import RequestException, Response


def handle_data_store_response(response):
    """Return the content of a response received from the datastore
    or parse the send error and raise it

    Args:
        response (requests.Response): a response from the data store

    Raises:
        SdkException: when the response contains an error

    Returns:
        str: content of the response
    """
    if 200 <= response.status_code < 300:
        return response.text

    # Parse XML error returned by the data store before raising it
    xml_error_node = ET.fromstring(response.text)
    error_infos = {node.tag: node.text for node in xml_error_node}
    error_code = error_infos.pop("Code")
    error_message = error_infos.pop("Message")
    raise SdkException(
        message=error_message,
        status_code=response.status_code,
        name=error_code,
        additional_data=error_infos,
    )


def _parse_json_response(response):
    if response.status_code == 204 or response.text == "OK":
        return
    try:
        response_json = response.json()
    except JSONDecodeError as error:
        raise SdkException(
            f"Unable to decode response data into json. Data being:\n'{response.text}'"
        ) from error
    return response_json


def _raise_craft_ai_error_from_response(response: Response):
    error_content = response.json()
    raise SdkException(
        message=error_content["message"],
        status_code=response.status_code,
        name=error_content.get("name"),
        stack_message=error_content.get("stackMessage"),
        request_id=error_content.get("requestId"),
        additional_data=error_content.get("additionalData"),
    )


def handle_http_request(request_func):
    def wrapper(*args, **kwargs):
        try:
            response = request_func(*args, **kwargs)
        except RequestException as error:
            raise SdkException(
                "Unable to perform the request", name="RequestError"
            ) from error

        if 200 <= response.status_code < 300:
            return _parse_json_response(response)
        _raise_craft_ai_error_from_response(response)

    return wrapper
