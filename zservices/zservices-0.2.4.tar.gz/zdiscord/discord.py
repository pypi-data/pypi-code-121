import requests
from zdiscord import logger


def send_notification(url, user_name, payload):
    response = None
    url = url
    headers = {'Content-Type': 'application/json'}

    data = {
        "content": payload, "username": user_name
    }

    try:
        response = requests.post(url=url, json=data, headers=headers)
    except Exception as e:
        logger.warning(f'[DISCORD] Unable to send notification, error={e}')

    return response
