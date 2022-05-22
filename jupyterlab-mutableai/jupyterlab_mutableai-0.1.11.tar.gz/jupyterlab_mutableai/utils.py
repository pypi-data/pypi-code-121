import requests


def update_analytics(url, api_key, action):
    data = {
        "action": action
    }

    requests.post(
        url=url,
        json=data,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
        },
    )
