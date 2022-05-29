import requests
import mimetypes
from os import getenv
from quickbeutils.helpers import verify_config

SLACK_UPLOAD_URL = 'https://slack.com/api/files.upload'
SLACK_POST_MESSAGE_URL = 'https://slack.com/api/chat.postMessage'
SLACK_BOT_TOKEN_KEY = 'SLACK_BOT_TOKEN'


def send_message(recipient_id: str, text: str):
    """
    https://api.slack.com/methods/chat.postMessage
    :param recipient_id:
    :param text:
    :return:
    """

    verify_config(
        conf={
            'SLACK_BOT_TOKEN': getenv(SLACK_BOT_TOKEN_KEY)
        }
    )

    payload = {
        'channel': recipient_id,
        'text': text,
        'as_user': 'true'
    }

    headers = {
        'Authorization': getenv(SLACK_BOT_TOKEN_KEY),
        'Content-Type': 'application/json'
    }

    _check_for_errors(requests.request("POST", SLACK_POST_MESSAGE_URL, headers=headers, json=payload))


def upload_file(recipient_id: str, file_path: str, file_name: str = '', comment: str = ''):
    """
    https://api.slack.com/methods/files.upload
    :param recipient_id:
    :param file_path:
    :param file_name:
    :param comment:
    :return:
    """

    verify_config(
        conf={
            'SLACK_BOT_TOKEN': getenv(SLACK_BOT_TOKEN_KEY)
        }
    )

    if file_name in ['', None]:
        file_name = file_path.split('/')[-1]

    mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'

    payload = {}
    files = [
        (
            'file',
            (file_name, open(file_path, 'rb'), mime_type)
        )
    ]
    headers = {
        'Authorization': getenv(SLACK_BOT_TOKEN_KEY)
    }

    url = f"{SLACK_UPLOAD_URL}?channels={recipient_id}&initial_comment={comment}&filename={file_name}"

    _check_for_errors(requests.request("POST", url, headers=headers, data=payload, files=files))


def _check_for_errors(response: requests.Response):
    try:
        assert response.status_code == 200 and response.json().get('ok', False)
    except AssertionError:
        raise ValueError(f'Slack error: {response.text}')
